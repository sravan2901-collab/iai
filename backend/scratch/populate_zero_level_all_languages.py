import sys
import os
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal
from app import models

db = SessionLocal()

print("=" * 80)
print("POPULATING ZERO LEVEL MODULES (18 TOTAL) ACROSS ALL 3 CURRICULUMS FOR ALL 8 LANGUAGES")
print("=" * 80)

# Clear old curriculum structure
db.query(models.PathLesson).delete()
db.query(models.LearningPath).delete()
db.query(models.Lesson).delete()
db.query(models.Module).delete()
db.query(models.Curriculum).delete()
db.commit()

languages = db.query(models.Language).all()

zero_curriculum_templates = {
    "SPOKEN": {
        "title": "Spoken Curriculum",
        "desc": "Zero level foundational oral communication, listening, phonetics, and speech shadowing.",
        "content_type": "Voice Practice",
        "modules": [
            {
                "seq": 1,
                "title": "Zero Module 1: Sound Inventory (Vowels & Unique Consonants)",
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
                "title": "Zero Module 2: Passive Listening Exposure (Rhythm & Intonation)",
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
                "title": "Zero Module 3: Core Survival Phrases (Hello, Goodbye, Please, Thank You, Yes, No, Excuse Me, Sorry)",
                "lang_data": {
                    "en": ("Core Survival Phrases: Daily Courtesy Words", "Hello, Goodbye, Please, Thank You, Yes, No, Excuse Me, Sorry", ["Hel-lo", "Please", "Thank-You"]),
                    "te": ("అత్యవసర జీవన వాక్యాలు: రోజువారీ మర్యాద పదాలు", "నమస్కారం, సెలవు, దయచేసి, ధన్యవాదాలు, అవును, కాదు, క్షమించండి", ["నమస్కారం", "ధన్యవాదాలు"]),
                    "hi": ("मुख्य उत्तरजीविता वाक्यांश: दैनिक शिष्टाचार शब्द", "नमस्ते, अलविदा, कृपया, धन्यवाद, हाँ, नहीं, माफ कीजिए", ["नमस्ते", "धन्यवाद"]),
                    "ta": ("முக்கிய உயிர்வாழ்வு சொற்றொடர்கள்: அன்றாட மரியாதை சொற்கள்", "வணக்கம், போய் வருகிறேன், தயவுசெய்து, நன்றி, ஆம், இல்லை, மன்னிக்கவும்", ["வணக்கம்", "நன்றி"]),
                    "mr": ("महत्वाचे दररोजचे शब्द: शिष्टाचार शब्द", "नमस्कार, आजच करतो, कृपया, धन्यवाद, होय, नाही, माफ करा", ["नमस्कार", "धन्यवाद"]),
                    "bn": ("জরুরী প্রয়োজনীয় বাক্য: দৈনন্দিন শিষ্টাচার শব্দ", "হ্যালো, বিদায়, দয়া করে, ধন্যবাদ, হ্যাঁ, না, ক্ষমা করবেন", ["হ্যালো", "ধন্যবাদ"]),
                    "kn": ("ಅಗತ್ಯ ದೈನಂದಿನ ಪದಗಳು: ಶಿಷ್ಟಾಚಾರದ ಮಾತುಗಳು", "ನಮಸ್ಕಾರ, ಹೋಗಿ ಬರುತ್ತೇನೆ, ದಯವಿಟ್ಟು, ಧನ್ಯವಾದಗಳು, ಹೌದು, ಇಲ್ಲ, ಕ್ಷಮಿಸಿ", ["ನಮಸ್ಕಾರ", "ಧನ್ಯವಾದಗಳು"]),
                    "es": ("Frases de Supervivencia: Palabras de Cortesía", "Hola, Adiós, Por favor, Gracias, Sí, No, Disculpe, Lo siento", ["Ho-la", "Gra-cias"])
                }
            },
            {
                "seq": 4,
                "title": "Zero Module 4: Numbers 0 to 10 (Counting Sound Phonemes)",
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
                "title": "Zero Module 5: Fixed Self-Intro Chunks ('My name is...', 'I am from...')",
                "lang_data": {
                    "en": ("Fixed Self-Intro Chunks: Name & Origin", "Hello, my name is Alex. I am from New York.", ["My-name-is", "I-am-from"]),
                    "te": ("స్వయం పరిచయ వాక్యాలు: పేరు మరియు ప్రాంతం", "నమస్కారం, నా పేరు ఆనంద్. నేను హైదరాబాద్ నుండి వచ్చాను.", ["నా-పేరు", "నేను-వచ్చాను"]),
                    "hi": ("आत्म-परिचय वाक्यांश: नाम एवं स्थान", "नमस्ते, मेरा नाम राहुल है। मैं दिल्ली से हूँ।", ["मेरा-नाम-है", "मैं-हूँ"]),
                    "ta": ("சுய அறிமுக வாக்கியங்கள்: பெயர் மற்றும் ஊர்", "வணக்கம், என் பெயர் கார்த்திக். நான் சென்னையிலிருந்து வருகிறேன்.", ["என்-பெயர்", "நான்-வருகிறேன்"]),
                    "mr": ("स्वतःची ओळख: नाव व गाव", "नमस्कार, माझे नाव समीर आहे. मी मुंबईहून आलो आहे.", ["माझे-नाव", "मी-आलो-आहे"]),
                    "bn": ("নিজের পরিচয় বাক্য: নাম ও স্থান", "হ্যালো, আমার নাম অয়ন। আমি কলকাতা থেকে এসেছি।", ["আমার-नाम", "আমি-এসেছি"]),
                    "kn": ("ಸ್ವಯಂ ಪರಿಚಯ: ಹೆಸರು ಮತ್ತು ಊರು", "ನಮಸ್ಕಾರ, ನನ್ನ ಹೆಸರು ಸುಹಾಸ್. ನಾನು ಬೆಂಗಳೂರಿನಿಂದ ಬಂದಿದ್ದೇನೆ.", ["ನನ್ನ-ಹೆಸರು", "ಬಂದಿದ್ದೇನೆ"]),
                    "es": ("Frases de Auto-Introducción: Nombre u Origen", "Hola, mi nombre es Carlos. Soy de Madrid.", ["Mi-nom-bre-es", "Soy-de"])
                }
            },
            {
                "seq": 6,
                "title": "Zero Module 6: Audio Shadowing Practice (Repeating Audio Clips)",
                "lang_data": {
                    "en": ("Audio Shadowing Practice: Ear & Mouth Coordination", "Repeat after me: I learn language with confidence and clarity.", ["Re-peat", "con-fi-dence"]),
                    "te": ("శ్రవణ అనుకరణ సాధన: చెవి మరియు నోటి సమన్వయం", "నా వెంట స్పష్టంగా చెప్పండి: నేను శ్రద్ధగా భాష నేర్చుకుంటున్నాను.", ["స్పష్టంగా", "నేర్చుకుంటున్నాను"]),
                    "hi": ("ऑडियो शैडोइंग अभ्यास: कान और मुंह का समन्वय", "मेरे बाद दोहराएं: मैं स्पष्टता के साथ भाषा सीख रहा हूँ।", ["दोहराएं", "स्पष्टता"]),
                    "ta": ("ஒலி நிழல் பயிற்சி: காது மற்றும் வாய் பயிற்சி", "என்னுடன் தெளிவுபடுத்தி பேசுங்கள்: நான் நம்பிக்கையுடன் மொழியைக் கற்கிறேன்.", ["தெளிவுபடுத்தி", "கற்கிறேன்"]),
                    "mr": ("ऑडिओ शैडोइंग सराव: कान व जिभेचा सराव", "माझ्यामागे स्पष्ट बोला: मी आत्मविश्वासाने भाषा शिकत आहे.", ["स्पष्ट-बोला", "शिकत-आहे"]),
                    "bn": ("অডিও শ্যাডোয়িং অনুশীলন: কান ও মুখের সামঞ্জস্য", "আমার পরে বলুন: আমি স্পষ্টতার সাথে ভাষা শিখছি।", ["স্পষ্টতা", "শিখছি"]),
                    "kn": ("ಆಡಿಯೋ ಶ್ಯಾಡೋಯಿಂಗ್ ಅಭ್ಯಾಸ: ಕಿವಿ ಮತ್ತು ಬಾಯಿಯ ತರಬೇತಿ", "ನನ್ನ ನಂತರ ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ: ನಾನು ನಂಬಿಕೆಯಿಂದ ಭಾಷೆಯನ್ನು ಕಲಿಯುತ್ತಿದ್ದೇನೆ.", ["ಸ್ಪಷ್ಟವಾಗಿ", "ಕಲಿಯುತ್ತಿದ್ದೇನೆ"]),
                    "es": ("Práctica de Shadowing: Entrenamiento Auditivo y Vocal", "Repite conmigo: Aprendo el idioma con claridad y confianza.", ["Re-pi-te", "Cla-ri-dad"])
                }
            }
        ]
    },
    "WRITTEN": {
        "title": "Written Curriculum",
        "desc": "Zero level foundational script formation, vowel mark writing, numbers, and basic sentence spelling.",
        "content_type": "Written Practice",
        "modules": [
            {
                "seq": 1,
                "title": "Zero Module 1: Script Strokes & Letter Shapes",
                "lang_data": {
                    "en": ("Script Strokes: Basic Alphabet Formation", "A, B, C, D, E — Basic Letter Strokes", ["A", "B", "C", "D", "E"]),
                    "te": ("అక్షర నిర్మాణం: ప్రాథమిక అక్షర లేఖన సాధన", "అ, ఆ, ఇ, ఈ, ఉ — ప్రాథమిక అక్షర లేఖనం", ["అ", "ఆ", "ఇ", "ఈ"]),
                    "hi": ("वर्णमाला लेखन: प्राथमिक वर्ण गठन", "अ, आ, इ, ई, उ — वर्णमाला लेखन अभ्यास", ["अ", "आ", "इ", "ई"]),
                    "ta": ("எழுத்து உருவாக்கம்: அடிப்படை எழுத்து பயிற்சி", "அ, ஆ, இ, ஈ, உ — அடிப்படை எழுத்து பயிற்சி", ["அ", "ஆ", "இ", "ஈ"]),
                    "mr": ("अक्षर लेखन: प्राथमिक अक्षर सराव", "अ, आ, इ, ई, उ — वर्णमाला लेखन सराव", ["अ", "आ", "इ", "ई"]),
                    "bn": ("বর্ণমালা লিখন: প্রাথমিক বর্ণ গঠন", "অ, আ, ই, ঈ, উ — বর্ণমালা লিখন অনুশীলন", ["অ", "আ", "ই", "ঈ"]),
                    "kn": ("ಅಕ್ಷರ ರಚನೆ: ಪ್ರಾಥಮಿಕ ಅಕ್ಷರ ಬರವಣಿಗೆ", "ಅ, ಆ, ಇ, ಈ, ಉ — ಅಕ್ಷರ ಬರವಣಿಗೆ ಅಭ್ಯಾಸ", ["ಅ", "ಆ", "ಇ", "ಈ"]),
                    "es": ("Trazos de Escritura: Formación de Letras", "A, B, C, D, E — Formación de Letras", ["Tra-zos", "Le-tras"])
                }
            },
            {
                "seq": 2,
                "title": "Zero Module 2: Vowel Marks & Accent Symbols",
                "lang_data": {
                    "en": ("Vowel Marks & Accent Spelling", "Am, An, As, At — Vowel Mark Spelling", ["Am", "An", "As", "At"]),
                    "te": ("గుణింత గుర్తులు మరియు స్వర లేఖనం", "తలకట్టు, దీర్ఘం, గుడి, గుడిదీర్ఘం — గుణింత గుర్తులు", ["తలకట్టు", "దీర్ఘం"]),
                    "hi": ("मात्रा लेखन एवं स्वर प्रतीक", "आ की मात्रा, इ की मात्रा, ई की मात्रा — मात्रा लेखन", ["मात्रा", "लेखन"]),
                    "ta": ("உயிரெழுத்து குறியீடுகள் மற்றும் எழுத்துக்கூட்டுதல்", "அகரம், ஆகாரம், இகரம் — குறியீடுகள்", ["குறியீடுகள்"]),
                    "mr": ("मात्रा लेखन व स्वर चिन्हे", "आ ची मात्रा, इ ची मात्रा, ई ची मात्रा — मात्रा सराव", ["मात्रा", "सराव"]),
                    "bn": ("কার চিহ্ন ও স্বরপ্রতীক লিখন", "আ-কার, ই-কার, ঈ-কার — কার চিহ্ন লিখন", ["কার-চিহ্ন"]),
                    "kn": ("ಗುಣಿತಾಕ್ಷರ ಚಿಹ್ನೆಗಳು ಮತ್ತು ಸ್ವರ ಬರವಣಿಗೆ", "ತಲಕಟ್ಟು, ದೀರ್ಘ, ಗುಡಿಸು, ಗುಡಿಸಿನ ದೀರ್ಘ", ["ಗುಣಿತಾಕ್ಷರ"]),
                    "es": ("Marcas de Vocales y Símbolos de Acentuación", "Am, An, As, At — Ortografía de Vocales", ["Vo-ca-les", "A-cen-tos"])
                }
            },
            {
                "seq": 3,
                "title": "Zero Module 3: 2-Letter Syllable Combinations",
                "lang_data": {
                    "en": ("2-Letter Syllable Word Writing", "In, On, It, To, Up, Go — Syllable Combinations", ["In", "On", "It", "To"]),
                    "te": ("ద్వియక్షర పదాల రాత సాధన", "అమ, అని, ఇది, అది, ఇటు, అటు — పదాల రాత సాధన", ["అమ", "అని", "ఇది"]),
                    "hi": ("दो अक्षर शब्द लेखन", "अब, सब, कब, जब, मत, चल — दो अक्षर शब्द", ["अब", "सब", "कब"]),
                    "ta": ("இரண்டெழுத்து சொற்கள் எழுதுதல்", "அல், கல், சொல், புல், வில் — சொற்கள்", ["அல்", "கல்"]),
                    "mr": ("दोन अक्षरी शब्द लेखन", "कर, चल, घर, बस, मन, वर — शब्द सराव", ["कर", "चल"]),
                    "bn": ("দুই অক্ষরের শব্দ লিখন", "আম, বন, জল, পথ, ফল, মত — শব্দ লিখন", ["আম", "বন"]),
                    "kn": ("ಎರಡಕ್ಷರ ಪದಗಳ ಬರವಣಿಗೆ", "ಅರ, ಇಲಿ, ಊಟ, ಎಲೆ, ಒಲೆ — ಪದ ಬರವಣಿಗೆ", ["ಅರ", "ಇಲಿ"]),
                    "es": ("Escritura de Palabras de 2 Letras", "En, Un, Su, Tu, Mi, Ir — Palabras Cortas", ["En", "Un", "Su"])
                }
            },
            {
                "seq": 4,
                "title": "Zero Module 4: Writing Numbers 0 to 10",
                "lang_data": {
                    "en": ("Writing Number Digits 0 to 10", "0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 — Digits", ["Zero", "One", "Ten"]),
                    "te": ("సంఖ్యల రాత సాధన 0 నుండి 10 వరకు", "౯, ౧, ౨, ౩, ౪, ౫, ౬, ౭, ౮, ౯, ౧౦ — సంఖ్యలు", ["సున్నా", "పది"]),
                    "hi": ("संख्या अंक लेखन 0 से 10", "०, १, २, ३, ४, ५, ६, ७, ८, ९, १० — संख्या लेखन", ["शून्य", "दस"]),
                    "ta": ("எண்கள் எழுதுதல் 0 முதல் 10 வரை", "0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 — எண்கள்", ["பூஜ்யம்", "பத்து"]),
                    "mr": ("अंक लेखन 0 ते 10", "०, १, २, ३, ४, ५, ६, ७, ८, ९, १० — अंक सराव", ["शून्य", "दहा"]),
                    "bn": ("সংখ্যা অঙ্ক লিখন 0 থেকে 10", "০, ১, ২, ৩, ৪, ৫, ৬, ৭, ৮, ৯, ১০ — সংখ্যা লিখন", ["শূন্য", "দশ"]),
                    "kn": ("ಸಂಖ್ಯೆಗಳ ಬರವಣಿಗೆ 0 ರಿಂದ 10", "೦, ೧, ೨, ೩, ೪, ೫, ೬, ೭, ೮, ೯, ೧೦ — ಸಂಖ್ಯೆಗಳು", ["ಸೊನ್ನೆ", "ಹತ್ತು"]),
                    "es": ("Escritura de Números del 0 al 10", "0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 — Dígitos", ["Ce-ro", "Diez"])
                }
            },
            {
                "seq": 5,
                "title": "Zero Module 5: Writing Survival Courtesy Words",
                "lang_data": {
                    "en": ("Writing Core Survival Words", "Hello, Thank You, Yes, No — Survival Spelling", ["Hel-lo", "Thank-You"]),
                    "te": ("ముఖ్య మర్యాద పదాల రాత సాధన", "నమస్కారం, ధన్యవాదాలు, అవును, కాదు — రాయడం", ["నమస్కారం", "ధన్యవాదాలు"]),
                    "hi": ("दैनिक शिष्टाचार शब्द लेखन", "नमस्ते, धन्यवाद, हाँ, नहीं — उत्तरजीविता शब्द", ["नमस्ते", "धन्यवाद"]),
                    "ta": ("முக்கிய மரியாதை சொற்கள் எழுதுதல்", "வணக்கம், நன்றி, ஆம், இல்லை — சொற்கள்", ["வணக்கம்", "நன்றி"]),
                    "mr": ("शिष्टाचार शब्द लेखन सराव", "नमस्कार, धन्यवाद, होय, नाही — शब्द सराव", ["नमस्कार", "धन्यवाद"]),
                    "bn": ("জরুরী শিষ্টাচার শব্দ লিখন", "হ্যালো, ধন্যবাদ, হ্যাঁ, না — শব্দ লিখন", ["হ্যালো", "ধন্যবাদ"]),
                    "kn": ("ಅಗತ್ಯ ಶಿಷ್ಟಾಚಾರದ ಪದಗಳ ಬರವಣಿಗೆ", "ನಮಸ್ಕಾರ, ಧನ್ಯವಾದಗಳು, ಹೌದು, ಇಲ್ಲ — ಬರವಣಿಗೆ", ["ನಮಸ್ಕಾರ", "ಧನ್ಯವಾದಗಳು"]),
                    "es": ("Escritura de Palabras de Cortesía", "Hola, Gracias, Sí, No — Ortografía Esencial", ["Ho-la", "Gra-cias"])
                }
            },
            {
                "seq": 6,
                "title": "Zero Module 6: Writing Fixed Self-Intro Sentence",
                "lang_data": {
                    "en": ("Writing Self-Intro Sentence", "My name is Alex. I am from New York.", ["My-name-is", "I-am-from"]),
                    "te": ("స్వయం పరిచయ వాక్యం రాయడం", "నా పేరు ఆనంద్. నేను హైదరాబాద్ నుండి వచ్చాను.", ["నా-పేరు", "వచ్చాను"]),
                    "hi": ("आत्म-परिचय वाक्य लेखन", "मेरा नाम राहुल है। मैं दिल्ली से हूँ।", ["मेरा-नाम", "मैं-हूँ"]),
                    "ta": ("சுய அறிமுக வாக்கியம் எழுதுதல்", "என் பெயர் கார்த்திக். நான் சென்னையிலிருந்து வருகிறேன்.", ["என்-பெயர்", "வருகிறேன்"]),
                    "mr": ("स्वतःचे नाव व गाव लिहिणे", "माझे नाव समीर आहे. मी मुंबईहून आलो आहे.", ["माझे-नाव", "आलो-आहे"]),
                    "bn": ("নিজের পরিচয় বাক্য লিখন", "আমার নাম অয়ন। আমি কলকাতা থেকে এসেছি।", ["আমার-নাম", "এসেছি"]),
                    "kn": ("ಸ್ವಯ ಪರಿಚಯ ವಾಕ್ಯ ಬರವಣಿಗೆ", "ನನ್ನ ಹೆಸರು ಸುಹಾಸ್. ನಾನು ಬೆಂಗಳೂರಿನಿಂದ ಬಂದಿದ್ದೇನೆ.", ["ನನ್ನ-ಹೆಸರು", "ಬಂದಿದ್ದೇನೆ"]),
                    "es": ("Escritura de Frases de Presentación", "Mi nombre es Carlos. Soy de Madrid.", ["Mi-nom-bre", "Soy-de"])
                }
            }
        ]
    },
    "READING": {
        "title": "Reading Curriculum",
        "desc": "Zero level foundational visual letter recognition, sight reading, number signs, and daily labels.",
        "content_type": "Functional Reading",
        "modules": [
            {
                "seq": 1,
                "title": "Zero Module 1: Visual Alphabet & Symbol Recognition",
                "lang_data": {
                    "en": ("Visual Alphabet & Symbol Recognition", "A, B, C, D, E, F — Visual Letter Recognition", ["A", "B", "C", "D", "E"]),
                    "te": ("అక్షర రూప గుర్తింపు సాధన", "అ, ఆ, ఇ, ఈ, ఉ, ఊ — అక్షరాల గుర్తింపు", ["అ", "ఆ", "ఇ", "ఈ"]),
                    "hi": ("दृश्य वर्ण पहचान अभ्यास", "अ, आ, इ, ई, उ, ऊ — वर्ण पहचान", ["अ", "आ", "इ", "ई"]),
                    "ta": ("எழுத்து வடிவம் அறிதல் பயிற்சி", "அ, ஆ, இ, ஈ, உ, ஊ — எழுத்து அறிதல்", ["அ", "ஆ", "இ", "ஈ"]),
                    "mr": ("दृश्य वर्ण ओळख सराव", "अ, आ, इ, ई, उ, ऊ — वर्ण ओळख", ["अ", "आ", "इ", "ई"]),
                    "bn": ("দৃশ্য বর্ণ চেনার অনুশীলন", "অ, আ, ই, ঈ, উ, ঊ — বর্ণ চেনা", ["অ", "আ", "ই", "ঈ"]),
                    "kn": ("ದೃಶ್ಯ ಅಕ್ಷರ ಗುರುತಿಸುವಿಕೆ ಅಭ್ಯಾಸ", "ಅ, ಆ, ಇ, ಈ, ಉ, ಊ — ಅಕ್ಷರ ಗುರುತು", ["ಅ", "ಆ", "ಇ", "ಈ"]),
                    "es": ("Reconocimiento Visual de Letras y Símbolos", "A, B, C, D, E, F — Reconocimiento Visual", ["Let-ras", "Sím-bo-los"])
                }
            },
            {
                "seq": 2,
                "title": "Zero Module 2: Vowel Sound Sight Reading",
                "lang_data": {
                    "en": ("Vowel Sound & Syllable Sight Reading", "Ba, Ca, Da, Fa, Ga — Sight Reading", ["Ba", "Ca", "Da", "Fa"]),
                    "te": ("గుణింత రూపాల పఠనావగాహన", "క, కా, కి, కీ, కు, కూ — గుణింత పఠనం", ["క", "కా", "కి"]),
                    "hi": ("मात्रा रूप पठन अभ्यास", "क, का, कि, की, कु, कू — मात्रा पठन", ["क", "का", "कि"]),
                    "ta": ("உயிரெழுத்து வடிவ வாசிப்பு", "க, கா, கி, கீ, கு, கூ — வாசிப்பு", ["க", "கா", "கி"]),
                    "mr": ("मात्रा रूप वाचन सराव", "क, का, कि, की, कु, कू — वाचन सराव", ["क", "का", "कि"]),
                    "bn": ("কার চিহ্ন রূপ পাঠ অনুশীলন", "ক, কা, কি, কী, কু, কূ — কার পাঠ", ["ক", "কা", "কি"]),
                    "kn": ("ಗುಣಿತಾಕ್ಷರ ರೂಪಗಳ ವಾಚನ ಅಭ್ಯಾಸ", "ಕ, ಕಾ, ಕಿ, ಕೀ, ಕು, ಕೂ — ಗುಣಿತಾಕ್ಷರ", ["ಕ", "ಕಾ", "ಕಿ"]),
                    "es": ("Lectura a Primera Vista de Vocales y Sílabas", "Ba, Ca, Da, Fa, Ga — Lectura Rápida", ["Sí-la-bas", "Lec-tu-ra"])
                }
            },
            {
                "seq": 3,
                "title": "Zero Module 3: 2-Letter Sight Word Reading",
                "lang_data": {
                    "en": ("2-Letter Sight Word Reading", "In, On, At, Is, It, Up — Short Word Reading", ["In", "On", "At", "Is"]),
                    "te": ("ద్వియక్షర పద పఠనం", "అల, ఇల, ఈల, ఉల, ఎల, ఒల — ద్వియక్షర పదాలు", ["అల", "ఇల", "ఈల"]),
                    "hi": ("दो अक्षर शब्द पठन", "घर, फल, जल, बस, खत, नल — दो अक्षर शब्द पठन", ["घर", "फल", "जल"]),
                    "ta": ("இரண்டெழுத்து சொற்கள் வாசிப்பு", "அல், கல், சொல், புல், வில் — வாசிப்பு", ["அல்", "கல்"]),
                    "mr": ("दोन अक्षरी शब्द वाचन", "घर, जल, बस, मन, वर, कर — शब्द वाचन", ["घर", "जल", "बस"]),
                    "bn": ("দুই অক্ষরের শব্দ পাঠ", "ঘর, জল, বন, পথ, ফল, মত — শব্দ পাঠ", ["ঘর", "জল", "বন"]),
                    "kn": ("ಎರಡಕ್ಷರ ಪದಗಳ ವಾಚನ", "ಅರ, ಇಲಿ, ಊಟ, ಎಲೆ, ಒಲೆ — ಪದ ವಾಚನ", ["ಅರ", "ಇಲಿ"]),
                    "es": ("Lectura de Palabras Cortas de 2 Letras", "En, Un, Su, Tu, Mi, Ir — Lectura Rápida", ["En", "Un", "Su"])
                }
            },
            {
                "seq": 4,
                "title": "Zero Module 4: Reading Numbers 0 to 10",
                "lang_data": {
                    "en": ("Visual Digit & Number Reading 0 to 10", "0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 — Digits", ["Zero", "One", "Ten"]),
                    "te": ("సంఖ్యల పఠనం 0 నుండి 10 వరకు", "సున్నా, ఒకటి, రెండు, మూడు, నాలుగు, ఐదు, ఆరు, ఏడు, ఎనిమిది, తొమ్మిది, పది", ["సున్నా", "ఒకటి", "పది"]),
                    "hi": ("संख्या पठन 0 से 10 तक", "शून्य, एक, दो, तीन, चार, पांच, छह, सात, आठ, नौ, दस", ["शून्य", "एक", "दस"]),
                    "ta": ("எண்கள் வாசிப்பு 0 முதல் 10 வரை", "பூஜ்யம், ஒன்று, இரண்டு, மூன்று, நான்கு, ஐந்து, ஆறு, ஏழு, எட்டு, ஒன்பது, பத்து", ["பூஜ்யம்", "ஒன்று"]),
                    "mr": ("अंक वाचन 0 ते 10", "शून्य, एक, दोन, तीन, चार, पाच, सहा, सात, आठ, नऊ, दहा", ["शून्य", "एक", "दहा"]),
                    "bn": ("সংখ্যা পাঠ 0 থেকে 10", "শূন্য, এক, দুই, তিন, চার, পাঁচ, ছয়, সাত, আট, নয়, দশ", ["শূন্য", "এক", "দশ"]),
                    "kn": ("ಸಂಖ್ಯೆಗಳ ವಾಚನ 0 ರಿಂದ 10", "ಸೊನ್ನೆ, ಒಂದು, ಎರಡು, ಮೂರು, ನಾಲ್ಕು, ಐದು, ಆರು, ಏಳು, ಎಂಟು, ಒಂಬತ್ತು, ಹತ್ತು", ["ಸೊನ್ನೆ", "ಒಂದು"]),
                    "es": ("Lectura Visual de Números del 0 al 10", "0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 — Dígitos", ["Ce-ro", "Diez"])
                }
            },
            {
                "seq": 5,
                "title": "Zero Module 5: Reading Survival Signs & Labels",
                "lang_data": {
                    "en": ("Everyday Survival Sign & Label Reading", "Open, Closed, Exit, Stop, Push — Label Reading", ["O-pen", "Closed", "Ex-it"]),
                    "te": ("రోజువారీ బోర్డులు మరియు గుర్తుల పఠనం", "తెరిచి ఉంది, మూసివేసి ఉంది, నిష్క్రమణ, ఆగుము", ["తెరిచి-ఉంది", "నిష్క్రమణ"]),
                    "hi": ("दैनिक बोर्ड एवं संकेत पठन", "खुला है, बंद है, निकास, रुकिए", ["खुला-है", "निकास"]),
                    "ta": ("அன்றாட பலகைகள் மற்றும் குறியீடுகள் வாசிப்பு", "திறந்திருக்கிறது, மூடப்பட்டுள்ளது, வெளியேறும் வழி, நில்", ["திறந்திருக்கிறது"]),
                    "mr": ("दैनिक पाट्या व चिन्हे वाचन", "उघडे आहे, बंद आहे, बाहेर पडण्याचा मार्ग, थांबा", ["उघडे-आहे"]),
                    "bn": ("দৈনন্দিন বোর্ড ও চিহ্ন পাঠ", "খোলা আছে, বন্ধ আছে, প্রস্থান, থামুন", ["খোলা-আছে", "প্রস্থান"]),
                    "kn": ("ದೈನಂದಿನ ಫಲಕಗಳು ಮತ್ತು ಚಿಹ್ನೆಗಳ ವಾಚನ", "ತೆರೆದಿದೆ, ಮುಚ್ಚಿದೆ, ನಿರ್ಗಮನ, ನಿಲ್ಲಿ", ["ತೆರೆದಿದೆ", "ನಿರ್ಗಮನ"]),
                    "es": ("Lectura de Señales Cotidianas y Etiquetas", "Abierto, Cerrado, Salida, Alto, Empuje — Etiquetas", ["A-bier-to", "Sa-li-da"])
                }
            },
            {
                "seq": 6,
                "title": "Zero Module 6: Reading Fixed Greetings & Intro Chunks",
                "lang_data": {
                    "en": ("Reading Fixed Greetings & Intro Chunks", "Hello, Welcome, Good Morning — Sight Reading", ["Hel-lo", "Wel-come"]),
                    "te": ("స్వాగత పలికే వాక్యాల పఠనం", "నమస్కారం, స్వాగతం, శుభోదయం — పఠనం", ["నమస్కారం", "స్వాగతం"]),
                    "hi": ("नमस्ते एवं स्वागत वाक्य पठन", "नमस्ते, स्वागत है, शुभ प्रभात — पठन", ["नमस्ते", "स्वागत"]),
                    "ta": ("வணக்கம் மற்றும் வரவேற்பு வாக்கியங்கள் வாசிப்பு", "வணக்கம், நல்வரவு, காலை வணக்கம்", ["வணக்கம்", "நல்வரவு"]),
                    "mr": ("नमस्कार व स्वागत वाक्य वाचन", "नमस्कार, स्वागत आहे, शुभ प्रभात", ["नमस्कार", "स्वागत"]),
                    "bn": ("স্বাগতম ও সম্ভাষণ বাক্য পাঠ", "হ্যালো, স্বাগতম, সুপ্রভাত", ["হ্যালো", "স্বাগতম"]),
                    "kn": ("ನಮಸ್ಕಾರ ಮತ್ತು ಸ್ವಾಗತ ವಾಕ್ಯಗಳ ವಾಚನ", "ನಮಸ್ಕಾರ, ಸ್ವಾಗತ, ಶುಭೋದಯ", ["ನಮಸ್ಕಾರ", "ಸ್ವಾಗತ"]),
                    "es": ("Lectura de Saludos Esenciales y Bienvenida", "Hola, Bienvenido, Buenos días — Lectura", ["Ho-la", "Bien-ve-ni-do"])
                }
            }
        ]
    }
}

