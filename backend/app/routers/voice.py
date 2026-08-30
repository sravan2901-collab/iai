"""
Voice Router for AksharAI Multilingual Literacy Assistant.

Provides REST endpoints for:
1. POST /api/voice/evaluate — Speech-to-Text & Pronunciation Analysis (Sarvam Saaras v3 + Web Speech + SpeechRecognition)
2. GET  /api/voice/audio/{filepath:path} — Stream/Download recorded user audio files from disk
3. GET  /api/voice/tts      — Text-to-Speech audio streaming (gTTS + Sarvam Bulbul v3)
4. GET  /api/voice/status   — Speech engine status & active STT/TTS provider
"""

import os
import time
import uuid
from io import BytesIO
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Response
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
from gtts import gTTS

from app.database import get_db
from app import models
from app.auth import get_optional_current_learner
from app.services.sarvam_service import sarvam_service, detect_script_language
from app.services.phoneme_service import evaluate_pronunciation

router = APIRouter(prefix="/api/voice", tags=["Voice Coach & Speech Analysis"])

# Audio Storage Directory on disk: backend/storage/audio
AUDIO_STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage", "audio"))
os.makedirs(AUDIO_STORAGE_DIR, exist_ok=True)


@router.get("/status")
def get_voice_engine_status():
    """
    Returns the live configuration status of the voice engine,
    including Sarvam AI credentials status, STT engine, and supported languages.
    """
    return sarvam_service.get_service_status()


@router.get("/audio/{filepath:path}")
def get_recorded_audio(filepath: str):
    """
    Retrieves and streams the stored audio recording file from disk.
    Supports paths formatted as {learner_id}/{session_id}.wav or {filename}.
    """
    clean_path = os.path.normpath(filepath).lstrip("\\/").replace("backend/storage/audio/", "").replace("storage/audio/", "")
    file_path = os.path.join(AUDIO_STORAGE_DIR, clean_path)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio recording file not found on server")
    
    media_type = "audio/mpeg" if file_path.endswith(".mp3") else "audio/wav"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=os.path.basename(file_path),
        headers={"Cache-Control": "public, max-age=86400"}
    )


