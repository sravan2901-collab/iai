import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("=" * 80)
print("UPDATING ZERO LEVEL WRITTEN CURRICULUM ACCORDING TO USER SPECIFICATION FOR ALL 8 LANGUAGES")
print("=" * 80)

WRITTEN_CURRICULUM_SPEC = {
    # 1. TELUGU
    "te": [
        ("మాడ్యూల్ 1: పూర్తి అక్షరమాల లేఖనం (అచ్చులు మరియు హల్లుల స్వరూపం)", "పూర్తి అక్షరమాల లేఖన సాధన", "అ, ఆ, ఇ, ఈ, ఉ, ఊ, ఋ, ఎ, ఏ, ఐ, ఒ, ఓ, ఔ — అక్షర సముదాయం", ["అ", "ఆ", "ఇ", "ఈ"]),
        ("మాడ్యూల్ 2: అక్షర రాత వరుస క్రమం మరియు వంపు సాధన", "అక్షర రాత వరుస క్రమం మరియు వంపులు", "అక్షరాల వంపులు మరియు సుడి తిరుగుళ్లు లేఖన సాధన", ["వంపులు", "సుడి"]),
        ("మాడ్యూల్ 3: ఎడమ నుండి కుడికి రాత దిశ మరియు వాక్య అమరిక", "రాత దిశ నియమాలు: ఎడమ నుండి కుడికి", "ఎడమ నుండి కుడికి లైన్ల సమన్వయంతో రాయడం", ["ఎడమ", "కుడి"]),
        ("మాడ్యూల్ 4: గుణింత గుర్తులు మరియు స్వర గుర్తుల రాత సాధన", "గుణింత గుర్తులు మరియు స్వర గుర్తులు", "తలకట్టు, దీర్ఘం, గుడి, గుడిదీర్ఘం, కొమ్ము, కొమ్ముదీర్ఘం", ["తలకట్టు", "దీర్ఘం"]),
        ("మాడ్యూల్ 5: అక్షరాల కాపీ రాత మరియు ట్రేసింగ్ సాధన", "అక్షరాల ట్రేసింగ్ మరియు ప్రతిలిపి రాత", "అ, ఆ, ఇ, ఈ, ఉ — ట్రేసింగ్ మరియు అనుకరణ రాత సాధన", ["ట్రేసింగ్", "రాత"]),
        ("మాడ్యూల్ 6: స్వయం పేరు మరియు ప్రాథమిక పదాల రాత సాధన", "స్వయం పేరు మరియు మర్యాద పదాల రాత", "నా పేరు ఆనంద్. నమస్కారం, ధన్యవాదాలు — రాత సాధన", ["నా-పేరు", "ధన్యవాదాలు"])
    ],

    # 2. HINDI
    "hi": [
        ("मॉड्यूल 1: पूर्ण वर्णमाला लेखन (स्वर एवं व्यंजन वर्ण समूह)", "पूर्ण वर्णमाला वर्ण समूह लेखन अभ्यास", "अ, आ, इ, ई, उ, ऊ, ऋ, ए, ऐ, ओ, औ — पूर्ण वर्ण समूह", ["अ", "आ", "इ", "ई"]),
        ("मॉड्यूल 2: वर्ण लेखन क्रम एवं शिरोरेखा नियम", "वर्ण स्ट्रोक क्रम एवं शिरोरेखा नियम", "वर्ण स्ट्रोक क्रम एवं ऊपरी शिरोरेखा नियम अभ्यास", ["स्ट्रोक", "शिरोरेखा"]),
        ("मॉड्यूल 3: बाएँ से दाएँ लेखन दिशा एवं रेखा संरेखण", "लेखन दिशा: बाएँ से दाएँ पंक्तिबद्ध", "बाएँ से दाएँ स्पष्ट पंक्तिबद्ध लेखन अभ्यास", ["बाएँ", "दाएँ"]),
        ("मॉड्यूल 4: मात्राएँ एवं स्वर चिन्ह लेखन (मात्रा ज्ञान)", "मात्राएँ एवं स्वर चिन्ह लेखन अभ्यास", "आ की मात्रा, इ की मात्रा, ई की मात्रा, उ की मात्रा", ["मात्रा", "चिन्ह"]),
        ("मॉड्यूल 5: वर्ण ट्रेसिंग एवं अनुलेखन अभ्यास", "वर्ण ट्रेसिंग एवं प्रतिलिपि अभ्यास", "अ, आ, इ, ई, उ — वर्ण ट्रेसिंग एवं प्रतिलिपि अभ्यास", ["ट्रेसिंग", "अनुलेखन"]),
        ("मॉड्यूल 6: स्वयं का नाम एवं मुख्य शब्द लेखन", "स्वयं का नाम एवं मुख्य शब्द लेखन अभ्यास", "मेरा नाम राहुल है। नमस्ते, धन्यवाद — लेखन अभ्यास", ["मेरा-नाम", "धन्यवाद"])
    ],

    # 3. TAMIL
    "ta": [
        ("தொகுதி 1: முழு எழுத்துமாலை (உயிர் மற்றும் மெய் எழுத்துக்கள்)", "முழு எழுத்துமாலை எழுத்துப் பயிற்சி", "அ, ஆ, இ, ஈ, உ, ஊ, எ, ஏ, ஐ, ஒ, ஓ, ஔ — எழுத்துக்கள்", ["அ", "ஆ", "இ", "ஈ"]),
        ("தொகுதி 2: எழுத்து வரைவு வரிசை மற்றும் வடிவ விதிகள்", "எழுத்து வரைவு வரிசை விதிகள்", "எழுத்து வளைவுகள் மற்றும் கோடுகள் வரைவுப் பயிற்சி", ["வரைவு", "வடிவம்"]),
        ("தொகுதி 3: இடமிருந்து வலமாக எழுதும் திசை விதிகள்", "எழுதும் திசை: இடமிருந்து வலமாக", "இடமிருந்து வலமாக நேர்கோட்டில் எழுதும் பயிற்சி", ["இடமிருந்து", "வலமாக"]),
        ("தொகுதி 4: உயிர்மெய் குறியீடுகள் மற்றும் புள்ளியிட்ட எழுத்துக்கள்", "உயிர்மெய் குறியீடுகள் பயிற்சி", "துணைக்கால், மேல்விலங்கு, கீழ்விலங்கு — குறியீடுகள்", ["துணைக்கால்", "குறியீடுகள்"]),
        ("தொகுதி 5: எழுத்துக்கள் நகலெடுப்பு மற்றும் டிரேசிங் பயிற்சி", "எழுத்துக்கள் டிரேசிங் பயிற்சி", "அ, ஆ, இ, ஈ, உ — டிரேசிங் மற்றும் நகலெடுப்பு", ["டிரேசிங்", "நகலெடுப்பு"]),
        ("தொகுதி 6: சுய பெயர் மற்றும் முக்கிய சொற்கள் எழுதுதல்", "சுய பெயர் மற்றும் முக்கிய சொற்கள் எழுதுதல்", "என் பெயர் அன்பு. வணக்கம், நன்றி — எழுதுதல்", ["என்-பெயர்", "நன்றி"])
    ],

    # 4. MARATHI
    "mr": [
        ("मॉड्यूल 1: पूर्ण मूळाक्षरे लेखन (स्वर व व्यंजन गट)", "पूर्ण मूळाक्षरे लेखन सराव", "अ, आ, इ, ई, उ, ऊ, ऋ, ए, ऐ, ओ, औ — मूळाक्षरे", ["अ", "आ", "इ", "ई"]),
        ("मॉड्यूल 2: अक्षर लेखन क्रम व शिरोरेषा नियम", "अक्षर लेखन क्रम व शिरोरेषा नियम", "अक्षर वळण व शिरोरेषा नियम सराव", ["वळण", "शिरोरेषा"]),
        ("मॉड्यूल 3: डावीकडून उजवीकडे लेखन दिशा नियम", "लेखन दिशा: डावीकडून उजवीकडे", "डावीकडून उजवीकडे ओळबद्ध लेखन सराव", ["डावीकडून", "उजवीकडे"]),
        ("मॉड्यूल 4: मात्रा, वेलांटी व स्वर चिन्हे लेखन", "स्वर चिन्हे व वेलांटी लेखन सराव", "काना, वेलांटी, उकार, मात्रा — चिन्हे लेखन", ["काना", "वेलांटी"]),
        ("मॉड्यूल 5: अक्षर ट्रेसिंग व अनुलेखन सराव", "अक्षर ट्रेसिंग व अनुलेखन सराव", "अ, आ, इ, ई, उ — अक्षर ट्रेसिंग सराव", ["ट्रेसिंग", "अनुलेखन"]),
        ("मॉड्यूल 6: स्वतःचे नाव व मुख्य शब्द लेखन", "स्वतःचे नाव व शब्द लेखन सराव", "माझे नाव सचिन आहे. नमस्कार, धन्यवाद — लेखन", ["माझे-नाव", "धन्यवाद"])
    ],

    # 5. BENGALI
    "bn": [
        ("মডিউল ১: সম্পূর্ণ বর্ণমালা লিখন (স্বর ও ব্যঞ্জন বর্ণ)", "সম্পূর্ণ বর্ণমালা লিখন অনুশীলন", "অ, আ, ই, ঈ, উ, ঊ, ঋ, এ, ঐ, ও, ঔ — বর্ণমালা", ["অ", "আ", "ই", "ঈ"]),
        ("মডিউল ২: বর্ণ মাত্রা ও লিখন ধারাবাহিকতা নিয়ম", "বর্ণ মাত্রা ও লিখন ধারাবাহিকতা", "বর্ণের মাত্রা ও টানের ক্রম অনুশীলন", ["মাত্রা", "টান"]),
        ("মডিউল ৩: বাম থেকে ডানে লেখার দিক ও বিন্যাস", "লেখার দিক: বাম থেকে ডানে", "বাম থেকে ডানে সারিবদ্ধ লিখন অনুশীলন", ["বাম", "ডান"]),
        ("মডিউল ৪: কার চিহ্ন ও স্বর চিহ্ন লিখন", "কার চিহ্ন ও স্বর চিহ্ন লিখন অনুশীলন", "আ-কার, ই-কার, ঈ-কার, উ-কার — কার চিহ্ন", ["আ-কার", "ই-কার"]),
        ("মডিউল ৫: বর্ণ ট্রেসিং ও অনুলিপি অনুশীলন", "বর্ণ ট্রেসিং ও অনুলিপি অনুশীলন", "অ, আ, ই, ঈ, উ — ট্রেসিং অনুশীলন", ["ট্রেসিং", "অনুলিপি"]),
        ("মডিউল ৬: নিজের নাম ও প্রয়োজনীয় শব্দ লিখন", "নিজের নাম ও প্রয়োজনীয় শব্দ লিখন", "আমার নাম অনির্বাণ। নমস্কার, ধন্যবাদ — লিখন", ["আমার-নাম", "ধন্যবাদ"])
    ],

    # 6. KANNADA
    "kn": [
        ("ಮಾಡ್ಯೂಲ್ 1: ಪೂರ್ಣ ಅಕ್ಷರಮಾಲೆ ಬರಹ (ಸ್ವರ ಮತ್ತು ವ್ಯಂಜನ)", "ಪೂರ್ಣ ಅಕ್ಷರಮಾಲೆ ಬರಹ ಅಭ್ಯಾಸ", "ಅ, ಆ, ಇ, ಈ, ಉ, ಊ, ಋ, ಎ, ಏ, ಐ, ಒ, ಓ, ಔ — ಅಕ್ಷರಮಾಲೆ", ["ಅ", "ಆ", "ಇ", "ಈ"]),
        ("ಮಾಡ್ಯೂಲ್ 2: ಅಕ್ಷರ ಬರಹದ ಸಾಲು ಮತ್ತು ತಿರುವು ನಿಯಮಗಳು", "ಅಕ್ಷರ ಬರಹದ ತಿರುವು ನಿಯಮಗಳು", "ಅಕ್ಷರಗಳ ತಿರುವು ಮತ್ತು ಬರಹದ ಕ್ರಮ ಅಭ್ಯಾಸ", ["ತಿರುವು", "ಸಾಲು"]),
        ("ಮಾಡ್ಯೂಲ್ 3: ಎಡದಿಂದ ಬಲಕ್ಕೆ ಬರೆಯುವ ದಿಕ್ಸೂಚಿ ನಿಯಮಗಳು", "ಬರೆಯುವ ದಿಕ್ಕು: ಎಡದಿಂದ ಬಲಕ್ಕೆ", "ಎಡದಿಂದ ಬಲಕ್ಕೆ ಸಾಲಿನಲ್ಲಿ ಬರೆಯುವ ಅಭ್ಯಾಸ", ["ಎಡದಿಂದ", "ಬಲಕ್ಕೆ"]),
        ("ಮಾಡ್ಯೂಲ್ 4: ಗುಣಿತಾಕ್ಷರ ಚಿಹ್ನೆಗಳ ಬರಹ ಅಭ್ಯಾಸ", "ಗುಣಿತಾಕ್ಷರ ಚಿಹ್ನೆಗಳ ಬರಹ ಅಭ್ಯಾಸ", "ತಲಕಟ್ಟು, ದೀರ್ಘ, ಗುಡಿಸು, ಕೊಂಬು — ಚಿಹ್ನೆಗಳು", ["ತಲಕಟ್ಟು", "ದೀರ್ಘ"]),
        ("ಮಾಡ್ಯೂಲ್ 5: ಅಕ್ಷರ ಟ್ರೇಸಿಂಗ್ ಮತ್ತು ಅನುಕರಣ ಬರಹ", "ಅಕ್ಷರ ಟ್ರೇಸಿಂಗ್ ಅಭ್ಯಾಸ", "ಅ, ಆ, ಇ, ಈ, ಉ — ಟ್ರೇಸಿಂಗ್ ಅಭ್ಯಾಸ", ["ಟ್ರೇಸಿಂಗ್", "ಅನುಕರಣ"]),
        ("ಮಾಡ್ಯೂಲ್ 6: ಸ್ವಯಂ ಹೆಸರು ಮತ್ತು ಮುಖ್ಯ ಪದಗಳ ಬರಹ", "ಸ್ವಯಂ ಹೆಸರು ಮತ್ತು ಮುಖ್ಯ ಪದಗಳ ಬರಹ", "ನನ್ನ ಹೆಸರು ಸುಹಾಸ್. ನಮಸ್ಕಾರ, ಧನ್ಯವಾದಗಳು — ಬರಹ", ["ನನ್ನ-ಹೆಸರು", "ಧನ್ಯವಾದಗಳು"])
    ],

    # 7. SPANISH
    "es": [
        ("Módulo 1: Alfabeto Completo (Mayúsculas y Minúsculas)", "Inventario del Alfabeto Completo", "A, a, B, b, C, c, D, d, E, e — Alfabeto Completo", ["A", "B", "C"]),
        ("Módulo 2: Orden de Trazos y Reglas de Formación", "Reglas de Formación y Trazos", "Trazos superiores e inferiores en letras mayúsculas y minúsculas", ["Trazos", "Formación"]),
        ("Módulo 3: Dirección de Escritura de Izquierda a Derecha", "Dirección de Escritura y Alineación", "Alineación de renglón de izquierda a derecha", ["Izquierda", "Derecha"]),
        ("Módulo 4: Signos Diacríticos y Acentos (Á, É, Í, Ó, Ú, Ñ, Ü)", "Signos Diacríticos y Tildes", "Á, É, Í, Ó, Ú, Ñ, Ü — Tildes y Signos Diacríticos", ["Tildes", "Diacríticos"]),
        ("Módulo 5: Práctica de Creado de Trazos y Copiado de Letras", "Trazado y Copiado de Letras", "Copiado y caligrafía de letras A, B, C, D, E", ["Copiado", "Trazos"]),
        ("Módulo 6: Escritura del Nombre Propio y Palabras Comunes", "Escritura del Nombre y Vocabulario Común", "Mi nombre es Carlos. Hola, Gracias, Por favor — Escritura", ["Mi-nombre", "Gracias"])
    ],

    # 8. ENGLISH
    "en": [
        ("Module 1: Full Alphabet Inventory (Upper & Lower Case)", "Full Alphabet Inventory (Upper & Lower Case)", "A a, B b, C c, D d, E e, F f — Full Letter Inventory", ["A", "B", "C"]),
        ("Module 2: Stroke Order & Letter Formation Rules", "Stroke Order & Letter Formation Rules", "Top-to-bottom and left-to-right stroke formation mechanics", ["Strokes", "Formation"]),
        ("Module 3: Writing Direction Mechanics (Left-to-Right & Line Discipline)", "Writing Direction Mechanics (Left-to-Right)", "Horizontal left-to-right writing direction and baseline alignment", ["Left-to-Right", "Baseline"]),
        ("Module 4: Diacritics & Accent Symbol Conventions", "Diacritics & Accent Symbol Conventions", "Apostrophes, hyphens, accent symbols, and dotting i & j", ["Apostrophe", "Accents"]),
        ("Module 5: Letter Tracing & Copying Practice", "Letter Tracing & Copying Practice", "Tracing and copying practice for letters A, B, C, D, E", ["Tracing", "Copying"]),
        ("Module 6: Writing Personal Name & Core Survival Words", "Writing Personal Name & Core Survival Words", "My name is Alex. Hello, Thank You, Please — Writing", ["My-name", "Survival"])
    ]
}

