import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("=" * 80)
print("UPDATING TELUGU CURRICULUM: CLEAN ENGLISH MODULE TITLES + 100% PURE TELUGU CONTENT")
print("=" * 80)

telugu_lang = db.query(models.Language).filter(models.Language.iso_code == 'te').first()

if not telugu_lang:
    print("Telugu language not found!")
    sys.exit(1)

telugu_clean_structure = {
    "SPOKEN": {
        "title": "Spoken Curriculum",
        "modules": [
            ("Module 1: Sound Inventory (Vowels & Unique Consonants)", "Sound Inventory: Vowels & Unique Consonant Phonemes", "అ, ఆ, ఇ, ఈ, ఉ, ఊ, ఋ, ఎ, ఏ, ఐ, ఒ, ఓ, ఔ", ["అ", "ఆ", "ఇ", "ఈ"]),
            ("Module 2: Passive Listening Exposure (Rhythm & Intonation)", "Passive Listening: Speech Cadence & Rhythm", "నమస్కారం అండి, మీరు ఎలా ఉన్నారు? ఈ పాఠానికి స్వాగతం.", ["నమస్కారం", "స్వాగతం"]),
            ("Module 3: Core Survival Phrases (Hello, Goodbye, Please, Thank You, Yes, No, Excuse Me, Sorry)", "Core Survival Phrases: Daily Courtesy Words", "నమస్కారం, సెలవు, దయచేసి, ధన్యవాదాలు, అవును, కాదు, క్షమించండి", ["నమస్కారం", "ధన్యవాదాలు"]),
            ("Module 4: Numbers 0 to 10 (Counting Sound Phonemes)", "Numbers 0 to 10 Pronunciation", "సున్నా, ఒకటి, రెండు, మూడు, నాలుగు, ఐదు, ఆరు, ఏడు, ఎనిమిది, తొమ్మిది, పది", ["సున్నా", "ఒకటి", "పది"]),
            ("Module 5: Fixed Self-Intro Chunks (\"My name is...\", \"I am from...\")", "Fixed Self-Intro Chunks: Name & Origin", "నమస్కారం, నా పేరు ఆనంద్. నేను హైదరాబాద్ నుండి వచ్చాను.", ["నా-పేరు", "నేను-వచ్చాను"]),
            ("Module 6: Audio Shadowing Practice (Repeating Short Audio Clips)", "Audio Shadowing Practice: Ear & Mouth Coordination", "నా వెంట స్పష్టంగా చెప్పండి: నేను శ్రద్ధగా భాష నేర్చుకుంటున్నాను.", ["స్పష్టంగా", "నేర్చుకుంటున్నాను"])
        ]
    },
    "WRITTEN": {
        "title": "Written Curriculum",
        "modules": [
            ("Module 1: Script Strokes & Letter Shapes", "Script Strokes: Basic Alphabet Formation", "అ, ఆ, ఇ, ఈ, ఉ — ప్రాథమిక అక్షర లేఖనం", ["అ", "ఆ", "ఇ", "ఈ"]),
            ("Module 2: Vowel Marks & Accent Symbols", "Vowel Marks & Accent Spelling", "తలకట్టు, దీర్ఘం, గుడి, గుడిదీర్ఘం — గుణింత గుర్తులు", ["తలకట్టు", "దీర్ఘం"]),
            ("Module 3: 2-Letter Syllable Combinations", "2-Letter Syllable Word Writing", "అమ, అని, ఇది, అది, ఇటు, అటు — పదాల రాత సాధన", ["అమ", "అని", "ఇది"]),
            ("Module 4: Writing Numbers 0 to 10", "Writing Number Digits 0 to 10", "౦, ౧, ౨, ౩, ౪, ౫, ౬, ౭, ౮, ౯, ౧౦ — సంఖ్యలు", ["సున్నా", "పది"]),
            ("Module 5: Writing Survival Courtesy Words", "Writing Core Survival Words", "నమస్కారం, ధన్యవాదాలు, అవును, కాదు — రాయడం", ["నమస్కారం", "ధన్యవాదాలు"]),
            ("Module 6: Writing Fixed Self-Intro Sentence", "Writing Self-Intro Sentence", "నా పేరు ఆనంద్. నేను హైదరాబాద్ నుండి వచ్చాను.", ["నా-పేరు", "వచ్చాను"])
        ]
    },
    "READING": {
        "title": "Reading Curriculum",
        "modules": [
            ("Module 1: Visual Alphabet & Symbol Recognition", "Visual Alphabet & Symbol Recognition", "అ, ఆ, ఇ, ఈ, ఉ, ఊ — అక్షరాల గుర్తింపు", ["అ", "ఆ", "ఇ", "ఈ"]),
            ("Module 2: Vowel Sound Sight Reading", "Vowel Sound & Syllable Sight Reading", "క, కా, కి, కీ, కు, కూ — గుణింత పఠనం", ["క", "కా", "కి"]),
            ("Module 3: 2-Letter Sight Word Reading", "2-Letter Sight Word Reading", "అల, ఇల, ఈల, ఉల, ఎల, ఒల — ద్వియక్షర పదాలు", ["అల", "ఇల", "ఈల"]),
            ("Module 4: Reading Numbers 0 to 10", "Visual Digit & Number Reading 0 to 10", "సున్నా, ఒకటి, రెండు, మూడు, నాలుగు, ఐదు, ఆరు, ఏడు, ఎనిమిది, తొమ్మిది, పది", ["సున్నా", "ఒకటి", "పది"]),
            ("Module 5: Reading Survival Signs & Labels", "Everyday Survival Sign & Label Reading", "తెరిచి ఉంది, మూసివేసి ఉంది, నిష్క్రమణ, ఆగుము", ["తెరిచి-ఉంది", "నిష్క్రమణ"]),
            ("Module 6: Reading Fixed Greetings & Intro Chunks", "Reading Fixed Greetings & Intro Chunks", "నమస్కారం, స్వాగతం, శుభోదయం — పఠనం", ["నమస్కారం", "స్వాగతం"])
        ]
    }
}