total_curriculums = 0
total_modules = 0
total_lessons = 0

for lang in languages:
    code = lang.iso_code
    
    for c_key, c_cfg in zero_curriculum_templates.items():
        curr = models.Curriculum(
            lang_id=lang.lang_id,
            title=f"{lang.lang_name} - {c_cfg['title']}",
            level="FOUNDATIONAL",
            description=f"{c_cfg['desc']} ({lang.lang_name})"
        )
        db.add(curr)
        db.commit()
        db.refresh(curr)
        total_curriculums += 1
        
        for m_data in c_cfg["modules"]:
            seq = m_data["seq"]
            m_title = m_data["title"]
            les_title, target_text, phonetics = m_data["lang_data"].get(code, m_data["lang_data"]["en"])
            
            mod = models.Module(
                curriculum_id=curr.curriculum_id,
                module_name=m_title,
                sequence_no=seq,
                skill_type=c_key
            )
            db.add(mod)
            db.commit()
            db.refresh(mod)
            total_modules += 1
            
            les = models.Lesson(
                module_id=mod.module_id,
                title=les_title,
                content_type=c_cfg["content_type"],
                content_url=f"/audio/{code}/zero_{c_key.lower()}_seq{seq}.mp3",
                target_text=target_text,
                phonetic_script=str(phonetics),
                difficulty_level="Zero"
            )
            db.add(les)
            db.commit()
            total_lessons += 1

print(f"SUCCESSFULLY CREATED:\n  • {total_curriculums} Curriculums (3 per language)\n  • {total_modules} Zero Level Modules (6 Spoken + 6 Written + 6 Reading x 8 languages)\n  • {total_lessons} Lessons across all 8 languages in Database!")
print("=" * 80)
db.close()
