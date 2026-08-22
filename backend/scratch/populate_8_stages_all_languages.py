import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("=" * 80)
print("POPULATING 8 PROGRESSIVE SUB-MODULES ACROSS ALL 3 CURRICULUMS & 8 LANGUAGES")
print("=" * 80)

# Clear existing curriculum structure to ensure clean sequence
db.query(models.PathLesson).delete()
db.query(models.LearningPath).delete()
db.query(models.Lesson).delete()
db.query(models.Module).delete()
db.query(models.Curriculum).delete()
db.commit()

languages = db.query(models.Language).all()

stages = [
    ("Zero", "ZERO", 1),
    ("Absolute Beginner", "ABSOLUTE_BEGINNER", 2),
    ("Beginner", "BEGINNER", 3),
    ("Elementary", "ELEMENTARY", 4),
    ("Intermediate", "INTERMEDIATE", 5),
    ("Upper Intermediate", "UPPER_INTERMEDIATE", 6),
    ("Advanced", "ADVANCED", 7),
    ("Mastery", "MASTERY", 8)
]

curriculum_types = [
    {
        "type": "SPOKEN",
        "title": "Spoken Curriculum",
        "desc": "Progressive oral communication, phonetics, articulation, and spoken fluency.",
        "content_type": "Voice Practice",
        "stage_templates": {
            "Zero": ("Single Letter Sounds & Phonemes", "A-ah, B-buh, C-kuh, D-duh, E-eh", ["A-ah", "B-buh", "C-kuh"]),
            "Absolute Beginner": ("Short Syllables & Sound Blends", "Ba, Be, Bi, Bo, Bu — Syllable Blends", ["Ba", "Be", "Bi", "Bo"]),
            "Beginner": ("2-Letter Word Oral Practice", "Go, Be, In, On, At, Up — Oral Practice", ["Go", "Be", "In", "On"]),
            "Elementary": ("Everyday Nouns & Object Pronunciation", "Cat, Dog, Sun, Cup, Book — Object Names", ["Cat", "Dog", "Sun"]),
            "Intermediate": ("Daily Conversation & Greetings", "Good Morning, Hello, Thank You, Welcome", ["Good-Morn-ing", "Hel-lo"]),
            "Upper Intermediate": ("Workplace Team Communication", "Let us review our daily project goals clearly", ["Let", "us", "re-view"]),
            "Advanced": ("Customer Service & Public Speaking", "Thank you for calling, I am happy to assist you today", ["Thank", "you", "for", "cal-ling"]),
            "Mastery": ("Literary Articulation & Fluent Oratory", "Mastery over language transforms thought into eloquent expression", ["Mas-ter-y", "lan-guage"])
        }
    },
    {
        "type": "WRITTEN",
        "title": "Written Curriculum",
        "desc": "Progressive sentence writing, spelling, memo composition, and formal writing.",
        "content_type": "Written Practice",
        "stage_templates": {
            "Zero": ("Letter Formation & Native Script Strokes", "A, B, C, D, E — Letter Strokes", ["A", "B", "C", "D", "E"]),
            "Absolute Beginner": ("Vowel Marks & Accent Spelling", "Am, An, As, At — Vowel Spelling", ["Am", "An", "As", "At"]),
            "Beginner": ("2-Letter Word Composition", "In, On, It, To, Up, Go — Word Writing", ["In", "On", "It", "To"]),
            "Elementary": ("3-Letter Word Spelling", "Sun, Pen, Box, Bag, Car — Noun Spelling", ["Sun", "Pen", "Box"]),
            "Intermediate": ("Short Sentence Writing & Grammar", "I write simple words correctly every day", ["I", "write", "sim-ple"]),
            "Upper Intermediate": ("Workplace Memo & Email Writing", "Please find attached the quarterly project report for your review", ["Please", "find", "at-tached"]),
            "Advanced": ("Paragraph Composition & Essays", "Continuous practice enhances writing fluency and structured expression", ["Con-tin-u-ous", "prac-tice"]),
            "Mastery": ("Literary Writing & Formal Documentation", "Written communication is an essential cornerstone of human knowledge", ["Writ-ten", "com-mu-ni-ca-tion"])
        }
    },
    {
        "type": "READING",
        "title": "Reading Curriculum",
        "desc": "Progressive reading comprehension, phonics, safety notice reading, and literature.",
        "content_type": "Functional Reading",
        "stage_templates": {
            "Zero": ("Visual Alphabet Recognition", "A, B, C, D, E, F — Letter Recognition", ["A", "B", "C", "D", "E"]),
            "Absolute Beginner": ("Short Sound & Syllable Sight Reading", "Ba, Ca, Da, Fa, Ga — Sight Reading", ["Ba", "Ca", "Da", "Fa"]),
            "Beginner": ("2-Letter Word Reading", "In, On, At, Is, It, Up — Short Word Reading", ["In", "On", "At", "Is"]),
            "Elementary": ("Everyday Label & Sign Reading", "Open, Closed, Exit, Stop, Push — Label Reading", ["O-pen", "Closed", "Ex-it"]),
            "Intermediate": ("Short Passage Reading Comprehension", "Reading daily unlocks wisdom and opens new doors of opportunity", ["Read-ing", "dai-ly", "un-locks"]),
            "Upper Intermediate": ("Workplace Safety & Policy Reading", "Always wear protective safety equipment and follow supervisor instructions", ["Al-ways", "wear", "pro-tec-tive"]),
            "Advanced": ("News Article & Editorial Reading", "Technology and digital literacy transform modern education globally", ["Tech-nol-o-gy", "dig-i-tal"]),
            "Mastery": ("Literary Prose & Classical Literature Reading", "Profound literature reflects the timeless beauty and wisdom of humanity", ["Pro-found", "lit-er-a-ture"])
        }
    }
]

total_curriculums_created = 0
total_modules_created = 0
total_lessons_created = 0

for lang in languages:
    for c_cfg in curriculum_types:
        curr = models.Curriculum(
            lang_id=lang.lang_id,
            title=f"{lang.lang_name} - {c_cfg['title']}",
            level="FOUNDATIONAL",
            description=f"{c_cfg['desc']} ({lang.lang_name})"
        )
        db.add(curr)
        db.commit()
        db.refresh(curr)
        total_curriculums_created += 1
        
        for stage_name, difficulty_label, seq_no in stages:
            les_title, target_text, phonetics = c_cfg["stage_templates"][stage_name]
            
            mod = models.Module(
                curriculum_id=curr.curriculum_id,
                module_name=f"{stage_name}: {les_title}",
                sequence_no=seq_no,
                skill_type=c_cfg["type"]
            )
            db.add(mod)
            db.commit()
            db.refresh(mod)
            total_modules_created += 1
            
            les = models.Lesson(
                module_id=mod.module_id,
                title=f"{stage_name} Practice: {les_title}",
                content_type=c_cfg["content_type"],
                content_url=f"/audio/{lang.iso_code}/{c_cfg['type'].lower()}_seq{seq_no}.mp3",
                target_text=target_text,
                phonetic_script=str(phonetics),
                difficulty_level=difficulty_label
            )
            db.add(les)
            db.commit()
            total_lessons_created += 1

print(f"SUCCESSFULLY CREATED:\n  • {total_curriculums_created} Curriculums\n  • {total_modules_created} Modules (8 stages x 3 curriculums x 8 languages)\n  • {total_lessons_created} Lessons across all languages in Database!")
print("=" * 80)
db.close()
