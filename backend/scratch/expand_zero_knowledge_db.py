import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("Expanding Zero Knowledge Modules across all Language Curriculums in Database...")

curriculums = db.query(models.Curriculum).all()

zero_knowledge_templates = {
    "en": [
        {
            "module_name": "Zero Knowledge 1: Single Consonant Sounds & Alphabet Phonemes",
            "skill_type": "Reading & Pronunciation",
            "sequence_no": 1,
            "lessons": [
                ("Alphabet Phonemes Part 1 (A-E)", "Voice Practice", "A-ah, B-buh, C-kuh, D-duh, E-eh", ["A-ah", "B-buh", "C-kuh", "D-duh", "E-eh"]),
                ("Alphabet Phonemes Part 2 (F-J)", "Voice Practice", "F-fuh, G-guh, H-huh, I-ih, J-juh", ["F-fuh", "G-guh", "H-huh", "I-ih", "J-juh"]),
                ("Alphabet Phonemes Part 3 (K-O)", "Voice Practice", "K-kuh, L-luh, M-muh, N-nuh, O-oh", ["K-kuh", "L-luh", "M-muh", "N-nuh", "O-oh"]),
                ("Alphabet Phonemes Part 4 (P-T)", "Voice Practice", "P-puh, Q-kwuh, R-ruh, S-suh, T-tuh", ["P-puh", "Q-kwuh", "R-ruh", "S-suh", "T-tuh"])
            ]
        },
        {
            "module_name": "Zero Knowledge 2: Vowels & Syllable Recognition",
            "skill_type": "Phonics & Vowels",
            "sequence_no": 2,
            "lessons": [
                ("Short Vowel Sounds (a, e, i, o, u)", "Voice Practice", "Short A in Apple, Short E in Egg, Short I in Ink", ["Short-A", "Short-E", "Short-I"]),
                ("Long Vowel Sounds (A, E, I, O, U)", "Voice Practice", "Long A in Ape, Long E in Eagle, Long I in Ice", ["Long-A", "Long-E", "Long-I"]),
                ("Vowel & Consonant Syllable Blends", "Voice Practice", "Ba, Be, Bi, Bo, Bu — Syllable Sounds", ["Ba", "Be", "Bi", "Bo", "Bu"])
            ]
        },
        {
            "module_name": "Zero Knowledge 3: Two-Letter Word Blends & Everyday Phonemes",
            "skill_type": "Functional Reading",
            "sequence_no": 3,
            "lessons": [
                ("2-Letter Vowel-Consonant Words", "Functional Reading", "Am, An, As, At, If, In, Is, It, Of, On", ["Am", "An", "As", "At", "If", "In"]),
                ("2-Letter Consonant-Vowel Words", "Voice Practice", "Be, Do, Go, He, Me, No, So, To, We", ["Be", "Do", "Go", "He", "Me", "No"]),
                ("Basic Directional Words", "Functional Reading", "Up, In, On, At, To, Go — Everyday Words", ["Up", "In", "On", "At", "To", "Go"])
            ]
        },
        {
            "module_name": "Zero Knowledge 4: Number Sound Phonemes & Counting (1 to 10)",
            "skill_type": "Numeracy Literacy",
            "sequence_no": 4,
            "lessons": [
                ("Number Names One to Five", "Voice Practice", "One, Two, Three, Four, Five", ["One", "Two", "Three", "Four", "Five"]),
                ("Number Names Six to Ten", "Voice Practice", "Six, Seven, Eight, Nine, Ten", ["Six", "Sev-en", "Eight", "Nine", "Ten"])
            ]
        },
        {
            "module_name": "Zero Knowledge 5: Everyday Essential Greetings & Expression",
            "skill_type": "Voice Practice",
            "sequence_no": 5,
            "lessons": [
                ("Basic Daily Greetings", "Voice Practice", "Hello, Good Morning, Welcome", ["Hel-lo", "Good-Morn-ing", "Wel-come"]),
                ("Polite Expressions & Thanks", "Voice Practice", "Thank You, Please, Yes, No", ["Thank-You", "Please", "Yes", "No"])
            ]
        }
    ],
    "te": [
        {
            "module_name": "Zero Knowledge 1: అచ్చులు మరియు ప్రాథమిక స్వరాలు (Vowels & Sounds)",
            "skill_type": "Reading & Pronunciation",
            "sequence_no": 1,
            "lessons": [
                ("అచ్చులు భాగం 1 (అ, ఆ, ఇ, ఈ, ఉ, ఊ)", "Voice Practice", "అ, ఆ, ఇ, ఈ, ఉ, ఊ — ప్రాథమిక అక్షర సాధన", ["అ", "ఆ", "ఇ", "ఈ", "ఉ", "ఊ"]),
                ("అచ్చులు భాగం 2 (ఋ, ఎ, ఏ, ఐ, ఒ, ఓ, ఔ)", "Voice Practice", "ఋ, ఎ, ఏ, ఐ, ఒ, ఓ, ఔ — స్వరాల ఉచ్చారణ", ["ఋ", "ఎ", "ఏ", "ఐ", "ఒ", "ఓ", "ఔ"])
            ]
        },
        {
            "module_name": "Zero Knowledge 2: హల్లులు గుర్తింపు (Consonant Phonemes)",
            "skill_type": "Phonics & Vowels",
            "sequence_no": 2,
            "lessons": [
                ("హల్లులు భాగం 1 (క, ఖ, గ, ఘ, ఙ)", "Voice Practice", "క, ఖ, గ, ఘ, ఙ — గుణింత అక్షర ఉచ్చారణ", ["క", "ఖ", "గ", "ఘ", "ఙ"]),
                ("హల్లులు భాగం 2 (చ, ఛ, జ, ఝ, ఞ)", "Voice Practice", "చ, ఛ, జ, ఝ, ఞ — ప్రాథమిక హల్లు శబ్దాలు", ["చ", "ఛ", "జ", "ఝ", "ఞ"])
            ]
        }
    ],
    "hi": [
        {
            "module_name": "Zero Knowledge 1: स्वर एवं प्राथमिक उच्चारण (Vowels & Phonemes)",
            "skill_type": "Reading & Pronunciation",
            "sequence_no": 1,
            "lessons": [
                ("स्वर परिचय भाग 1 (अ, आ, इ, ई, उ, ऊ)", "Voice Practice", "अ, आ, इ, ई, उ, ऊ — प्राथमिक स्वर उच्चारण", ["अ", "आ", "इ", "ई", "उ", "ऊ"]),
                ("स्वर परिचय भाग 2 (ऋ, ए, ऐ, ओ, औ, अं, अः)", "Voice Practice", "ऋ, ए, ऐ, ओ, औ, अं, अः — स्वर पहचान", ["ऋ", "ए", "ऐ", "ओ", "औ"])
            ]
        },
        {
            "module_name": "Zero Knowledge 2: व्यंजन पहचान (Consonant Phonemes)",
            "skill_type": "Phonics & Vowels",
            "sequence_no": 2,
            "lessons": [
                ("व्यंजन भाग 1 (क, ख, ग, घ, ङ)", "Voice Practice", "क, ख, ग, घ, ङ — मूल व्यंजन ध्वनियाँ", ["क", "ख", "ग", "घ", "ङ"]),
                ("व्यंजन भाग 2 (च, छ, ज, झ, ञ)", "Voice Practice", "च, छ, ज, झ, ञ — द्वितीय वर्ग व्यंजन", ["च", "छ", "ज", "झ", "ञ"])
            ]
        }
    ]
}

