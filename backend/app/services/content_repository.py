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