@router.post("/evaluate")
async def evaluate_voice_session(
    lesson_id: int = Form(...),
    learner_id: Optional[int] = Form(None),
    audio_file: Optional[UploadFile] = File(None),
    transcript: Optional[str] = Form(None),
    language_code: Optional[str] = Form(None),
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    """
    Receives user recorded audio file and/or live client speech recognition transcript.
    Saves the physical audio file to disk at backend/storage/audio/{learner_id}/{session_id}.<ext>,
    evaluates pronunciation accuracy using Sarvam Saaras v3 STT in the lesson's native language,
    and attaches scores to the authenticated learner.
    """
    # 1. Resolve real learner ID: Bearer token > Form param > first DB learner fallback
    target_learner_id = None
    if current_learner:
        target_learner_id = current_learner.learner_id
    elif learner_id and learner_id > 0:
        target_learner_id = learner_id
    else:
        first_learner = db.query(models.Learner).first()
        if first_learner:
            target_learner_id = first_learner.learner_id

    # 2. Fetch lesson and infer target text & language code
    # Resolve real language via Lesson -> Module -> Curriculum -> Language.iso_code
    lesson = db.query(models.Lesson).filter(models.Lesson.lesson_id == lesson_id).first()
    
    target_text = "Hello, how are you today?"
    inferred_lang = language_code

    if lesson:
        if lesson.target_text:
            target_text = lesson.target_text
        
        # Determine language from module -> curriculum -> language relationship
        try:
            if not inferred_lang and lesson.module and lesson.module.curriculum and lesson.module.curriculum.language:
                inferred_lang = lesson.module.curriculum.language.iso_code
        except Exception:
            pass

    # If language is still undetermined, detect directly from target_text script characters
    if not inferred_lang or inferred_lang in ("en", ""):
        inferred_lang = detect_script_language(target_text, fallback=inferred_lang or "en")

    # If learner exists and still undetermined, fallback to learner's native language preference
    if (not inferred_lang or inferred_lang == "en") and target_learner_id:
        try:
            learner = db.query(models.Learner).filter(models.Learner.learner_id == target_learner_id).first()
            if learner and learner.current_language:
                inferred_lang = learner.current_language.iso_code or inferred_lang
        except Exception:
            pass

    inferred_lang = inferred_lang or "en"

    # 3. Read audio bytes if file was provided
    audio_bytes = None
    audio_filename = "recording.wav"
    calculated_duration = 3

    if audio_file:
        audio_bytes = await audio_file.read()
        if audio_file.filename:
            audio_filename = audio_file.filename
        if audio_bytes:
            calculated_duration = max(1, round(len(audio_bytes) / 32000))

    # 4. Multi-tier Speech-to-Text Transcription (Sarvam AI Saaras v3 -> Web Speech API -> Python SpeechRecognition)
    # Spanish ('es') is guarded inside sarvam_service to skip Sarvam and use client transcript
    stt_result = await sarvam_service.transcribe_audio(
        audio_bytes=audio_bytes,
        language_code=inferred_lang,
        client_transcript=transcript,
        target_text=target_text,
        audio_filename=audio_filename
    )

    recognized_text = stt_result.get("transcript", "").strip()
    stt_provider = stt_result.get("provider", "none")
    detected_lang = stt_result.get("language_code", inferred_lang)

    # 5. Evaluate Pronunciation & Phoneme Similarity
    eval_result = evaluate_pronunciation(
        target_text=target_text,
        spoken_text=recognized_text,
        language_code=inferred_lang
    )

    # 6. Save Voice Session in DB and persist audio bytes to backend/storage/audio/{learner_id}/{session_id}.<ext>
    voice_session_id = None
    saved_audio_url = ""
    achievements_unlocked = []

    try:
        if target_learner_id:
            learner_exists = db.query(models.Learner).filter(models.Learner.learner_id == target_learner_id).first()
            if learner_exists:
                voice_session = models.VoiceSession(
                    learner_id=target_learner_id,
                    lesson_id=lesson_id,
                    audio_url="",
                    duration_sec=calculated_duration
                )
                db.add(voice_session)
                db.commit()
                db.refresh(voice_session)
                voice_session_id = voice_session.session_id

                # Save physical audio file to backend/storage/audio/{target_learner_id}/{session_id}.<ext>
                if audio_bytes and len(audio_bytes) > 0:
                    ext = "mp3" if audio_filename.lower().endswith(".mp3") else "wav"
                    learner_dir = os.path.join(AUDIO_STORAGE_DIR, str(target_learner_id))
                    os.makedirs(learner_dir, exist_ok=True)
                    stored_name = f"{voice_session_id}.{ext}"
                    abs_file_path = os.path.join(learner_dir, stored_name)
                    with open(abs_file_path, "wb") as fh:
                        fh.write(audio_bytes)
                    
                    saved_audio_url = f"backend/storage/audio/{target_learner_id}/{stored_name}"
                    voice_session.audio_url = saved_audio_url
                    db.commit()

                # Save Pronunciation Score
                score_rec = models.PronunciationScore(
                    session_id=voice_session.session_id,
                    recognized_text=recognized_text,
                    phoneme_accuracy=eval_result["phoneme_accuracy"],
                    syllable_score=eval_result["syllable_score"],
                    word_feedback_json=str(eval_result["word_feedback"]),
                    overall_score=eval_result["overall_score"]
                )
                db.add(score_rec)

                # Update learner points and voice_pct skill score
                profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == target_learner_id).first()
                if profile:
                    profile.total_points = (profile.total_points or 0) + int(eval_result["overall_score"] / 10)
                    new_voice_pct = float(eval_result["overall_score"])
                    if not profile.voice_pct or profile.voice_pct == 0.0:
                        profile.voice_pct = round(new_voice_pct, 1)
                    else:
                        profile.voice_pct = round((profile.voice_pct * 0.7) + (new_voice_pct * 0.3), 1)

                db.commit()

                # Step 3.1: Trigger lesson completion if passing score >= 50.0
                if eval_result["overall_score"] >= 50.0:
                    from app.routers.learning_path import complete_lesson_workflow
                    # Pass award_points=False so complete_lesson_workflow does not double-award points
                    complete_lesson_workflow(target_learner_id, lesson_id, eval_result["overall_score"], db, award_points=False)

                # Gamification: Update streak and check/award achievements
                from app.services.gamification_service import update_streak, check_and_award_achievements
                update_streak(target_learner_id, db)
                achievements_unlocked = check_and_award_achievements(target_learner_id, db, voice_score=eval_result["overall_score"])
    except Exception as db_err:
        print(f"[VOICE ROUTER] Notice during database save: {db_err}")

    return {
        "session_id": voice_session_id,
        "audio_url": saved_audio_url,
        "recognized_text": recognized_text,
        "stt_provider": stt_provider,
        "target_text": target_text,
        "language_code": detected_lang,
        "phoneme_accuracy": eval_result["phoneme_accuracy"],
        "syllable_score": eval_result["syllable_score"],
        "overall_score": eval_result["overall_score"],
        "word_feedback": eval_result["word_feedback"],
        "remediation_tip": eval_result["remediation_tip"],
        "achievements_unlocked": achievements_unlocked
    }


@router.get("/tts")
async def text_to_speech(text: str, lang: str = "te"):
    """
    Generates high-fidelity natural spoken human speech MP3 audio for any target text and language.
    Supports: te (Telugu), hi (Hindi), ta (Tamil), en (English), mr (Marathi), bn (Bengali), kn (Kannada), es (Spanish).
    """
    clean_text = text.strip() or "అ ఆ ఇ ఈ"
    clean_lang = lang.split('-')[0].lower()  # e.g. 'te-IN' -> 'te'
    if clean_lang not in ['te', 'hi', 'ta', 'en', 'mr', 'bn', 'kn', 'es']:
        clean_lang = 'te'

    try:
        mp3_fp = BytesIO()
        tts = gTTS(text=clean_text, lang=clean_lang)
        tts.write_to_fp(mp3_fp)
        mp3_fp.seek(0)

        return StreamingResponse(
            mp3_fp,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": f"inline; filename=tts_{clean_lang}.mp3",
                "Cache-Control": "public, max-age=3600"
            }
        )
    except Exception as e:
        print(f"gTTS generation notice: {e}, attempting Sarvam Bulbul TTS fallback")
        if sarvam_service.is_configured():
            audio_bytes = await sarvam_service.generate_speech(clean_text, clean_lang)
            if audio_bytes:
                return Response(content=audio_bytes, media_type="audio/mpeg")
        
        # Safe fallback: return empty audio response
        return Response(content=b"", media_type="audio/mpeg")