total_updated = 0

for lang in db.query(models.Language).all():
    code = lang.iso_code
    spec_modules = WRITTEN_CURRICULUM_SPEC.get(code, WRITTEN_CURRICULUM_SPEC["en"])

    written_curr = db.query(models.Curriculum).filter(
        models.Curriculum.lang_id == lang.lang_id,
        (models.Curriculum.title.like("%Written%") | models.Curriculum.title.like("%లేఖన%") | models.Curriculum.title.like("%लिखित%") | models.Curriculum.title.like("%எழுத்து%") | models.Curriculum.title.like("%लेखन%") | models.Curriculum.title.like("%লিখন%") | models.Curriculum.title.like("%ಬರಹ%") | models.Curriculum.title.like("%Escrito%"))
    ).first()

    if not written_curr:
        written_curr = models.Curriculum(
            lang_id=lang.lang_id,
            title=f"{lang.lang_name} - Written Curriculum",
            level="FOUNDATIONAL",
            description=f"Zero level written curriculum for {lang.lang_name}"
        )
        db.add(written_curr)
        db.commit()
        db.refresh(written_curr)

    for idx, (m_name, l_title, target_t, phonetics) in enumerate(spec_modules, start=1):
        mod = db.query(models.Module).filter(
            models.Module.curriculum_id == written_curr.curriculum_id,
            models.Module.sequence_no == idx
        ).first()

        if not mod:
            mod = models.Module(
                curriculum_id=written_curr.curriculum_id,
                module_name=m_name,
                sequence_no=idx,
                skill_type="WRITTEN"
            )
            db.add(mod)
            db.commit()
            db.refresh(mod)
        else:
            mod.module_name = m_name
            mod.skill_type = "WRITTEN"
            db.commit()

        les = db.query(models.Lesson).filter(models.Lesson.module_id == mod.module_id).first()
        if not les:
            les = models.Lesson(
                module_id=mod.module_id,
                title=l_title,
                content_type="Written Practice",
                content_url=f"/audio/{code}/zero_written_seq{idx}.mp3",
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
        total_updated += 1

print("=" * 80)
print(f"SUCCESSFULLY UPDATED {total_updated} ZERO LEVEL WRITTEN MODULES ACROSS ALL 8 LANGUAGES!")
print("=" * 80)
db.close()
