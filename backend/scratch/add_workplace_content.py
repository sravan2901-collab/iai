import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("Populating Workplace Communication Modules & Lessons across all Curriculums...")

curriculums = db.query(models.Curriculum).all()

workplace_lessons_data = [
    {
        "title": "Professional Team Meeting Greetings & Agenda",
        "content_type": "Voice Practice",
        "target_text": "Good morning team, let us review our key project goals and daily targets clearly",
        "phonetic_script": json.dumps(["Good morn-ing team", "let us re-view key goals"]),
        "difficulty_level": "FOUNDATIONAL"
    },
    {
        "title": "Workplace Safety Guidelines & Emergency Protocols",
        "content_type": "Functional Reading",
        "target_text": "Always wear protective safety equipment and report all hazards immediately to your supervisor",
        "phonetic_script": json.dumps(["Al-ways wear safe-ty e-quip-ment", "re-port haz-ards"]),
        "difficulty_level": "FUNCTIONAL"
    },
    {
        "title": "Customer Service Dialogue & Polite Assistance",
        "content_type": "Voice Practice",
        "target_text": "Thank you for contacting customer support. I am happy to assist you with your inquiry",
        "phonetic_script": json.dumps(["Thank you for con-tac-ting sup-port", "hap-py to as-sist"]),
        "difficulty_level": "FUNCTIONAL"
    },
    {
        "title": "Professional Workplace Email & Memo Literacy",
        "content_type": "Functional Reading",
        "target_text": "Please find attached the quarterly project report for your review and formal approval",
        "phonetic_script": json.dumps(["Please find at-tached the re-port", "for your ap-pro-val"]),
        "difficulty_level": "INTERMEDIATE"
    },
    {
        "title": "Managerial Progress Reporting & Team Coordination",
        "content_type": "Voice Practice",
        "target_text": "Our team successfully achieved all weekly performance benchmarks with zero technical errors",
        "phonetic_script": json.dumps(["Our team a-chieved all bench-marks", "zero er-rors"]),
        "difficulty_level": "ADVANCED"
    },
    {
        "title": "Constructive Workplace Feedback & Collaboration",
        "content_type": "Functional Reading",
        "target_text": "Effective collaboration relies on mutual respect, active listening, and constructive dialogue",
        "phonetic_script": json.dumps(["Ef-fec-tive col-lab-o-ra-tion", "con-struc-tive di-a-logue"]),
        "difficulty_level": "ADVANCED"
    }
]

added_lessons_count = 0

for curr in curriculums:
    # Check or create Workplace Communication Module for this curriculum
    mod = db.query(models.Module).filter(
        models.Module.curriculum_id == curr.curriculum_id,
        models.Module.module_name.like("%Workplace Communication%")
    ).first()

    if not mod:
        mod = models.Module(
            curriculum_id=curr.curriculum_id,
            module_name="Workplace Communication & Professional Skills",
            sequence_no=10,
            skill_type="Reading & Pronunciation"
        )
        db.add(mod)
        db.commit()
        db.refresh(mod)
        print(f"Created Module ID={mod.module_id} for Curriculum ID={curr.curriculum_id}")

    for les_data in workplace_lessons_data:
        existing = db.query(models.Lesson).filter(
            models.Lesson.module_id == mod.module_id,
            models.Lesson.title == les_data["title"]
        ).first()

        if not existing:
            new_les = models.Lesson(
                module_id=mod.module_id,
                title=les_data["title"],
                content_type=les_data["content_type"],
                content_url=f"/audio/workplace_{added_lessons_count + 1}.mp3",
                target_text=les_data["target_text"],
                phonetic_script=les_data["phonetic_script"],
                difficulty_level=les_data["difficulty_level"]
            )
            db.add(new_les)
            db.commit()
            added_lessons_count += 1

print(f"Successfully populated {added_lessons_count} new Workplace Communication lessons into aksharai_dev.db!")
db.close()
