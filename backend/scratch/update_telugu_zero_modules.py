import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("=" * 80)
print("UPDATING TELUGU ZERO LEVEL MODULES & LESSONS ENTIRELY IN NATIVE TELUGU SCRIPT")
print("=" * 80)

# Get Telugu Language
telugu_lang = db.query(models.Language).filter(models.Language.iso_code == 'te').first()

if not telugu_lang:
    print("Telugu language not found in database!")
    sys.exit(1)

telugu_zero_modules = {
    "SPOKEN": {
        "title": "తెలుగు - శ్రవణ పాఠ్యాంశం (Spoken Curriculum)",
        "modules": [
            {
                "seq": 1,
                "mod_name": "మాడ్యూల్ 1: శబ్ద నిధి (అచ్చులు మరియు హల్లుల ఉచ్చారణ)",
                "les_title": "శబ్ద నిధి: అచ్చులు మరియు హల్లుల ఉచ్చారణ సాధన",
                "target_text": "అ, ఆ, ఇ, ఈ, ఉ, ఊ, ఋ, ఎ, ఏ, ఐ, ఒ, ఓ, ఔ",
                "phonetics": ["అ", "ఆ", "ఇ", "ఈ"]
            },
            {
                "seq": 2,
                "mod_name": "మాడ్యూల్ 2: శ్రవణ సాధన (సంభాషణ స్వర శైలి మరియు ధ్వని లయ)",
                "les_title": "గ్రహణ శ్రవణ సాధన: సంభాషణ స్వర తరంగాలు",
                "target_text": "నమస్కారం అండి, మీరు ఎలా ఉన్నారు? ఈ పాఠానికి స్వాగతం.",
                "phonetics": ["నమస్కారం", "స్వాగతం"]
            },
            {
                "seq": 3,
                "mod_name": "మాడ్యూల్ 3: ప్రాథమిక జీవన వాక్యాలు (మర్యాద పదాలు)",
                "les_title": "అత్యవసర జీవన వాక్యాలు: రోజువారీ మర్యాద పదాలు",
                "target_text": "నమస్కారం, సెలవు, దయచేసి, ధన్యవాదాలు, అవును, కాదు, క్షమించండి",
                "phonetics": ["నమస్కారం", "ధన్యవాదాలు"]
            },
            {
                "seq": 4,
                "mod_name": "మాడ్యూల్ 4: 0 నుండి 10 వరకు సంఖ్యల ఉచ్చారణ",
                "les_title": "సంఖ్యల ఉచ్చారణ: సున్నా నుండి పది వరకు",
                "target_text": "సున్నా, ఒకటి, రెండు, మూడు, నాలుగు, ఐదు, ఆరు, ఏడు, ఎనిమిది, తొమ్మిది, పది",
                "phonetics": ["సున్నా", "ఒకటి", "పది"]
            },
            {
                "seq": 5,
                "mod_name": "మాడ్యూల్ 5: స్వయం పరిచయ వాక్యాలు (\"నా పేరు...\", \"నేను... వచ్చాను\")",
                "les_title": "స్వయం పరిచయ వాక్యాలు: పేరు మరియు ప్రాంతం",
                "target_text": "నమస్కారం, నా పేరు ఆనంద్. నేను హైదరాబాద్ నుండి వచ్చాను.",
                "phonetics": ["నా-పేరు", "నేను-వచ్చాను"]
            },
            {
                "seq": 6,
                "mod_name": "మాడ్యూల్ 6: శ్రవణ అనుకరణ సాధన (ఆడియో వింటూ అనుకరించడం)",
                "les_title": "శ్రవణ అనుకరణ సాధన: చెవి మరియు నోటి సమన్వయం",
                "target_text": "నా వెంట స్పష్టంగా చెప్పండి: నేను శ్రద్ధగా భాష నేర్చుకుంటున్నాను.",
                "phonetics": ["స్పష్టంగా", "నేర్చుకుంటున్నాను"]
            }
        ]
    },
    "WRITTEN": {
        "title": "తెలుగు - లేఖన పాఠ్యాంశం (Written Curriculum)",
        "modules": [
            {
                "seq": 1,
                "mod_name": "మాడ్యూల్ 1: అక్షర లేఖన సాధన (ప్రాథమిక అక్షర స్వరూపం)",
                "les_title": "అక్షర నిర్మాణం: ప్రాథమిక అక్షర లేఖన సాధన",
                "target_text": "అ, ఆ, ఇ, ఈ, ఉ — ప్రాథమిక అక్షర లేఖనం",
                "phonetics": ["అ", "ఆ", "ఇ", "ఈ"]
            },
            {
                "seq": 2,
                "mod_name": "మాడ్యూల్ 2: గుణింత గుర్తులు (తలకట్టు, దీర్ఘం, గుడి, గుడిదీర్ఘం)",
                "les_title": "గుణింత గుర్తులు మరియు స్వర లేఖనం",
                "target_text": "తలకట్టు, దీర్ఘం, గుడి, గుడిదీర్ఘం — గుణింత గుర్తులు",
                "phonetics": ["తలకట్టు", "దీర్ఘం"]
            },
            {
                "seq": 3,
                "mod_name": "మాడ్యూల్ 3: ద్వియక్షర పదాల రాత సాధన",
                "les_title": "ద్వియక్షర పదాల రాత సాధన",
                "target_text": "అమ, అని, ఇది, అది, ఇటు, అటు — పదాల రాత సాధన",
                "phonetics": ["అమ", "అని", "ఇది"]
            },
            {
                "seq": 4,
                "mod_name": "మాడ్యూల్ 4: 0 నుండి 10 వరకు సంఖ్యల రాత సాధన",
                "les_title": "సంఖ్యల రాత సాధన: ౦ నుండి ౧౦ వరకు",
                "target_text": "౦, ౧, ౨, ౩, ౪, ౫, ౬, ౭, ౮, ౯, ౧౦ — సంఖ్యలు",
                "phonetics": ["సున్నా", "పది"]
            },
            {
                "seq": 5,
                "mod_name": "మాడ్యూల్ 5: రోజువారీ మర్యాద పదాల రాత సాధన",
                "les_title": "ముఖ్య మర్యాద పదాల రాత సాధన",
                "target_text": "నమస్కారం, ధన్యవాదాలు, అవును, కాదు — రాయడం",
                "phonetics": ["నమస్కారం", "ధన్యవాదాలు"]
            },
            {
                "seq": 6,
                "mod_name": "మాడ్యూల్ 6: స్వయం పరిచయ వాక్యం రాయడం",
                "les_title": "స్వయం పరిచయ వాక్యం రాయడం",
                "target_text": "నా పేరు ఆనంద్. నేను హైదరాబాద్ నుండి వచ్చాను.",
                "phonetics": ["నా-పేరు", "వచ్చాను"]
            }
        ]
    },
    "READING": {
        "title": "తెలుగు - పఠన పాఠ్యాంశం (Reading Curriculum)",
        "modules": [
            {
                "seq": 1,
                "mod_name": "మాడ్యూల్ 1: దృశ్య అక్షర గుర్తింపు (అక్షరాల సాధన)",
                "les_title": "అక్షర రూప గుర్తింపు సాధన",
                "target_text": "అ, ఆ, ఇ, ఈ, ఉ, ఊ — అక్షరాల గుర్తింపు",
                "phonetics": ["అ", "ఆ", "ఇ", "ఈ"]
            },
            {
                "seq": 2,
                "mod_name": "మాడ్యూల్ 2: గుణింత రూపాల పఠనావగాహన",
                "les_title": "గుణింత రూపాల పఠనావగాహన",
                "target_text": "క, కా, కి, కీ, కు, కూ — గుణింత పఠనం",
                "phonetics": ["క", "కా", "కి"]
            },
            {
                "seq": 3,
                "mod_name": "మాడ్యూల్ 3: ద్వియక్షర పదాల పఠనం",
                "les_title": "ద్వియక్షర పద పఠనం",
                "target_text": "అల, ఇల, ఈల, ఉల, ఎల, ఒల — ద్వియక్షర పదాలు",
                "phonetics": ["అల", "ఇల", "ఈల"]
            },
            {
                "seq": 4,
                "mod_name": "మాడ్యూల్ 4: 0 నుండి 10 వరకు సంఖ్యల పఠనం",
                "les_title": "సంఖ్యల పఠనం: సున్నా నుండి పది వరకు",
                "target_text": "సున్నా, ఒకటి, రెండు, మూడు, నాలుగు, ఐదు, ఆరు, ఏడు, ఎనిమిది, తొమ్మిది, పది",
                "phonetics": ["సున్నా", "ఒకటి", "పది"]
            },
            {
                "seq": 5,
                "mod_name": "మాడ్యూల్ 5: రోజువారీ సూచికలు మరియు బోర్డుల పఠనం",
                "les_title": "రోజువారీ బోర్డులు మరియు గుర్తుల పఠనం",
                "target_text": "తెరిచి ఉంది, మూసివేసి ఉంది, నిష్క్రమణ, ఆగుము",
                "phonetics": ["తెరిచి-ఉంది", "నిష్క్రమణ"]
            },
            {
                "seq": 6,
                "mod_name": "మాడ్యూల్ 6: స్వాగత పలికే వాక్యాల పఠనం",
                "les_title": "స్వాగత పలికే వాక్యాల పఠనం",
                "target_text": "నమస్కారం, స్వాగతం, శుభోదయం — పఠనం",
                "phonetics": ["నమస్కారం", "స్వాగతం"]
            }
        ]
    }
}

