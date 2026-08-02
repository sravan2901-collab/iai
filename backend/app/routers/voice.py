from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.sarvam_service import sarvam_service
from app.services.phoneme_service import evaluate_pronunciation

router = APIRouter(prefix="/api/voice", tags=["Voice Coach & Speech Analysis"])

@router.post("/evaluate")
async def evaluate_voice_session(
    learner_id: int = Form(...),
    lesson_id: int = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Receives user recorded audio file, calls Sarvam Saaras STT API, 
    and scores pronunciation accuracy using Levenshtein distance.
    """
    audio_bytes = await audio_file.read()

    # 1. Fetch lesson target text
    lesson = db.query(models.Lesson).filter(models.Lesson.lesson_id == lesson_id).first()
    target_text = lesson.target_text if lesson and lesson.target_text else "नमस्ते आप कैसे हैं"

    # 2. Call Sarvam Saaras v3 STT
    transcribed_text = await sarvam_service.transcribe_audio(audio_bytes)

    # 3. Evaluate Pronunciation
    eval_result = evaluate_pronunciation(target_text, transcribed_text)

    # 4. Save Voice Session in DB
    voice_session = models.VoiceSession(
        learner_id=learner_id,
        lesson_id=lesson_id,
        audio_url=f"/storage/audio/{audio_file.filename}",
        duration_sec=5
    )
    db.add(voice_session)
    db.commit()
    db.refresh(voice_session)

    # 5. Save Pronunciation Score in DB
    score_rec = models.PronunciationScore(
        session_id=voice_session.session_id,
        recognized_text=transcribed_text,
        phoneme_accuracy=eval_result["phoneme_accuracy"],
        syllable_score=eval_result["syllable_score"],
        word_feedback_json=str(eval_result["word_feedback"]),
        overall_score=eval_result["overall_score"]
    )
    db.add(score_rec)
    
    # Update learner points
    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner_id).first()
    if profile:
        profile.total_points += int(eval_result["overall_score"] / 10)
    
    db.commit()

    return {
        "session_id": voice_session.session_id,
        "recognized_text": transcribed_text,
        "phoneme_accuracy": eval_result["phoneme_accuracy"],
        "syllable_score": eval_result["syllable_score"],
        "overall_score": eval_result["overall_score"],
        "word_feedback": eval_result["word_feedback"],
        "remediation_tip": eval_result["remediation_tip"]
    }

@router.get("/tts")
async def text_to_speech(text: str, lang_code: str = "hi-IN"):
    """
    Generates Sarvam Bulbul v3 TTS audio stream for lesson targets.
    """
    audio_bytes = await sarvam_service.generate_speech(text, lang_code)
    return {"status": "success", "text": text, "bytes_length": len(audio_bytes)}
