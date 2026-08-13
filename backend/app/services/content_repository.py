from typing import Dict, List, Optional

class MultilingualContentRepository:
    """
    Centralized Multilingual Content Repository for AksharAI Language Literacy Platform.
    Stores and serves localized learning modules, vocabulary dictionaries,
    phonetic scripts, audio sample mappings, and assessment questions for 8 languages:
    - English (en)
    - Hindi (hi)
    - Telugu (te)
    - Tamil (ta)
    - Marathi (mr)
    - Bengali (bn)
    - Kannada (kn)
    - Spanish (es)
    """

    SUPPORTED_LANGUAGES = {
        "en": {"name": "English", "native_name": "English", "flag": "🇬🇧"},
        "hi": {"name": "Hindi", "native_name": "हिन्दी", "flag": "🇮🇳"},
        "te": {"name": "Telugu", "native_name": "తెలుగు", "flag": "🇮🇳"},
        "ta": {"name": "Tamil", "native_name": "தமிழ்", "flag": "🇮🇳"},
        "mr": {"name": "Marathi", "native_name": "मराठी", "flag": "🇮🇳"},
        "bn": {"name": "Bengali", "native_name": "বাংলা", "flag": "🇮🇳"},
        "kn": {"name": "Kannada", "native_name": "ಕನ್ನಡ", "flag": "🇮🇳"},
        "es": {"name": "Spanish", "native_name": "Español", "flag": "🇪🇸"}
    }

    CONTENT_REPOSITORY: Dict[str, Dict] = {
        "en": {
            "curriculum_title": "English Language Literacy & Advanced Fluency",
            "categories": [
                {
                    "id": "phonetics",
                    "title": "Phonemes & Alphabet Fundamentals",
                    "lessons": [
                        {"id": 101, "title": "Vowel Sounds & Phoneme Synthesis", "target_text": "Language unlocks knowledge, wisdom, and human expression", "phonemes": ["Lan-guage", "un-locks", "know-ledge"], "audio_url": "/audio/en/phonetics.mp3"},
                        {"id": 102, "title": "Consonant Blends & Syllables", "target_text": "Graceful articulation requires patience and practice", "phonemes": ["Grace-ful", "ar-ti-cu-la-tion"], "audio_url": "/audio/en/syllables.mp3"}
                    ]
                },
                {
                    "id": "vocabulary",
                    "title": "Vocabulary & Word Formation",
                    "lessons": [
                        {"id": 201, "title": "Prefixes, Suffixes & Root Words", "target_text": "Understanding root words enhances vocabulary comprehension", "phonemes": ["Un-der-stand-ing", "vo-ca-bu-la-ry"], "audio_url": "/audio/en/vocabulary.mp3"},
                        {"id": 202, "title": "Synonyms & Antonyms Mastery", "target_text": "Persist with determination to achieve true fluency", "phonemes": ["Per-sist", "de-ter-mi-na-tion"], "audio_url": "/audio/en/synonyms.mp3"}
                    ]
                },
                {
                    "id": "grammar",
                    "title": "Sentence Grammar & Syntax",
                    "lessons": [
                        {"id": 301, "title": "Noun-Verb Agreement & Tenses", "target_text": "She had written an eloquent essay before sunrise", "phonemes": ["She", "had", "writ-ten", "el-o-quent"], "audio_url": "/audio/en/grammar.mp3"}
                    ]
                },
                {
                    "id": "literature",
                    "title": "Advanced Literary Fluency & Expression",
                    "lessons": [
                        {"id": 401, "title": "Prose & Passage Comprehension", "target_text": "Mastery over language transforms thought into eloquent communication", "phonemes": ["Mas-te-ry", "trans-forms", "com-mu-ni-ca-tion"], "audio_url": "/audio/en/passage.mp3"}
                    ]
                }
            ]
        },
        "hi": {
            "curriculum_title": "हिन्दी भाषा साक्षरता एवं उच्च साहित्य ज्ञान",
            "categories": [
                {
                    "id": "phonetics",
                    "title": "वर्णमाला, स्वर एवं मात्रा ज्ञान",
                    "lessons": [
                        {"id": 101, "title": "स्वर एवं व्यंजन उच्चारण", "target_text": "भाषा विचारों को अभिव्यक्त करने का अमूल्य माध्यम है", "phonemes": ["भा-षा", "वि-चा-रों"], "audio_url": "/audio/hi/phonetics.mp3"},
                        {"id": 102, "title": "मात्राएँ एवं संयुक्त अक्षर", "target_text": "कृपा और क्षमा मानव जीवन के आधार हैं", "phonemes": ["कृ-पा", "क्ष-मा"], "audio_url": "/audio/hi/syllables.mp3"}
                    ]
                },
                {
                    "id": "vocabulary",
                    "title": "शब्दावली एवं शब्द निर्माण",
                    "lessons": [
                        {"id": 201, "title": "पर्यायवाची एवं विलोम शब्द", "target_text": "सूर्य और दिनकर प्रकाश के प्रतीक हैं", "phonemes": ["सू-र्य", "दिन-कर"], "audio_url": "/audio/hi/vocabulary.mp3"}
                    ]
                },
                {
                    "id": "grammar",
                    "title": "संधि, समास एवं वाक्य व्याकरण",
                    "lessons": [
                        {"id": 301, "title": "हिंदी संधि एवं समास", "target_text": "विद्या और आलय से मिलकर विद्यालय बनता है", "phonemes": ["विद्-या-ल-य"], "audio_url": "/audio/hi/grammar.mp3"}
                    ]
                },
                {
                    "id": "literature",
                    "title": "उच्च साहित्यिक वाचन एवं अभिव्यक्ति",
                    "lessons": [
                        {"id": 401, "title": "साहित्यिक गद्यांश वाचन", "target_text": "साहित्य का अनुशीलन मानव चेतना और व्यक्तित्व विकास का शाश्वत स्रोत है", "phonemes": ["सा-हि-त्-य"], "audio_url": "/audio/hi/passage.mp3"}
                    ]
                }
            ]
        },
        "te": {
            "curriculum_title": "తెలుగు భాషా అక్షరాస్యత మరియు సాహిత్య ప్రవీణత",
            "categories": [
                {
                    "id": "phonetics",
                    "title": "అక్షరాలు, వర్ణమాల మరియు గుణింతాలు",
                    "lessons": [
                        {"id": 101, "title": "అచ్చులు మరియు హల్లుల ఉచ్చారణ", "target_text": "భాష అనేది ఆలోచనలకు రూపాన్ని ఇచ్చే అమూల్యమైన సాధనం", "phonemes": ["భా-ష", "ఆ-లో-చ-న-లు"], "audio_url": "/audio/te/phonetics.mp3"},
                        {"id": 102, "title": "గుణింతాలు మరియు ఒత్తుల సాధన", "target_text": "కృప మరియు కరుణతో కూడిన మాటలు సమాజాన్ని రక్షిస్తాయి", "phonemes": ["కృ-ప", "క-రు-ణ"], "audio_url": "/audio/te/syllables.mp3"}
                    ]
                },
                {
                    "id": "vocabulary",
                    "title": "పదజాలం, పర్యాయపదాలు మరియు అర్థాలు",
                    "lessons": [
                        {"id": 201, "title": "పర్యాయపదాలు మరియు నానార్థాలు", "target_text": "అమృతం అనగా సుధ మరియు పీయూషము", "phonemes": ["అ-మృ-తం", "సు-ధ"], "audio_url": "/audio/te/vocabulary.mp3"}
                    ]
                },
                {
                    "id": "grammar",
                    "title": "సంధులు, సమాసాలు మరియు వ్యాకరణం",
                    "lessons": [
                        {"id": 301, "title": "తెలుగు సంధులు మరియు వాక్య నిర్మాణం", "target_text": "దేవ మరియు ఆలయం కలిస్తే దేవాలయము అవుతుంది", "phonemes": ["దే-వా-ల-య-ము"], "audio_url": "/audio/te/grammar.mp3"}
                    ]
                },
                {
                    "id": "literature",
                    "title": "సాహిత్య గద్య పఠనం మరియు భావ వ్యక్తీకరణ",
                    "lessons": [
                        {"id": 401, "title": "సాహిత్య గద్య పఠనం మరియు అర్థ గ్రహణ", "target_text": "సాహిత్యానుశీలనం మానవ చైతన్యానికి మరియు వ్యక్తిత్వ వికాసానికి అక్షయమైన నిధి", "phonemes": ["సా-హి-త్యా-ను-శీ-ల-నం"], "audio_url": "/audio/te/passage.mp3"}
                    ]
                }
            ]
        },
        "ta": {
            "curriculum_title": "தமிழ் மொழி எழுத்தறிவு மற்றும் இலக்கியம்",
            "categories": [
                {
                    "id": "phonetics",
                    "title": "எழுத்துக்கள் மற்றும் ஒலிகள்",
                    "lessons": [
                        {"id": 101, "title": "உயிர் எழுத்துக்கள் மற்றும் மெய் எழுத்துக்கள்", "target_text": "மொழி மனித எண்ணங்களின் உயரிய வெளிப்பாடாகும்", "phonemes": ["மொ-ழி", "எண்-ணங்-க-ளின்"], "audio_url": "/audio/ta/phonetics.mp3"},
                        {"id": 102, "title": "உயிர்மெய் எழுத்துக்கள் மற்றும் கூட்டெழுத்து", "target_text": "அறிவும் கல்வியும் வாழ்வின் அடிப்படை ஆகும்", "phonemes": ["அ-றி-வும்", "கல்-வி-யும்"], "audio_url": "/audio/ta/syllables.mp3"}
                    ]
                },
                {
                    "id": "vocabulary",
                    "title": "சொற்களஞ்சியம் மற்றும் சொல் உருவாக்கம்",
                    "lessons": [
                        {"id": 201, "title": "இணைச்சொற்கள் மற்றும் எதிர்ச்சொற்கள்", "target_text": "பரிதி என்பது சூரியனின் மறுபெயர் ஆகும்", "phonemes": ["ப-ரி-தி", "சூ-ரி-ய-னின்"], "audio_url": "/audio/ta/vocabulary.mp3"},
                        {"id": 202, "title": "சொல்லாக்கம் மற்றும் பொருள் விளக்கம்", "target_text": "நூலகம் என்பது நூல்களின் சேமிப்புக் கிடங்கு ஆகும்", "phonemes": ["நூ-ல-கம்", "சே-மிப்-பு"], "audio_url": "/audio/ta/words.mp3"}
                    ]
                },
                {
                    "id": "grammar",
                    "title": "இலக்கணம் மற்றும் வாக்கிய அமைப்பு",
                    "lessons": [
                        {"id": 301, "title": "புணர்ச்சி விதிகள் மற்றும் இலக்கணம்", "target_text": "தமிழ் மொழி இலக்கணம் மிகவும் பழமையானது", "phonemes": ["இ-லக்-க-ணம்", "ப-ழ-மை"], "audio_url": "/audio/ta/grammar.mp3"},
                        {"id": 302, "title": "வாக்கிய அமைப்பு மற்றும் தொடர் நிலை", "target_text": "கல்வி கற்றவன் கண் இருப்பவனுக்கு நிகர்", "phonemes": ["கல்-வி", "கற்-ற-வன்"], "audio_url": "/audio/ta/syntax.mp3"}
                    ]
                },
                {
                    "id": "literature",
                    "title": "உயர் இலக்கிய வாசிப்பு",
                    "lessons": [
                        {"id": 401, "title": "இலக்கிய உரைநடை வாசிப்பு", "target_text": "இலக்கியப் பயிற்சி மனித உணர்வுகளையும் ஆளுமையையும் உயர்த்தும் வற்றாத ஊற்றாகும்", "phonemes": ["இ-லக்-கி-யம்", "ஊற்-றா-கும்"], "audio_url": "/audio/ta/passage.mp3"},
                        {"id": 402, "title": "சரளமான பேச்சாற்றல் பயிற்சி", "target_text": "தொடர் பயிற்சியும் தீவிர முயற்சியும் மட்டுமே மொழியில் தேர்ச்சியைத் தரும்", "phonemes": ["ப-யிற்-சி", "தேர்ச்-சி"], "audio_url": "/audio/ta/fluency.mp3"}
                    ]
                }
            ]
        },
        "mr": {
            "curriculum_title": "मराठी भाषा साक्षरता व साहित्य",
            "categories": [
                {
                    "id": "phonetics",
                    "title": "वर्णमाला व ध्वनी ओळख",
                    "lessons": [
                        {"id": 101, "title": "स्वर व व्यंजन उच्चारण", "target_text": "भाषा ही विचारांना व्यक्त करण्याचे अमूल्य साधन आहे", "phonemes": ["भा-षा", "वि-चा-रां-ना"], "audio_url": "/audio/mr/phonetics.mp3"},
                        {"id": 102, "title": "मात्रा व जोडाक्षरे", "target_text": "कृपा आणि क्षमा हे मानवी जीवनाचे आधारस्तंभ आहेत", "phonemes": ["कृ-पा", "क्ष-मा"], "audio_url": "/audio/mr/syllables.mp3"}
                    ]
                },
                {
                    "id": "vocabulary",
                    "title": "शब्दसंग्रह व शब्दनिर्मिती",
                    "lessons": [
                        {"id": 201, "title": "समानार्थी व विरुद्धार्थी शब्द", "target_text": "भास्कर हा सूर्याचा समानार्थी शब्द आहे", "phonemes": ["भा-स्क-र", "सू-र्या-चा"], "audio_url": "/audio/mr/vocabulary.mp3"},
                        {"id": 202, "title": "शब्दनिर्मिती व उपसर्ग प्रत्यय", "target_text": "ग्रंथालय म्हणजे पुस्तकांचे संग्रहालय", "phonemes": ["ग्रं-था-ल-य", "सं-ग्र-हा-ल-य"], "audio_url": "/audio/mr/words.mp3"}
                    ]
                },
                {
                    "id": "grammar",
                    "title": "व्याकरण व वाक्यरचना",
                    "lessons": [
                        {"id": 301, "title": "मराठी संधी व समास", "target_text": "विद्या आणि आलय यांचा संधी विद्यालय होतो", "phonemes": ["विद्-या-ल-य", "सं-धी"], "audio_url": "/audio/mr/grammar.mp3"},
                        {"id": 302, "title": "शुद्ध वाक्यरचना व व्याकरण", "target_text": "सततचा सराव आणि अभ्यासानेच भाषेत प्रगती होते", "phonemes": ["स-रा-व", "प्र-ग-ती"], "audio_url": "/audio/mr/syntax.mp3"}
                    ]
                },
                {
                    "id": "literature",
                    "title": "उच्च साहित्यिक वाचन",
                    "lessons": [
                        {"id": 401, "title": "साहित्यिक उतारा वाचन", "target_text": "साहित्याचा अभ्यास मानवी चेतना आणि व्यक्तिमत्त्व विकासाचा अक्षय स्रोत आहे", "phonemes": ["सा-हि-त्या-चा", "चे-त-ना"], "audio_url": "/audio/mr/passage.mp3"},
                        {"id": 402, "title": "धाराप्रवाह भाषा व्यक्तीकरण", "target_text": "संध्याकाळची शांतता मनाला असीम समाधान देते", "phonemes": ["शां-त-ता", "स-मा-धा-न"], "audio_url": "/audio/mr/fluency.mp3"}
                    ]
                }
            ]
        },
        "bn": {
            "curriculum_title": "বাংলা ভাষা সাক্ষরতা ও সাহিত্য",
            "categories": [
                {
                    "id": "phonetics",
                    "title": "বর্ণমালা ও ধ্বনি পরিচয়",
                    "lessons": [
                        {"id": 101, "title": "স্বরবর্ণ ও ব্যঞ্জনবর্ণ উচ্চারণ", "target_text": "ভাষা মানুষের চিন্তাকে রূপ দেওয়ার অমূল্য বাহন", "phonemes": ["ভা-ষা", "মা-নু-ষের"], "audio_url": "/audio/bn/phonetics.mp3"},
                        {"id": 102, "title": "মাত্রা ও যুক্তাক্ষর অভ্যাস", "target_text": "কৃপা ও ক্ষমা মানব জীবনের ভিত্তি", "phonemes": ["কৃ-পা", "ক্ষ-মা"], "audio_url": "/audio/bn/syllables.mp3"}
                    ]
                },
                {
                    "id": "vocabulary",
                    "title": "শব্দভাণ্ডার ও শব্দগঠন",
                    "lessons": [
                        {"id": 201, "title": "সমার্থক ও বিপরীতার্থক শব্দ", "target_text": "রবি হলো সূর্যের সমার্থক শব্দ", "phonemes": ["র-বি", "সূ-র্যের"], "audio_url": "/audio/bn/vocabulary.mp3"},
                        {"id": 202, "title": "শব্দগঠন ও উপসর্গ প্রত্যয়", "target_text": "গ্রন্থাগার মানে বইয়ের সংগ্রহশালা", "phonemes": ["গ্রন্-থা-গা-র", "সং-গ্র-হ"], "audio_url": "/audio/bn/words.mp3"}
                    ]
                },
                {
                    "id": "grammar",
                    "title": "ব্যাকরণ ও বাক্যগঠন",
                    "lessons": [
                        {"id": 301, "title": "বাংলা সন্ধি ও সমাস", "target_text": "বিদ্যা ও আলয় যুক্ত হলে বিদ্যালয় হয়", "phonemes": ["বিদ্-যা-ল-য়", "স-ন্ধি"], "audio_url": "/audio/bn/grammar.mp3"},
                        {"id": 302, "title": "শুদ্ধ বাক্যগঠন ও ব্যাকরণ", "target_text": "নিরন্তর সাধনা ও অধ্যবসায়ের দ্বারাই ভাষার দক্ষতা অর্জন সম্ভব", "phonemes": ["নি-রন্-তর", "দক্ষ-তা"], "audio_url": "/audio/bn/syntax.mp3"}
                    ]
                },
                {
                    "id": "literature",
                    "title": "উচ্চ সাহিত্যিক পাঠ",
                    "lessons": [
                        {"id": 401, "title": "সাহিত্যিক গদ্য পাঠ", "target_text": "সাহিত্যের অনুশীলন মানব চেতনা ও ব্যক্তিত্ব বিকাশের শাশ্বত উৎস", "phonemes": ["সা-হি-ত্যের", "চে-ত-না"], "audio_url": "/audio/bn/passage.mp3"},
                        {"id": 402, "title": "সাবলীল ভাষা প্রকাশ", "target_text": "সন্ধ্যাবেলার শান্ত পরিবেশ মনকে আনন্দ দেয়", "phonemes": ["শা-ন্ত", "আ-ন-ন্দ"], "audio_url": "/audio/bn/fluency.mp3"}
                    ]
                }
            ]
        },
        "kn": {
            "curriculum_title": "ಕನ್ನಡ ಭಾಷಾ ಸಾಕ್ಷರತೆ ಮತ್ತು ಸಾಹಿತ್ಯ",
            "categories": [
                {
                    "id": "phonetics",
                    "title": "ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಉಚ್ಚಾರಣೆ",
                    "lessons": [
                        {"id": 101, "title": "ಸ್ವರ ಮತ್ತು ವ್ಯಂಜನ ಉಚ್ಚಾರಣೆ", "target_text": "ಭಾಷೆಯು ವಿಚಾರಗಳನ್ನು ವ್ಯಕ್ತಪಡಿಸುವ ಅಮೂಲ್ಯವಾದ ಸಾಧನವಾಗಿದೆ", "phonemes": ["ಭಾ-ಷೆ", "ವಿ-ಚಾ-ರ"], "audio_url": "/audio/kn/phonetics.mp3"},
                        {"id": 102, "title": "ಗುಣಿತಾಕ್ಷರ ಮತ್ತು ಒತ್ತಕ್ಷರ ಅಭ್ಯಾಸ", "target_text": "ಕೃಪೆ ಮತ್ತು ಕರುಣೆ ಮಾನವ ಜೀವನದ ಆಧಾರ", "phonemes": ["ಕೃ-ಪೆ", "ಕ-ರು-ಣೆ"], "audio_url": "/audio/kn/syllables.mp3"}
                    ]
                },
                {
                    "id": "vocabulary",
                    "title": "ಶಬ್ದಕೋಶ ಮತ್ತು ಪದರಚನೆ",
                    "lessons": [
                        {"id": 201, "title": "ಸಮಾನಾರ್ಥಕ ಮತ್ತು ವಿರುದ್ಧಾರ್ಥಕ ಪದಗಳು", "target_text": "ರವಿ ಎಂಬುದು ಸೂರ್ಯನ ಸಮಾನಾರ್ಥಕ ಪದ", "phonemes": ["ರ-ವಿ", "ಸೂ-ರ್ಯ"], "audio_url": "/audio/kn/vocabulary.mp3"},
                        {"id": 202, "title": "ಪದರಚನೆ ಮತ್ತು ಉಪಸರ್ಗ ಪ್ರತ್ಯಯ", "target_text": "ಗ್ರಂಥಾಲಯ ಎಂದರೆ ಪುಸ್ತಕಗಳ ಭಂಡಾರ", "phonemes": ["ಗ್ರಂ-ಥಾ-ಲ-ಯ", "ಭಂ-ಡಾ-ರ"], "audio_url": "/audio/kn/words.mp3"}
                    ]
                },
                {
                    "id": "grammar",
                    "title": "ವ್ಯಾಕರಣ ಮತ್ತು ವಾಕ್ಯರಚನೆ",
                    "lessons": [
                        {"id": 301, "title": "ಕನ್ನಡ ಸಂಧಿ ಮತ್ತು ಸಮಾಸ", "target_text": "ದೇವ ಮತ್ತು ಆಲಯ ಸೇರಿ ದೇವಾಲಯ ಆಗುತ್ತದೆ", "phonemes": ["ದೇ-ವಾ-ಲ-ಯ", "ಸಂ-ಧಿ"], "audio_url": "/audio/kn/grammar.mp3"},
                        {"id": 302, "title": "ಶುದ್ಧ ವಾಕ್ಯರಚನೆ ಮತ್ತು ವ್ಯಾಕರಣ", "target_text": "ನಿರಂತರ ಅಭ್ಯಾಸ ಮತ್ತು ಅಧ್ಯಯನದಿಂದ ಮಾತ್ರ ಭಾಷೆಯಲ್ಲಿ ಪಾಂಡಿತ್ಯ ಸಿಗುತ್ತದೆ", "phonemes": ["ನಿ-ರಂ-ತ-ರ", "ಪಾಂ-ಡಿ-ತ್ಯ"], "audio_url": "/audio/kn/syntax.mp3"}
                    ]
                },
                {
                    "id": "literature",
                    "title": "ಸಾಹಿತ್ಯಿಕ ಓದುವಿಕೆ",
                    "lessons": [
                        {"id": 401, "title": "ಸಾಹಿತ್ಯಿಕ ಗದ್ಯ ಓದುವಿಕೆ", "target_text": "ಸಾಹಿತ್ಯದ ಅಧ್ಯಯನವು ಮಾನವ ಚೇತನ ಮತ್ತು ವ್ಯಕ್ತಿತ್ವ ವಿಕಾಸದ ಅಕ್ಷಯ ಮೂಲವಾಗಿದೆ", "phonemes": ["ಸಾ-ಹಿ-ತ್ಯ", "ಚೇ-ತ-ನ"], "audio_url": "/audio/kn/passage.mp3"},
                        {"id": 402, "title": "ಸರಳ ಭಾಷಾ ಅಭಿವ್ಯಕ್ತಿ", "target_text": "ಸಂಜೆಯ ಪ್ರಶಾಂತ ವಾತಾವರಣವು ಮನಸ್ಸಿಗೆ ಸಂತಸ ನೀಡುತ್ತದೆ", "phonemes": ["ಪ್ರ-ಶಾಂ-ತ", "ಸಂ-ತ-ಸ"], "audio_url": "/audio/kn/fluency.mp3"}
                    ]
                }
            ]
        },
        "es": {
            "curriculum_title": "Alfabetización y Literatura en Español",
            "categories": [
                {
                    "id": "phonetics",
                    "title": "Fonemas y Fundamentos del Alfabeto",
                    "lessons": [
                        {"id": 101, "title": "Sonidos Vocálicos y Síntesis Fonémica", "target_text": "El lenguaje transforma el conocimiento y la expresión humana", "phonemes": ["len-gua-je", "trans-for-ma"], "audio_url": "/audio/es/phonetics.mp3"},
                        {"id": 102, "title": "Combinaciones de Consonantes y Sílabas", "target_text": "La articulación clara requiere paciencia y práctica constante", "phonemes": ["ar-ti-cu-la-ción", "pa-cien-cia"], "audio_url": "/audio/es/syllables.mp3"}
                    ]
                },
                {
                    "id": "vocabulary",
                    "title": "Vocabulario y Formación de Palabras",
                    "lessons": [
                        {"id": 201, "title": "Prefijos, Sufijos y Raíces de Palabras", "target_text": "Comprender las raíces de las palabras mejora la comprensión", "phonemes": ["com-pren-der", "ra-í-ces"], "audio_url": "/audio/es/vocabulary.mp3"},
                        {"id": 202, "title": "Sinónimos y Antónimos", "target_text": "Perseverar con determinación para lograr la verdadera fluidez", "phonemes": ["per-se-ve-rar", "de-ter-mi-na-ción"], "audio_url": "/audio/es/synonyms.mp3"}
                    ]
                },
                {
                    "id": "grammar",
                    "title": "Gramática y Sintaxis de Oraciones",
                    "lessons": [
                        {"id": 301, "title": "Concordancia Sustantivo-Verbo y Tiempos", "target_text": "Ella había escrito un ensayo elocuente antes del amanecer", "phonemes": ["es-cri-to", "e-lo-cuen-te"], "audio_url": "/audio/es/grammar.mp3"},
                        {"id": 302, "title": "Construcción de Oraciones Complejas", "target_text": "Aunque el viaje fue largo el destino resultó valioso", "phonemes": ["via-je", "des-ti-no"], "audio_url": "/audio/es/syntax.mp3"}
                    ]
                },
                {
                    "id": "literature",
                    "title": "Fluidez Literaria Avanzada",
                    "lessons": [
                        {"id": 401, "title": "Comprensión de Prosa y Pasajes", "target_text": "El dominio del lenguaje transforma el pensamiento en comunicación elocuente", "phonemes": ["do-mi-nio", "co-mu-ni-ca-ción"], "audio_url": "/audio/es/passage.mp3"},
                        {"id": 402, "title": "Expresión Oral Fluida", "target_text": "La práctica continua y la dedicación son la clave del dominio lingüístico", "phonemes": ["prác-ti-ca", "do-mi-nio"], "audio_url": "/audio/es/fluency.mp3"}
                    ]
                }
            ]
        }
    }

    @classmethod
    def get_supported_languages(cls) -> List[Dict]:
        return [{"code": code, **info} for code, info in cls.SUPPORTED_LANGUAGES.items()]

    @classmethod
    def get_content_by_language(cls, lang_code: str) -> Dict:
        target_code = lang_code if lang_code in cls.CONTENT_REPOSITORY else "en"
        return cls.CONTENT_REPOSITORY[target_code]

    @classmethod
    def search_content(cls, lang_code: str, query: str) -> List[Dict]:
        repo = cls.get_content_by_language(lang_code)
        matches = []
        q_lower = query.lower()
        for cat in repo.get("categories", []):
            for les in cat.get("lessons", []):
                if q_lower in les["title"].lower() or q_lower in les["target_text"].lower():
                    matches.append({"category": cat["title"], **les})
        return matches
