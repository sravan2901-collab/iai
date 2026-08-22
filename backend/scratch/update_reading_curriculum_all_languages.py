import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("=" * 80)
print("UPDATING ZERO LEVEL READING CURRICULUM ACCORDING TO USER SPECIFICATION FOR ALL 8 LANGUAGES")
print("=" * 80)

READING_CURRICULUM_SPEC = {
    # 1. TELUGU
    "te": [
        ("మాడ్యూల్ 1: అక్షర-ధ్వని అనుసంధాన పాఠాలు (ఫోనిక్స్ పఠనం)", "అక్షర-ధ్వని అనుసంధాన పాఠాలు", "అ-అను, ఆ-ఆవు, ఇ-ఇల్లు, ఈ-ఈగ — అక్షర ధ్వని సంబంధం", ["అక్షర", "ధ్వని"]),
        ("మాడ్యూల్ 2: ప్రాథమిక 2-3 అక్షరాల పదాల పఠనావగాహన", "ప్రాథమిక 2-3 అక్షరాల పదాల పఠనం", "అల, ఇల, ఈల, ఉల, అమ, అని, ఇది, అది — పదాల పఠనం", ["అల", "ఇల"]),
        ("మాడ్యూల్ 3: అత్యంత ముఖ్యమైన రోజువారీ సైట్ పదాలు", "అత్యంత ముఖ్యమైన సైట్ పదాల పఠనం", "మరియు, మరియును, ఇది, అది, ఉన్నది, లో, పై — సైట్ పదాలు", ["మరియు", "ఉన్నది"]),
        ("మాడ్యూల్ 4: పద సరిహద్దులు మరియు అక్షర విభజన గుర్తింపు", "పద సరిహద్దులు మరియు అక్షర విభజన", "పదాల మధ్య ఖాళీలు మరియు వాక్య విభజన పఠనం", ["సరిహద్దులు", "విభజన"]),
        ("మాడ్యూల్ 5: చిత్ర-పద అనుసంధాన పఠనం (ప్రాథమిక పాఠాలు)", "చిత్ర-పద అనుసంధాన పఠనం", "ఆవు (🐄), ఇల్లు (🏠), చెట్టు (🌳), పండు (🍎)", ["ఆవు", "ఇల్లు"]),
        ("మాడ్యూల్ 6: సార్వజనిక సూచికలు మరియు బోర్డుల పఠనం (నిష్క్రమణ, ఆగుము, శౌచాలయం, ప్రమాదం)", "సార్వజనిక సూచికలు మరియు బోర్డుల పఠనం", "తెరిచి ఉంది, మూసివేసి ఉంది, నిష్క్రమణ, ఆగుము, శౌచాలయం, ప్రమాదం", ["నిష్క్రమణ", "ప్రమాదం"])
    ],

    # 2. HINDI
    "hi": [
        ("मॉड्यूल 1: वर्ण-ध्वनि संबंध ज्ञान (ध्वनि विज्ञान / फोनिक्स)", "वर्ण-ध्वनि संबंध ज्ञान अभ्यास", "अ-अनार, आ-आम, इ-इमली, ई-ईख — वर्ण ध्वनि संबंध", ["वर्ण", "ध्वनि"]),
        ("मॉड्यूल 2: सरल 2-3 अक्षर वाले शब्दों का पठन", "सरल 2-3 अक्षर वाले शब्दों का पठन", "घर, फल, जल, बस, खत, नल, मन, सब, अब, सच — शब्द पठन", ["घर", "फल"]),
        ("मॉड्यूल 3: उच्च-आवृत्ति वाले मुख्य साइट शब्द (Sight Words)", "उच्च-आवृत्ति मुख्य साइट शब्द पठन", "और, है, यह, वह, में, पर, कि, का, की, के — साइट शब्द", ["और", "है"]),
        ("मॉड्यूल 4: शब्द सीमा एवं पद विभाजन पहचान", "शब्द सीमा एवं पद विभाजन पहचान", "शब्दों के बीच स्थान एवं वाक्य विभाजन पठन अभ्यास", ["सीमा", "विभाजन"]),
        ("मॉड्यूल 5: चित्र-शब्द संबंध पठन (प्रारंभिक बाल पाठक)", "चित्र-शब्द संबंध पठन अभ्यास", "गाय (🐄), घर (🏠), पेड़ (🌳), सेब (🍎)", ["गाय", "घर"]),
        ("मॉड्यूल 6: सामान्य सार्वजनिक संकेत एवं बोर्ड पठन (निकास, रुकिए, शौचालय, खतरा)", "सामान्य सार्वजनिक संकेत एवं बोर्ड पठन", "खुला है, बंद है, निकास, रुकिए, प्रसाधन/शौचालय, खतरा", ["निकास", "खतरा"])
    ],

    # 3. TAMIL
    "ta": [
        ("தொகுதி 1: எழுத்து-ஒலி தொடர்பு (போனிக்ஸ் வாசிப்பு)", "எழுத்து-ஒலி தொடர்பு வாசிப்புப் பயிற்சி", "அ-அம்மா, ஆ-ஆடு, இ-இலை, ஈ-ஈட்டி — ஒலி தொடர்பு", ["எழுத்து", "ஒலி"]),
        ("தொகுதி 2: அடிப்படை 2-3 எழுத்துச் சொற்கள் வாசித்தல்", "அடிப்படை 2-3 எழுத்துச் சொற்கள் வாசித்தல்", "அறம், ஆடை, இலை, ஈட்டி, உடை, அணி, அடி, இது, அது", ["அறம்", "ஆடை"]),
        ("தொகுதி 3: அதிக பயன்பாடுள்ள முக்கிய சொற்கள் (Sight Words)", "அதிக பயன்பாடுள்ள முக்கிய சொற்கள்", "மற்றும், இருக்கிறது, இது, அது, உள்ளே, மேலே", ["மற்றும்", "இருக்கிறது"]),
        ("தொகுதி 4: சொல் எல்லை மற்றும் இடவெளி அடையாளம் காணுதல்", "சொல் எல்லை அடையாளம் காணுதல்", "சொற்களுக்கு இடையே உள்ள இடைவெளி வாசிப்பு", ["எல்லை", "இடைவெளி"]),
        ("தொகுதி 5: படம்-சொல் தொடர்பு வாசிப்பு (ஆரம்ப வாசிப்பு)", "படம்-சொல் தொடர்பு வாசிப்பு", "பசு (🐄), வீடு (🏠), மரம் (🌳), பழம் (🍎)", ["பசு", "வீடு"]),
        ("தொகுதி 6: பொதுப் பலகைகள் மற்றும் குறியீடுகள் வாசித்தல் (வெளியேற்றம், நில்லுங்கள், கழிப்பறை, அபாயம்)", "பொதுப் பலகைகள் வாசித்தல்", "திறக்கப்பட்டுள்ளது, மூடப்பட்டுள்ளது, வெளியேற்றம், நில்லுங்கள், கழிப்பறை, அபாயம்", ["வெளியேற்றம்", "அபாயம்"])
    ],

    # 4. MARATHI
    "mr": [
        ("मॉड्यूल 1: अक्षर-ध्वनी संबंध (फोनिक्स वाचन)", "अक्षर-ध्वनी संबंध वाचन सराव", "अ-अननस, आ-आंबा, इ-इमारत, ई-ईद — ध्वनी संबंध", ["अक्षर", "ध्वनी"]),
        ("मॉड्यूल 2: सोपे 2-3 अक्षरी शब्द वाचन", "सोपे 2-3 अक्षरी शब्द वाचन सराव", "घर, फळ, जल, बस, खत, नळ, मन, सब, कर, कप", ["घर", "फळ"]),
        ("मॉड्यूल 3: वारंवार वापरले जाणारे मुख्य शब्द (Sight Words)", "वारंवार वापरले जाणारे मुख्य शब्द वाचन", "आणि, आहे, हे, ते, मध्ये, वर, की, चा, ची, चे", ["आणि", "आहे"]),
        ("मॉड्यूल 4: शब्द सीमा व अक्षर अंतर ओळख", "शब्द सीमा व अक्षर अंतर ओळख", "शब्दांमधील अंतर व वाक्य विभाजन वाचन सराव", ["सीमा", "अंतर"]),
        ("मॉड्यूल 5: चित्र-शब्द संबंध वाचन (बाल वाचक सराव)", "चित्र-शब्द संबंध वाचन सराव", "गाय (🐄), घर (🏠), झाड (🌳), सफरचंद (🍎)", ["गाय", "घर"]),
        ("मॉड्यूल 6: सार्वजनिक पाट्या व चिन्हे वाचन (बाहेर जाण्याचा मार्ग, थांबा, शौचालय, धोका)", "सार्वजनिक पाट्या व चिन्हे वाचन", "उघडे आहे, बंद आहे, बाहेर जाण्याचा मार्ग, थांबा, शौचालय, धोका", ["मार्ग", "धोका"])
    ],

    # 5. BENGALI
    "bn": [
        ("মডিউল ১: বর্ণ-ধ্বনি সম্পর্ক (ফোনিক্স পঠন)", "বর্ণ-ধ্বনি সম্পর্ক পঠন অনুশীলন", "অ-অজগর, আ-আম, ই-ইঁদুর, ঈ-ঈগল — বর্ণ ধ্বনি সম্পর্ক", ["বর্ণ", "ধ্বনি"]),
        ("মডিউল ২: সহজ ২-৩ অক্ষরের শব্দ পঠন", "সহজ ২-৩ অক্ষরের শব্দ পঠন", "জল, ফল, ঘর, বই, আম, পথ, বন, সব, পথ, মত", ["জল", "ফল"]),
        ("মডিউল ৩: বহুল ব্যবহৃত প্রধান শব্দ (Sight Words)", "বহুল ব্যবহৃত প্রধান শব্দ পঠন", "এবং, হয়, এটি, ওটি, মধ্যে, উপরে, এর, তার", ["এবং", "হয়"]),
        ("মডিউল ৪: শব্দ সীমানা ও ব্যবধান চেনা", "শব্দ সীমানা ও ব্যবধান চেনা", "শব্দের মাঝের ব্যবধান ও বাক্য বিভাজন পঠন", ["সীমানা", "ব্যবধান"]),
        ("মডিউল ৫: ছবি-শব্দ মেলানো পঠন (প্রাথমিক পাঠক)", "ছবি-শব্দ মেলানো পঠন অনুশীলন", "গরু (🐄), ঘর (🏠), গাছ (🌳), আপেল (🍎)", ["গরু", "ঘর"]),
        ("মডিউল ৬: সাধারণ সাইনবোর্ড ও চিহ্ন পঠন (প্রস্থান, থামুন, শৌচাগার, বিপদ)", "সাধারণ সাইনবোর্ড ও চিহ্ন পঠন", "খোলা আছে, বন্ধ আছে, প্রস্থান, থামুন, শৌচাগার, বিপদ", ["প্রস্থান", "বিপদ"])
    ],

    # 6. KANNADA
    "kn": [
        ("ಮಾಡ್ಯೂಲ್ 1: ಅಕ್ಷರ-ಧ್ವನಿ ನಂಟಿನ ಓದುವಿಕೆ (ಫೋನಿಕ್ಸ್)", "ಅಕ್ಷರ-ಧ್ವನಿ ನಂಟಿನ ಓದುವಿಕೆ ಅಭ್ಯಾಸ", "ಅ-ಅರಮನೆ, ಆ-ಆನೆ, ಇ-ಇಲಿ, ಈ-ಈಜುವುದು — ಧ್ವನಿ ನಂಟು", ["ಅಕ್ಷರ", "ಧ್ವನಿ"]),
        ("ಮಾಡ್ಯೂಲ್ 2: ಸರಳ 2-3 ಅಕ್ಷರಗಳ ಪದಗಳ ಓದುವಿಕೆ", "ಸರಳ 2-3 ಅಕ್ಷರಗಳ ಪದಗಳ ಓದುವಿಕೆ", "ಮರ, ಮನೆ, ಹಾಲು, ಕಾಡು, ನದಿ, ಜಲ, ಹಣ್ಣು, ಬಸ್", ["ಮರ", "ಮನೆ"]),
        ("ಮಾಡ್ಯೂಲ್ 3: ಹೆಚ್ಚು ಬಳಕೆಯಾಗುವ ಪ್ರಮುಖ ಸೈಟ್ ಪದಗಳು (Sight Words)", "ಪ್ರಮುಖ ಸೈಟ್ ಪದಗಳ ಓದುವಿಕೆ", "ಮತ್ತು, ಇದೆ, ಇದು, ಅದು, ಒಳಗೆ, ಮೇಲೆ, ರ, ನ", ["ಮತ್ತು", "ಇದೆ"]),
        ("ಮಾಡ್ಯೂಲ್ 4: ಪದ ಗಡಿ ಮತ್ತು ಸಾಲು ವ್ಯತ್ಯಾಸ ಗುರುತಿಸುವಿಕೆ", "ಪದ ಗಡಿ ಮತ್ತು ಸಾಲು ವ್ಯತ್ಯಾಸ ಗುರುತಿಸುವಿಕೆ", "ಪದಗಳ ನಡುವಿನ ಅಂತರ ಮತ್ತು ವಾಕ್ಯ ವಿಂಗಡಣೆ ಓದುವಿಕೆ", ["ಗಡಿ", "ಅಂತರ"]),
        ("ಮಾಡ್ಯೂಲ್ 5: ಚಿತ್ರ-ಪದ ನಂಟಿನ ಓದುವಿಕೆ (ಆರಂಭಿಕ ವಾಚಕ)", "ಚಿತ್ರ-ಪದ ನಂಟಿನ ಓದುವಿಕೆ ಅಭ್ಯಾಸ", "ಸೌತೆ (🐄), ಮನೆ (🏠), ಮರ (🌳), ಸೇಬು (🍎)", ["ಮನೆ", "ಮರ"]),
        ("ಮಾಡ್ಯೂಲ್ 6: ಸಾರ್ವಜನಿಕ ಸೂಚನಾ ಫಲಕಗಳ ಓದುವಿಕೆ (ನಿರ್ಗಮನ, ನಿಲ್ಲಿಸಿ, ಶೌಚಾಲಯ, ಅಪಾಯ)", "ಸಾರ್ವಜನಿಕ ಸೂಚನಾ ಫಲಕಗಳ ಓದುವಿಕೆ", "ತೆರೆದಿದೆ, ಮುಚ್ಚಲ್ಪಟ್ಟಿದೆ, ನಿರ್ಗಮನ, ನಿಲ್ಲಿಸಿ, ಶೌಚಾಲಯ, ಅಪಾಯ", ["ನಿರ್ಗಮನ", "ಅಪಾಯ"])
    ],

    # 7. SPANISH
    "es": [
        ("Módulo 1: Correspondencia Letra-Sonido (Fónica Básica)", "Correspondencia Letra-Sonido y Fónica", "A-Auto, B-Barco, C-Casa, D-Dado, E-Elefante — Fónica", ["Fónica", "Sonido"]),
        ("Módulo 2: Decodificación de Palabras Simples de 2-3 Letras", "Decodificación de Palabras Simples", "Sol, Pan, Mar, Luz, Sal, Dos, Ver, Ir, Un, No", ["Sol", "Pan"]),
        ("Módulo 3: Palabras de Alta Frecuencia (Sight Words)", "Palabras de Alta Frecuencia", "El, La, Los, Las, Es, Y, En, Por, Con, Para", ["Sight-Words", "El-La"]),
        ("Módulo 4: Reconocimiento de Límites de Palabras y Espacios", "Reconocimiento de Límites y Espacios", "Reconocimiento de espacios entre palabras en oraciones", ["Límites", "Espacios"]),
        ("Módulo 5: Asociación de Imagen y Palabra (Lectura Temprana)", "Asociación de Imagen y Palabra", "Vaca (🐄), Casa (🏠), Árbol (🌳), Manzana (🍎)", ["Imagen", "Palabra"]),
        ("Módulo 6: Señales y Símbolos Comunes (Salida, Pare, Baños, Peligro)", "Señales y Símbolos Comunes", "Abierto, Cerrado, Salida, Pare / Alto, Baños / Sanitarios, Peligro", ["Salida", "Peligro"])
    ],

    # 8. ENGLISH
    "en": [
        ("Module 1: Letter–Sound Correspondence (Phonics Rules)", "Letter–Sound Correspondence (Phonics)", "A-Apple, B-Ball, C-Cat, D-Dog, E-Elephant — Phonics", ["Letter-Sound", "Phonics"]),
        ("Module 2: Decoding Simple 2–3 Letter Words", "Decoding Simple 2–3 Letter Words", "Cat, Dog, Sun, Pen, Cup, Bus, Red, Hat, Sit, Run", ["Cat", "Dog"]),
        ("Module 3: 10–20 High-Frequency Sight Words (\"the\", \"is\", \"and\")", "High-Frequency Sight Words", "The, Is, And, In, On, It, To, You, That, Was, For, Are", ["Sight-Words", "The-Is"]),
        ("Module 4: Word-Boundary & Script Space Recognition", "Word-Boundary & Script Space Recognition", "Identifying spaces between words and sentence punctuation boundaries", ["Boundary", "Spaces"]),
        ("Module 5: Picture-Word Association (Early Reader Material)", "Picture-Word Association", "Cow (🐄), House (🏠), Tree (🌳), Apple (🍎)", ["Picture-Word", "Cow"]),
        ("Module 6: Common Public Signage & Symbols (Exit, Stop, Restroom, Danger)", "Common Public Signage & Symbols", "Open, Closed, Exit, Stop, Restroom, Danger / Caution", ["Signage", "Danger"])
    ]
}