total_modules_created = 0
total_lessons_created = 0

for curr in curriculums:
    lang = db.query(models.Language).filter(models.Language.lang_id == curr.lang_id).first()
    lang_code = lang.iso_code if lang else "en"
    
    templates = zero_knowledge_templates.get(lang_code, zero_knowledge_templates["en"])
    
    for t_idx, t in enumerate(templates):
        existing_mod = db.query(models.Module).filter(
            models.Module.curriculum_id == curr.curriculum_id,
            models.Module.module_name == t["module_name"]
        ).first()
        
        if not existing_mod:
            new_mod = models.Module(
                curriculum_id=curr.curriculum_id,
                module_name=t["module_name"],
                sequence_no=t["sequence_no"],
                skill_type=t["skill_type"]
            )
            db.add(new_mod)
            db.commit()
            db.refresh(new_mod)
            total_modules_created += 1
            mod_obj = new_mod
        else:
            mod_obj = existing_mod
            
        for les_tuple in t["lessons"]:
            les_title, les_type, les_target, les_phonemes = les_tuple
            existing_les = db.query(models.Lesson).filter(
                models.Lesson.module_id == mod_obj.module_id,
                models.Lesson.title == les_title
            ).first()
            
            if not existing_les:
                new_les = models.Lesson(
                    module_id=mod_obj.module_id,
                    title=les_title,
                    content_type=les_type,
                    content_url=f"/audio/{lang_code}/zk_{les_title[:10]}.mp3",
                    target_text=les_target,
                    phonetic_script=str(les_phonemes),
                    difficulty_level="FOUNDATIONAL"
                )
                db.add(new_les)
                total_lessons_created += 1

db.commit()
print(f"Successfully populated {total_modules_created} new Zero Knowledge Modules and {total_lessons_created} Lessons in Database!")
db.close()
