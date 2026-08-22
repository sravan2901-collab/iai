import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("=" * 80)
print("UPDATING ZERO LEVEL SPOKEN CURRICULUM WITH 6 FOUNDATIONAL MODULES ACROSS ALL LANGUAGES")
print("=" * 80)

zero_spoken_modules_template = [
    {
        "seq": 1,
        "title": "Module 1: Sound Inventory (Vowels & Unique Consonants)",
        "desc": "Sound inventory: vowels/consonants that don't exist in your native language.",
        "difficulty": "Zero",
        "lang_data": {
            "en": ("Sound Inventory: Vowels & Unique Consonant Phonemes", "A-ah, B-buh, C-kuh, D-duh, E-eh, Th-sound, Ph-sound", ["A-ah", "B-buh", "Th-sound"]),
            "te": ("శబ్ద నిధి: అచ్చులు మరియు హల్లుల ఉచ్చారణ", "అ, ఆ, ఇ, ఈ, ఉ, ఊ, ఋ, ఎ, ఏ, ఐ, ఒ, ఓ, ఔ", ["అ", "ఆ", "ఇ", "ఈ"]),
            "hi": ("ध्वनि भंडार: स्वर एवं विशिष्ट व्यंजन उच्चारण", "अ, आ, इ, ई, उ, ऊ, ऋ, ए, ऐ, ओ, औ", ["अ", "आ", "इ", "ई"]),
            "ta": ("ஒலி இருப்பு: உயிரெழுத்து மற்றும் மெய்யெழுத்து ஒலிப்பு", "அ, ஆ, இ, ஈ, உ, ஊ, எ, ஏ, ஐ, ஒ, ஓ, ஔ", ["அ", "ஆ", "இ", "ஈ"]),
            "mr": ("ध्वनी भांडार: स्वर व विशिष्ट व्यंजन उच्चार", "अ, आ, इ, ई, उ, ऊ, ऋ, ए, ऐ, ओ, औ", ["अ", "आ", "इ", "ई"]),
            "bn": ("ধ্বনি ভান্ডার: স্বরবর্ণ ও বিশেষ ব্যঞ্জনধ্বনি", "অ, আ, ই, ঈ, উ, ঊ, ঋ, এ, ঐ, ও, ঔ", ["অ", "আ", "ই", "ঈ"]),
            "kn": ("ಧ್ವನಿ ಭಂಡಾರ: ಸ್ವರಗಳು ಮತ್ತು ವ್ಯಂಜನಗಳ ಉಚ್ಚಾರಣೆ", "ಅ, ಆ, ಇ, ಈ, ಉ, ಊ, ಋ, ಎ, ಏ, ಐ, ಒ, ಓ, ಔ", ["ಅ", "ಆ", "ಇ", "ಈ"]),
            "es": ("Inventario de Sonidos: Vocales y Consonantes Únicas", "A, E, I, O, U, R suave, RR fuerte, Ñ sonido", ["Vocales", "Sonido-Ñ"])
        }
    },
    {
        "seq": 2,
        "title": "Module 2: Passive Listening Exposure (Rhythm & Intonation)",
        "desc": "Passive listening exposure (songs, simple dialogues) to absorb rhythm and intonation before producing anything.",
        "difficulty": "Zero",
        "lang_data": {
            "en": ("Passive Listening: Speech Cadence & Rhythm", "Hello friend, how are you today? Welcome to our practice lesson.", ["Hel-lo", "friend", "wel-come"]),
            "te": ("గ్రహణ శ్రవణ సాధన: సంభాషణ స్వర తరంగాలు", "నమస్కారం అండి, మీరు ఎలా ఉన్నారు? ఈ పాఠానికి స్వాగతం.", ["నమస్కారం", "స్వాగతం"]),
            "hi": ("निष्क्रिय श्रवण: भाषण ताल एवं लय", "नमस्ते दोस्त, आप कैसे हैं? इस अभ्यास पाठ में आपका स्वागत है।", ["नमस्ते", "स्वागत"]),
            "ta": ("செயலற்ற கேட்டல்: பேச்சு தாளம் மற்றும் உச்சரிப்பு", "வணக்கம் நண்பரே, நீங்கள் எப்படி இருக்கிறீர்கள்? நல்வரவு.", ["வணக்கம்", "நல்வரவு"]),
            "mr": ("निष्क्रिय श्रवण: संभाषण लय व उच्चार", "नमस्कार मित्रा, तू कसा आहेस? या पाठात तुमचे स्वागत आहे.", ["नमस्कार", "स्वागत"]),
            "bn": ("নিষ্ক্রিয় শোনা: কথার ছন্দ ও লয়", "হ্যালো বন্ধু, কেমন আছেন? আজকের পাঠে আপনাকে স্বাগতম।", ["হ্যালো", "স্বাগতম"]),
            "kn": ("ಪರೋಕ್ಷ ಶ್ರವಣ: ಮಾತಿನ ಲಯ ಮತ್ತು ಶೈಲಿ", "ನಮಸ್ಕಾರ ಸ್ನೇಹಿತರೆ, ಹೇಗಿದ್ದೀರ? ಈ ಪಾಠಕ್ಕೆ ಸ್ವಾಗತ.", ["ನಮಸ್ಕಾರ", "ಸ್ವಾಗತ"]),
            "es": ("Escucha Pasiva: Ritmo e Intonación del Habla", "Hola amigo, ¿cómo estás hoy? Bienvenido a nuestra lección.", ["Ho-la", "Bien-ve-ni-do"])
        }
    },
    {
        "seq": 3,
        "title": "Module 3: Core Survival Phrases (Essential Everyday Words)",
        "desc": "Core survival phrases: hello, goodbye, please, thank you, yes, no, excuse me, sorry.",
        "difficulty": "Zero",
        "lang_data": {
            "en": ("Core Survival Phrases: Daily Courtesy Words", "Hello, Goodbye, Please, Thank You, Yes, No, Excuse Me, Sorry", ["Hel-lo", "Please", "Thank-You"]),
            "te": ("అత్యవసర జీవన వాక్యాలు: రోజువారీ మర్యాద పదాలు", "నమస్కారం, సెలవు, దయచేసి, ధన్యవాదాలు, అవును, కాదు, క్షమించండి", ["నమస్కారం", "ధన్యవాదాలు"]),
            "hi": ("मुख्य उत्तरजीविता वाक्यांश: दैनिक शिष्टाचार शब्द", "नमस्ते, अलविदा, कृपया, धन्यवाद, हाँ, नहीं, माफ कीजिए", ["नमस्ते", "धन्यवाद"]),
            "ta": ("முக்கிய உயிர்வாழ்வு சொற்றொடர்கள்: அன்றாட மரியாதை சொற்கள்", "வணக்கம், போய் வருகிறேன், தயவுசெய்து, நன்றி, ஆம், இல்லை, மன்னிக்கவும்", ["வணக்கம்", "நன்றி"]),
            "mr": ("महत्वाचे दररोजचे शब्द: शिष्टाचार शब्द", "नमस्कार, आजच येतो, कृपया, धन्यवाद, होय, नाही, माफ करा", ["नमस्कार", "धन्यवाद"]),
            "bn": ("জরুরী প্রয়োজনীয় বাক্য: দৈনন্দিন শিষ্টাচার শব্দ", "হ্যালো, বিদায়, দয়া করে, ধন্যবাদ, হ্যাঁ, না, ক্ষমা করবেন", ["হ্যালো", "ধন্যবাদ"]),
            "kn": ("ಅಗತ್ಯ ದೈನಂದಿನ ಪದಗಳು: ಶಿಷ್ಟಾಚಾರದ ಮಾತುಗಳು", "ನಮಸ್ಕಾರ, ಹೋಗಿ ಬರುತ್ತೇನೆ, ದಯವಿಟ್ಟು, ಧನ್ಯವಾದಗಳು, ಹೌದು, ಇಲ್ಲ, ಕ್ಷಮಿಸಿ", ["ನಮಸ್ಕಾರ", "ಧನ್ಯವಾದಗಳು"]),
            "es": ("Frases de Supervivencia: Palabras de Cortesía", "Hola, Adiós, Por favor, Gracias, Sí, No, Disculpe, Lo siento", ["Ho-la", "Gra-cias"])
        }
    },
    {
        "seq": 4,
        "title": "Module 4: Numbers 0 to 10 (Counting Sound Phonemes)",
        "desc": "Numbers 0–10: Pronunciation of essential counting numbers.",
        "difficulty": "Zero",
        "lang_data": {
            "en": ("Numbers 0 to 10 Pronunciation", "Zero, One, Two, Three, Four, Five, Six, Seven, Eight, Nine, Ten", ["Zero", "One", "Two", "Ten"]),
            "te": ("సంఖ్యల ఉచ్చారణ 0 నుండి 10 వరకు", "సున్నా, ఒకటి, రెండు, మూడు, నాలుగు, ఐదు, ఆరు, ఏడు, ఎనిమిది, తొమ్మిది, పది", ["సున్నా", "ఒకటి", "పది"]),
            "hi": ("संख्या उच्चारण 0 से 10 तक", "शून्य, एक, दो, तीन, चार, पांच, छह, सात, आठ, नौ, दस", ["शून्य", "एक", "दस"]),
            "ta": ("எண்கள் 0 முதல் 10 வரை உச்சரிப்பு", "பூஜ்யம், ஒன்று, இரண்டு, மூன்று, நான்கு, ஐந்து, ஆறு, ஏழு, எட்டு, ஒன்பது, பத்து", ["பூஜ்யம்", "ஒன்று"]),
            "mr": ("संख्या उच्चार 0 ते 10", "शून्य, एक, दोन, तीन, चार, पाच, सहा, सात, आठ, नऊ, दहा", ["शून्य", "एक", "दहा"]),
            "bn": ("সংখ্যা উচ্চারণ 0 থেকে 10", "শূন্য, এক, দুই, তিন, চার, পাঁচ, ছয়, সাত, আট, নয়, দশ", ["শূন্য", "এক", "দশ"]),
            "kn": ("ಸಂಖ್ಯೆಗಳ ಉಚ್ಚಾರಣೆ 0 ರಿಂದ 10", "ಸೊನ್ನೆ, ಒಂದು, ಎರಡು, ಮೂರು, ನಾಲ್ಕು, ಐದು, ಆರು, ಏಳು, ಎಂಟು, ಒಂಬತ್ತು, ಹತ್ತು", ["ಸೊನ್ನೆ", "ಒಂದು"]),
            "es": ("Pronunciación de Números del 0 al 10", "Cero, Uno, Dos, Tres, Cuatro, Cinco, Seis, Siete, Ocho, Nueve, Diez", ["Ce-ro", "U-no", "Diez"])
        }
    },
    {
        "seq": 5,
        "title": "Module 5: Fixed Self-Intro Chunks (Identity Expressions)",
        "desc": "One or two fixed self-intro chunks: 'My name is...', 'I am from...'.",
        "difficulty": "Zero",
        "lang_data": {
            "en": ("Fixed Self-Intro Chunks: Name & Origin", "Hello, my name is Alex. I am from New York.", ["My-name-is", "I-am-from"]),
            "te": ("స్వయం పరిచయ వాక్యాలు: పేరు మరియు ప్రాంతం", "నమస్కారం, నా పేరు ఆనంద్. నేను హైదరాబాద్ నుండి వచ్చాను.", ["నా-పేరు", "నేను-వచ్చాను"]),
            "hi": ("आत्म-परिचय वाक्यांश: नाम एवं स्थान", "नमस्ते, मेरा नाम राहुल है। मैं दिल्ली से हूँ।", ["मेरा-नाम-है", "मैं-हूँ"]),
            "ta": ("சுய அறிமுக வாக்கியங்கள்: பெயர் மற்றும் ஊர்", "வணக்கம், என் பெயர் கார்த்திக். நான் சென்னையிலிருந்து வருகிறேன்.", ["என்-பெயர்", "நான்-வருகிறேன்"]),
            "mr": ("स्वतःची ओळख: नाव व गाव", "नमस्कार, माझे नाव समीर आहे. मी मुंबईहून आलो आहे.", ["माझे-नाव", "मी-आलो-आहे"]),
            "bn": ("নিজের পরিচয় বাক্য: নাম ও স্থান", "হ্যালো, আমার নাম অয়ন। আমি কলকাতা থেকে এসেছি।", ["আমার-নাম", "আমি-এসেছি"]),
            "kn": ("ಸ್ವಯಂ ಪರಿಚಯ: ಹೆಸರು ಮತ್ತು ಊರು", "ನಮಸ್ಕಾರ, ನನ್ನ ಹೆಸರು ಸುಹಾಸ್. ನಾನು ಬೆಂಗಳೂರಿನಿಂದ ಬಂದಿದ್ದೇನೆ.", ["ನನ್ನ-ಹೆಸರು", "ಬಂದಿದ್ದೇನೆ"]),
            "es": ("Frases de Auto-Introducción: Nombre u Origen", "Hola, mi nombre es Carlos. Soy de Madrid.", ["Mi-nom-bre-es", "Soy-de"])
        }
    },
    {
        "seq": 6,
        "title": "Module 6: Shadowing Practice (Repeating Audio Clips)",
        "desc": "Shadowing practice — repeating short audio clips to train ear and mouth together for all languages as modules for spoken.",
        "difficulty": "Zero",
        "lang_data": {
            "en": ("Audio Shadowing Practice: Ear & Mouth Coordination", "Repeat after me: I learn language with confidence and clarity.", ["Re-peat", "con-fi-dence"]),
            "te": ("శ్రవణ అనుకరణ సాధన: చెవి మరియు నోటి సమన్వయం", "నా వెంట స్పష్టంగా చెప్పండి: నేను శ్రద్ధగా భాష నేర్చుకుంటున్నాను.", ["స్పష్టంగా", "నేర్చుకుంటున్నాను"]),
            "hi": ("ऑडियो शैडोइंग अभ्यास: कान और मुंह का समन्वय", "मेरे बाद दोहराएं: मैं स्पष्टता के साथ भाषा सीख रहा हूँ।", ["दोहराएं", "स्पष्टता"]),
            "ta": ("ஒலி நிழல் பயிற்சி: காது மற்றும் வாய் பயிற்சி", "என்னுடன் தெளிவுபடுத்தி பேசுங்கள்: நான் நம்பிக்கையுடன் மொழியைக் கற்கிறேன்.", ["தெளிவுபடுத்தి", "கற்கிறேன்"]),
            "mr": ("ऑडिओ शैडोइंग सराव: कान व जिभेचा सराव", "माझ्यामागे स्पष्ट बोला: मी आत्मविश्वासाने भाषा शिकत आहे.", ["स्पष्ट-बोला", "शिकत-आहे"]),
            "bn": ("অডিও শ্যাডোয়িং অনুশীলন: কান ও মুখের সামঞ্জস্য", "আমার পরে বলুন: আমি স্পষ্টতার সাথে ভাষা শিখছি।", ["স্পষ্টতা", "শিখছি"]),
            "kn": ("ಆಡಿಯೋ ಶ್ಯಾಡೋಯಿಂಗ್ ಅಭ್ಯಾಸ: ಕಿವಿ ಮತ್ತು ಬಾಯಿಯ ತರಬೇತಿ", "ನನ್ನ ನಂತರ ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ: ನಾನು ನಂಬಿಕೆಯಿಂದ ಭಾಷೆಯನ್ನು ಕಲಿಯುತ್ತಿದ್ದೇನೆ.", ["ಸ್ಪಷ್ಟವಾಗಿ", "ಕಲಿಯುತ್ತಿದ್ದೇನೆ"]),
            "es": ("Práctica de Shadowing: Entrenamiento Auditivo y Vocal", "Repite conmigo: Aprendo el idioma con claridad y confianza.", ["Re-pi-te", "Cla-ri-dad"])
        }
    }
]