total_updated = 0

for lang in db.query(models.Language).all():
    code = lang.iso_code
    spec_modules = READING_CURRICULUM_SPEC.get(code, READING_CURRICULUM_SPEC["en"])

    reading_curr = db.query(models.Curriculum).filter(
        models.Curriculum.lang_id == lang.lang_id,
        (models.Curriculum.title.like("%Reading%") | models.Curriculum.title.like("%పఠన%") | models.Curriculum.title.like("%पठन%") | models.Curriculum.title.like("%வாசிப்பு%") | models.Curriculum.title.like("%वाचन%") | models.Curriculum.title.like("%পঠন%") | models.Curriculum.title.like("%ಓದುವ%") | models.Curriculum.title.like("%Lectura%"))
    ).first()

    if not reading_curr:
        reading_curr = models.Curriculum(
            lang_id=lang.lang_id,
            title=f"{lang.lang_name} - Reading Curriculum",
            level="FOUNDATIONAL",
            description=f"Zero level reading curriculum for {lang.lang_name}"
        )
        db.add(reading_curr)
        db.commit()
        db.refresh(reading_curr)

    for idx, (m_name, l_title, target_t, phonetics) in enumerate(spec_modules, start=1):
        mod = db.query(models.Module).filter(
            models.Module.curriculum_id == reading_curr.curriculum_id,
            models.Module.sequence_no == idx
        ).first()

        if not mod:
            mod = models.Module(
                curriculum_id=reading_curr.curriculum_id,
                module_name=m_name,
                sequence_no=idx,
                skill_type="READING"
            )
            db.add(mod)
            db.commit()
            db.refresh(mod)
        else:
            mod.module_name = m_name
            mod.skill_type = "READING"
            db.commit()

        les = db.query(models.Lesson).filter(models.Lesson.module_id == mod.module_id).first()
        if not les:
            les = models.Lesson(
                module_id=mod.module_id,
                title=l_title,
                content_type="Functional Reading",
                content_url=f"/audio/{code}/zero_reading_seq{idx}.mp3",
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
print(f"SUCCESSFULLY UPDATED {total_updated} ZERO LEVEL READING MODULES ACROSS ALL 8 LANGUAGES!")
print("=" * 80)
db.close()