content_type_map = {
    "SPOKEN": "Voice Practice",
    "WRITTEN": "Written Practice",
    "READING": "Functional Reading"
}

for s_key, s_data in telugu_clean_structure.items():
    curr = db.query(models.Curriculum).filter(
        models.Curriculum.lang_id == telugu_lang.lang_id,
        (models.Curriculum.title.like(f"%{s_data['title']}%") | models.Curriculum.title.like("%తెలుగు%"))
    ).first()

    if not curr:
        curr = models.Curriculum(
            lang_id=telugu_lang.lang_id,
            title=f"Telugu - {s_data['title']}",
            level="FOUNDATIONAL",
            description=f"Zero level curriculum for Telugu ({s_key})"
        )
        db.add(curr)
        db.commit()
        db.refresh(curr)
    else:
        curr.title = f"Telugu - {s_data['title']}"
        db.commit()

    for idx, (m_name, l_title, target_t, phonetics) in enumerate(s_data["modules"], start=1):
        mod = db.query(models.Module).filter(
            models.Module.curriculum_id == curr.curriculum_id,
            models.Module.sequence_no == idx
        ).first()

        if not mod:
            mod = models.Module(
                curriculum_id=curr.curriculum_id,
                module_name=m_name,
                sequence_no=idx,
                skill_type=s_key
            )
            db.add(mod)
            db.commit()
            db.refresh(mod)
        else:
            mod.module_name = m_name
            mod.skill_type = s_key
            db.commit()

        les = db.query(models.Lesson).filter(
            models.Lesson.module_id == mod.module_id
        ).first()

        if not les:
            les = models.Lesson(
                module_id=mod.module_id,
                title=l_title,
                content_type=content_type_map[s_key],
                content_url=f"/audio/te/zero_{s_key.lower()}_seq{idx}.mp3",
                target_text=target_t,
                phonetic_script=str(phonetics),
                difficulty_level="Zero"
            )
            db.add(les)
        else:
            les.title = l_title
            les.target_text = target_t
            les.phonetic_script = str(phonetics)
            les.difficulty_level = "Zero"

        db.commit()

print("=" * 80)
print("SUCCESSFULLY UPDATED TELUGU CURRICULUM: CLEAN ENGLISH TITLES + PURE TELUGU CONTENT!")
print("=" * 80)
db.close()