languages = db.query(models.Language).all()
updated_count = 0

for lang in languages:
    code = lang.iso_code
    
    # Find or create Spoken Curriculum
    spoken_curr = db.query(models.Curriculum).filter(
        models.Curriculum.lang_id == lang.lang_id,
        models.Curriculum.title.like("%Spoken%")
    ).first()
    
    if not spoken_curr:
        spoken_curr = models.Curriculum(
            lang_id=lang.lang_id,
            title=f"{lang.lang_name} - Spoken Curriculum",
            level="FOUNDATIONAL",
            description=f"Zero level to advanced spoken language mastery for {lang.lang_name}"
        )
        db.add(spoken_curr)
        db.commit()
        db.refresh(spoken_curr)
        
    for mod_cfg in zero_spoken_modules_template:
        seq = mod_cfg["seq"]
        m_title = mod_cfg["title"]
        m_desc = mod_cfg["desc"]
        
        les_title, target_text, phonetics = mod_cfg["lang_data"].get(code, mod_cfg["lang_data"]["en"])
        
        # Check if module exists for this sequence and curriculum
        existing_mod = db.query(models.Module).filter(
            models.Module.curriculum_id == spoken_curr.curriculum_id,
            models.Module.sequence_no == seq
        ).first()
        
        if not existing_mod:
            existing_mod = models.Module(
                curriculum_id=spoken_curr.curriculum_id,
                module_name=m_title,
                sequence_no=seq,
                skill_type="SPOKEN"
            )
            db.add(existing_mod)
            db.commit()
            db.refresh(existing_mod)
        else:
            existing_mod.module_name = m_title
            existing_mod.skill_type = "SPOKEN"
            db.commit()
            
        # Update or create lesson
        existing_les = db.query(models.Lesson).filter(
            models.Lesson.module_id == existing_mod.module_id
        ).first()
        
        if not existing_les:
            new_les = models.Lesson(
                module_id=existing_mod.module_id,
                title=les_title,
                content_type="Voice Practice",
                content_url=f"/audio/{code}/zero_spoken_seq{seq}.mp3",
                target_text=target_text,
                phonetic_script=str(phonetics),
                difficulty_level="Zero"
            )
            db.add(new_les)
        else:
            existing_les.title = les_title
            existing_les.target_text = target_text
            existing_les.phonetic_script = str(phonetics)
            existing_les.difficulty_level = "Zero"
        
        db.commit()
        updated_count += 1

print(f"SUCCESSFULLY UPDATED {updated_count} ZERO LEVEL SPOKEN MODULES ACROSS ALL 8 LANGUAGES!")
print("=" * 80)
db.close()