updated_mods = 0
updated_less = 0

for skill_key, skill_cfg in telugu_zero_modules.items():
    curriculum = db.query(models.Curriculum).filter(
        models.Curriculum.lang_id == telugu_lang.lang_id,
        (models.Curriculum.title.like(f"%{skill_key.capitalize()}%") | models.Curriculum.title.like("%తెలుగు%"))
    ).first()
    
    if not curriculum:
        curriculum = models.Curriculum(
            lang_id=telugu_lang.lang_id,
            title=skill_cfg["title"],
            level="FOUNDATIONAL",
            description=f"తెలుగు సున్నా స్థాయి పాఠ్యాంశం ({skill_key})"
        )
        db.add(curriculum)
        db.commit()
        db.refresh(curriculum)
    else:
        curriculum.title = skill_cfg["title"]
        db.commit()
        
    for m_info in skill_cfg["modules"]:
        seq = m_info["seq"]
        
        module = db.query(models.Module).filter(
            models.Module.curriculum_id == curriculum.curriculum_id,
            models.Module.sequence_no == seq
        ).first()
        
        if not module:
            module = models.Module(
                curriculum_id=curriculum.curriculum_id,
                module_name=m_info["mod_name"],
                sequence_no=seq,
                skill_type=skill_key
            )
            db.add(module)
            db.commit()
            db.refresh(module)
        else:
            module.module_name = m_info["mod_name"]
            module.skill_type = skill_key
            db.commit()
            
        updated_mods += 1
        
        lesson = db.query(models.Lesson).filter(
            models.Lesson.module_id == module.module_id
        ).first()
        
        content_type_map = {"SPOKEN": "Voice Practice", "WRITTEN": "Written Practice", "READING": "Functional Reading"}
        
        if not lesson:
            lesson = models.Lesson(
                module_id=module.module_id,
                title=m_info["les_title"],
                content_type=content_type_map[skill_key],
                content_url=f"/audio/te/zero_{skill_key.lower()}_seq{seq}.mp3",
                target_text=m_info["target_text"],
                phonetic_script=str(m_info["phonetics"]),
                difficulty_level="Zero"
            )
            db.add(lesson)
        else:
            lesson.title = m_info["les_title"]
            lesson.target_text = m_info["target_text"]
            lesson.phonetic_script = str(m_info["phonetics"])
            lesson.difficulty_level = "Zero"
            
        db.commit()
        updated_less += 1

print(f"SUCCESSFULLY UPDATED TELUGU ZERO LEVEL MODULES ({updated_mods}) & LESSONS ({updated_less}) IN NATIVE TELUGU SCRIPT!")
print("=" * 80)
db.close()
