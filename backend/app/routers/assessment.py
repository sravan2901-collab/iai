from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from typing import List, Optional
from pydantic import BaseModel
from app.auth import get_optional_current_learner

router = APIRouter(prefix="/api/assessment", tags=["Generic Initial Assessment & Learning Path Generation"])

DIAGNOSTIC_QUESTIONS_BY_LANG = {
    "en": [
        {
            "id": 1, "stage": 1, "difficulty": 1, "skill_type": "READ",
            "question_title": "Question 1/9 [Level 1] — Phoneme & Letter Identification",
            "question_text": "Which word contains the long vowel sound /eɪ/ as in 'Fate'?",
            "options": [
                {"id": "a", "text": "Grace", "is_correct": True},
                {"id": "b", "text": "Track", "is_correct": False},
                {"id": "c", "text": "Bell", "is_correct": False},
                {"id": "d", "text": "Rock", "is_correct": False}
            ]
        },
        {
            "id": 2, "stage": 2, "difficulty": 2, "skill_type": "WRITE",
            "question_title": "Question 2/9 [Level 2] — Word Spelling & Structure",
            "question_text": "Type the correctly spelled word for a place where books are kept:",
            "accepted_answers": ["Library", "library", "LIBRARY"]
        },
        {
            "id": 3, "stage": 3, "difficulty": 3, "skill_type": "SPEAK",
            "question_title": "Question 3/9 [Level 3] — Sentence Pronunciation",
            "question_text": "Press microphone and speak aloud the sentence below:",
            "target_text": "Language unlocks knowledge, wisdom, and human expression"
        },
        {
            "id": 4, "stage": 4, "difficulty": 4, "skill_type": "READ",
            "question_title": "Question 4/9 [Level 4] — Synonyms & Vocabulary Mastery",
            "question_text": "Select the exact synonym for the word 'PERSISTENT':",
            "options": [
                {"id": "a", "text": "Persevering", "is_correct": True},
                {"id": "b", "text": "Temporary", "is_correct": False},
                {"id": "c", "text": "Hesitant", "is_correct": False},
                {"id": "d", "text": "Careless", "is_correct": False}
            ]
        },
        {
            "id": 5, "stage": 5, "difficulty": 5, "skill_type": "WRITE",
            "question_title": "Question 5/9 [Level 5] — Advanced Grammar & Verb Conjugation",
            "question_text": "Type the past perfect form of the verb 'Write':",
            "accepted_answers": ["written", "Written", "WRITTEN"]
        },
        {
            "id": 6, "stage": 6, "difficulty": 6, "skill_type": "SPEAK",
            "question_title": "Question 6/9 [Level 6] — Complex Sentence Articulation",
            "question_text": "Press microphone and speak aloud the compound complex sentence:",
            "target_text": "Although the journey was challenging, continuous practice brought clarity and confidence"
        },
        {
            "id": 7, "stage": 7, "difficulty": 7, "skill_type": "READ",
            "question_title": "Question 7/9 [Level 7] — Literary Passage Comprehension",
            "question_text": "Read passage: 'The profound silence of the evening was broken only by the gentle rustle of falling leaves.' What is the primary tone?",
            "options": [
                {"id": "a", "text": "Tranquil and Reflective", "is_correct": True},
                {"id": "b", "text": "Chaotic and Noisy", "is_correct": False},
                {"id": "c", "text": "Frightening and Dangerous", "is_correct": False},
                {"id": "d", "text": "Humorous and Joyful", "is_correct": False}
            ]
        },
        {
            "id": 8, "stage": 8, "difficulty": 8, "skill_type": "WRITE",
            "question_title": "Question 8/9 [Level 8] — Advanced Spelling & Orthography",
            "question_text": "Type the correct spelling for fluent and expressive speech:",
            "accepted_answers": ["Eloquence", "eloquence", "ELOQUENCE"]
        },
        {
            "id": 9, "stage": 9, "difficulty": 9, "skill_type": "SPEAK",
            "question_title": "Question 9/9 [Level 9] — High Literary Speech & Fluency",
            "question_text": "Press microphone and speak aloud the advanced literary passage:",
            "target_text": "Mastery over language transforms thought into eloquent communication and lifelong empowerment"
        }
    ],
    "te": [
        {
            "id": 1, "stage": 1, "difficulty": 1, "skill_type": "READ",
            "question_title": "ప్రశ్న 1/9 [స్థాయి 1] — అక్షరం మరియు గుణింత గుర్తింపు (Question 1/9 [Level 1] — Phonetics)",
            "question_text": "క్రింది వాటిలో 'కృ' (క + ఋ) గుణింత అక్షరం కలిగి ఉన్న పదాన్ని ఎంచుకోండి\nWhich word contains the 'కృ' (k + ru) letter sound?",
            "options": [
                {"id": "a", "text": "కృప", "is_correct": True},
                {"id": "b", "text": "కథ", "is_correct": False},
                {"id": "c", "text": "కలము", "is_correct": False},
                {"id": "d", "text": "కడవ", "is_correct": False}
            ]
        },
        {
            "id": 2, "stage": 2, "difficulty": 2, "skill_type": "WRITE",
            "question_title": "ప్రశ్న 2/9 [స్థాయి 2] — అక్షర దోష నివారణ మరియు రాయడం (Question 2/9 [Level 2] — Spelling)",
            "question_text": "జ్ఞానానికి మరియు పుస్తకాలకు నిలయమైన ప్రదేశాన్ని తెలిపే పదాన్ని రాయండి\nType the correct word for library:",
            "accepted_answers": ["గ్రంథాలయము", "గ్రంథాలయం", "పుస్తకాలయం"]
        },
        {
            "id": 3, "stage": 3, "difficulty": 3, "skill_type": "SPEAK",
            "question_title": "ప్రశ్న 3/9 [స్థాయి 3] — భాషా ఉచ్చారణ వాక్యం (Question 3/9 [Level 3] — Speech)",
            "question_text": "మైక్రోఫోన్ నొక్కి క్రింది భాషా వాక్యాన్ని స్పష్టంగా చదవండి\nPress microphone and speak aloud the sentence below:",
            "target_text": "భాష అనేది ఆలోచనలకు రూపాన్ని ఇచ్చే అమూల్యమైన సాధనం"
        },
        {
            "id": 4, "stage": 4, "difficulty": 4, "skill_type": "READ",
            "question_title": "ప్రశ్న 4/9 [స్థాయి 4] — పర్యాయపదాలు మరియు పదజాలం (Question 4/9 [Level 4] — Synonyms)",
            "question_text": "'అమృతం' అనే పదానికి సరైన పర్యాయపదాన్ని ఎంచుకోండి\nSelect the exact synonym for 'Amrutam':",
            "options": [
                {"id": "a", "text": "సుధ", "is_correct": True},
                {"id": "b", "text": "గరళం", "is_correct": False},
                {"id": "c", "text": "అనలం", "is_correct": False},
                {"id": "d", "text": "పవనం", "is_correct": False}
            ]
        },
        {
            "id": 5, "stage": 5, "difficulty": 5, "skill_type": "WRITE",
            "question_title": "ప్రశ్న 5/9 [స్థాయి 5] — సంధి మరియు వ్యాకరణ రాయడం (Question 5/9 [Level 5] — Grammar)",
            "question_text": "'దేవ + ఆలయం' కలిపి రాస్తే వచ్చే సరైన పదాన్ని టైప్ చేయండి\nType the combined Sandhi word for 'Deva + Alayam':",
            "accepted_answers": ["దేవాలయం", "దేవాలయము"]
        },
        {
            "id": 6, "stage": 6, "difficulty": 6, "skill_type": "SPEAK",
            "question_title": "ప్రశ్న 6/9 [స్థాయి 6] — సంక్లిష్ట వాక్య ఉచ్చారణ (Question 6/9 [Level 6] — Articulation)",
            "question_text": "మైక్రోఫోన్ నొక్కి క్రింది సంక్లిష్ట వాక్యాన్ని బిగ్గరగా చదవండి\nPress microphone and speak aloud complex sentence:",
            "target_text": "నిరంతర సాధన మరియు అధ్యయనం ద్వారా మాత్రమే భాషా ప్రావీణ్యం లభిస్తుంది"
        },
        {
            "id": 7, "stage": 7, "difficulty": 7, "skill_type": "READ",
            "question_title": "ప్రశ్న 7/9 [స్థాయి 7] — సాహిత్య గద్య పఠనావగాహన (Question 7/9 [Level 7] — Prose Reading)",
            "question_text": "వాక్యం: 'ప్రశాంతమైన సాయంత్ర వేళ పక్షుల కలకూజనాలు మనస్సుకు ఆహ్లాదాన్ని కలిగిస్తాయి.' దీని భావం ఏమిటి?\nWhat is the primary tone of the passage?",
            "options": [
                {"id": "a", "text": "ప్రశాంతత మరియు సంతోషం", "is_correct": True},
                {"id": "b", "text": "భయం మరియు ఆందోళన", "is_correct": False},
                {"id": "c", "text": "కోపం మరియు గొడవ", "is_correct": False},
                {"id": "d", "text": "అల్లరి మరియు సడి", "is_correct": False}
            ]
        },
        {
            "id": 8, "stage": 8, "difficulty": 8, "skill_type": "WRITE",
            "question_title": "ప్రశ్న 8/9 [స్థాయి 8] — ప్రౌఢ సాహిత్య పద నిర్మాణం (Question 8/9 [Level 8] — Advanced Spelling)",
            "question_text": "మిక్కిలి పాండిత్యం కలవాడిని తెలిపే పదాన్ని సరైన అక్షరాలతో రాయండి\nType the correct word for scholar:",
            "accepted_answers": ["విద్వాంసుడు", "విద్వాంసురాలు"]
        },
        {
            "id": 9, "stage": 9, "difficulty": 9, "skill_type": "SPEAK",
            "question_title": "ప్రశ్న 9/9 [స్థాయి 9] — ప్రౌఢ సాహిత్య భాషా ప్రవాహం (Question 9/9 [Level 9] — High Fluency)",
            "question_text": "మైక్రోఫోన్ నొక్కి క్రింది ఉన్నత సాహిత్య వాక్యాన్ని అనర్గళంగా చదవండి\nPress microphone and speak aloud advanced literary passage:",
            "target_text": "సాహిత్యానుశీలనం మానవ చైతన్యానికి మరియు వ్యక్తిత్వ వికాసానికి అక్షయమైన నిధి"
        }
    ],
    "hi": [
        {
            "id": 1, "stage": 1, "difficulty": 1, "skill_type": "READ",
            "question_title": "प्रश्न 1/9 [स्तर 1] — वर्णमाला एवं ध्वनि पहचान (Question 1/9 [Level 1] — Phonetics)",
            "question_text": "इनमें से 'ऋ' की मात्रा वाला सही शब्द चुनें\nWhich word contains the 'Ri' vowel sound?",
            "options": [
                {"id": "a", "text": "कृपा", "is_correct": True},
                {"id": "b", "text": "कपड़ा", "is_correct": False},
                {"id": "c", "text": "काम", "is_correct": False},
                {"id": "d", "text": "कान", "is_correct": False}
            ]
        },
        {
            "id": 2, "stage": 2, "difficulty": 2, "skill_type": "WRITE",
            "question_title": "प्रश्न 2/9 [स्तर 2] — शब्द वर्तनी एवं लेखन (Question 2/9 [Level 2] — Spelling)",
            "question_text": "पुस्तकों के संग्रह स्थल के लिए सही शब्द लिखें\nType the correctly spelled word for library:",
            "accepted_answers": ["पुस्तकालय", "पुस्तकागार"]
        },
        {
            "id": 3, "stage": 3, "difficulty": 3, "skill_type": "SPEAK",
            "question_title": "प्रश्न 3/9 [स्तर 3] — भाषा उच्चारण वाक्य (Question 3/9 [Level 3] — Speech)",
            "question_text": "माइक दबाएं और नीचे दिए गए वाक्य को स्पष्ट बोलें\nPress microphone and speak aloud sentence below:",
            "target_text": "भाषा विचारों को अभिव्यक्त करने का अमूल्य माध्यम है"
        },
        {
            "id": 4, "stage": 4, "difficulty": 4, "skill_type": "READ",
            "question_title": "प्रश्न 4/9 [स्तर 4] — पर्यायवाची शब्द ज्ञान (Question 4/9 [Level 4] — Synonyms)",
            "question_text": "'सूर्य' का सही पर्यायवाची शब्द चुनें\nSelect the exact synonym for the word 'Sun':",
            "options": [
                {"id": "a", "text": "दिनकर", "is_correct": True},
                {"id": "b", "text": "निशाचर", "is_correct": False},
                {"id": "c", "text": "पावक", "is_correct": False},
                {"id": "d", "text": "अंबर", "is_correct": False}
            ]
        },
        {
            "id": 5, "stage": 5, "difficulty": 5, "skill_type": "WRITE",
            "question_title": "प्रश्न 5/9 [स्तर 5] — संधि एवं व्याकरण लेखन (Question 5/9 [Level 5] — Grammar)",
            "question_text": "'विद्या + आलय' को मिलाकर बनने वाला सही शब्द लिखें\nType combined Sandhi word for 'Vidya + Alaya':",
            "accepted_answers": ["विद्यालय", "विद्याधाम"]
        },
        {
            "id": 6, "stage": 6, "difficulty": 6, "skill_type": "SPEAK",
            "question_title": "प्रश्न 6/9 [स्तर 6] — जटिल वाक्य वाचन (Question 6/9 [Level 6] — Articulation)",
            "question_text": "माइक दबाएं और नीचे दिए गए वाक्य को स्पष्ट रूप से पढ़ें\nSpeak aloud complex sentence:",
            "target_text": "निरंतर अभ्यास और अध्ययन से ही भाषा में निपुणता प्राप्त होती है"
        },
        {
            "id": 7, "stage": 7, "difficulty": 7, "skill_type": "READ",
            "question_title": "प्रश्न 7/9 [स्तर 7] — साहित्यिक गद्यांश समझ (Question 7/9 [Level 7] — Prose Reading)",
            "question_text": "वाक्य: 'संध्या काल की शांति मन को असीम सुख और संतोष प्रदान करती है।' इसका मुख्य भाव क्या है?\nWhat is the primary tone of the passage?",
            "options": [
                {"id": "a", "text": "शांति और मानसिक संतोष", "is_correct": True},
                {"id": "b", "text": "भय और अशांति", "is_correct": False},
                {"id": "c", "text": "क्रोध और विवाद", "is_correct": False},
                {"id": "d", "text": "शोरगुल", "is_correct": False}
            ]
        },
        {
            "id": 8, "stage": 8, "difficulty": 8, "skill_type": "WRITE",
            "question_title": "प्रश्न 8/9 [स्तर 8] — उच्च साहित्यिक शब्द रचना (Question 8/9 [Level 8] — Advanced Spelling)",
            "question_text": "ज्ञानवान एवं विद्वान व्यक्ति के लिए प्रयुक्त एक शब्द लिखें\nType correct word for scholar:",
            "accepted_answers": ["विद्वान", "ज्ञानवान"]
        },
        {
            "id": 9, "stage": 9, "difficulty": 9, "skill_type": "SPEAK",
            "question_title": "प्रश्न 9/9 [स्तर 9] — उच्च साहित्यिक भाषा प्रवाह (Question 9/9 [Level 9] — High Fluency)",
            "question_text": "माइक दबाएं और नीचे दिए गए उच्च साहित्यिक वाक्य को धाराप्रवाह बोलें\nSpeak aloud advanced literary passage:",
            "target_text": "साहित्य का अनुशीलन मानव चेतना और व्यक्तित्व विकास का शाश्वत स्रोत है"
        }
    ],
    "ta": [
        {
            "id": 1, "stage": 1, "difficulty": 1, "skill_type": "READ",
            "question_title": "கேள்வி 1/9 [நிலை 1] — எழுத்து மற்றும் ஒலி அடையாளம் (Question 1/9 [Level 1] — Phonetics)",
            "question_text": "கீழ்கண்டவற்றுள் 'க்' மெய் எழுத்து உள்ள சரியான சொல்லைத் தேர்ந்தெடுக்கவும்\nWhich word contains the Tamil consonant sound 'Ik'?",
            "options": [
                {"id": "a", "text": "அக்கறை", "is_correct": True},
                {"id": "b", "text": "மரம்", "is_correct": False},
                {"id": "c", "text": "படம்", "is_correct": False},
                {"id": "d", "text": "பந்து", "is_correct": False}
            ]
        },
        {
            "id": 2, "stage": 2, "difficulty": 2, "skill_type": "WRITE",
            "question_title": "கேள்வி 2/9 [நிலை 2] — சொல் எழுத்துப்பிழை திருத்தம் (Question 2/9 [Level 2] — Spelling)",
            "question_text": "நூல்கள் சேமித்து வைக்கும் இடத்திற்குரிய சரியான சொல்லை எழுதவும்\nType the correct Tamil word for Library:",
            "accepted_answers": ["நூல்நிலையம்", "நூலகம்"]
        },
        {
            "id": 3, "stage": 3, "difficulty": 3, "skill_type": "SPEAK",
            "question_title": "கேள்வி 3/9 [நிலை 3] — வாக்கிய உச்சரிப்பு (Question 3/9 [Level 3] — Speech)",
            "question_text": "மைக்கை அழுத்தி கீழே உள்ள தமிழ் வாக்கியத்தை தெளிவாகப் பேசவும்\nPress microphone and speak aloud Tamil sentence:",
            "target_text": "மொழி மனித எண்ணங்களின் உயரிய வெளிப்பாடாகும்"
        },
        {
            "id": 4, "stage": 4, "difficulty": 4, "skill_type": "READ",
            "question_title": "கேள்வி 4/9 [நிலை 4] — இணைச்சொற்கள் மற்றும் சொற்களஞ்சியம் (Question 4/9 [Level 4] — Synonyms)",
            "question_text": "'பரிதி' என்ற சொல்லின் சரியான பொருள் எது?\nSelect the exact Tamil synonym for the word 'Paridhi' (Sun):",
            "options": [
                {"id": "a", "text": "சூரியன்", "is_correct": True},
                {"id": "b", "text": "சந்திரன்", "is_correct": False},
                {"id": "c", "text": "மேகம்", "is_correct": False},
                {"id": "d", "text": "காற்று", "is_correct": False}
            ]
        },
        {
            "id": 5, "stage": 5, "difficulty": 5, "skill_type": "WRITE",
            "question_title": "கேள்வி 5/9 [நிலை 5] — இலக்கணப் புணர்ச்சி (Question 5/9 [Level 5] — Grammar)",
            "question_text": "'தமிழ் + மொழி' என்பதைச் சேர்த்து எழுதினால் வரும் சொல் எது?\nType the combined grammar word for 'Tamil + Mozhi':",
            "accepted_answers": ["தமிழ்மொழி", "தமிழ் மொழி"]
        },
        {
            "id": 6, "stage": 6, "difficulty": 6, "skill_type": "SPEAK",
            "question_title": "கேள்வி 6/9 [நிலை 6] — சிக்கலான வாக்கிய உச்சரிப்பு (Question 6/9 [Level 6] — Articulation)",
            "question_text": "மைக்கை அழுத்தி கீழே உள்ள சிக்கலான வாக்கியத்தைப் படிக்கவும்\nSpeak aloud complex Tamil sentence:",
            "target_text": "தொடர் பயிற்சியும் தீவிர முயற்சியும் மட்டுமே மொழியில் தேர்ச்சியைத் தரும்"
        },
        {
            "id": 7, "stage": 7, "difficulty": 7, "skill_type": "READ",
            "question_title": "கேள்வி 7/9 [நிலை 7] — இலக்கியப் பத்திப் புரிதல் (Question 7/9 [Level 7] — Prose Reading)",
            "question_text": "வாக்கியம்: 'மாலை நேர அமைதியும் பறவைகளின் ஒலியும் மனதிற்கு அமைதியைத் தருகின்றன.' இதன் மையம் யாது?\nWhat is the primary tone of the passage?",
            "options": [
                {"id": "a", "text": "அமைதி மற்றும் மகிழ்ச்சி", "is_correct": True},
                {"id": "b", "text": "பயம் மற்றும் கவலை", "is_correct": False},
                {"id": "c", "text": "கோபம்", "is_correct": False},
                {"id": "d", "text": "இரைச்சல்", "is_correct": False}
            ]
        },
        {
            "id": 8, "stage": 8, "difficulty": 8, "skill_type": "WRITE",
            "question_title": "கேள்வி 8/9 [நிலை 8] — உயர் இலக்கியச் சொல் உருவாக்கம் (Question 8/9 [Level 8] — Advanced Spelling)",
            "question_text": "கல்வியில் சிறந்தவரைக் குறிக்கும் தமிழ் சொல்லை எழுதவும்\nType the correct Tamil word for Scholar:",
            "accepted_answers": ["சான்றோர்", "அறிஞர்"]
        },
        {
            "id": 9, "stage": 9, "difficulty": 9, "skill_type": "SPEAK",
            "question_title": "கேள்வி 9/9 [நிலை 9] — உயர் இலக்கியப் பேச்சாற்றல் (Question 9/9 [Level 9] — High Fluency)",
            "question_text": "மைக்கை அழுத்தி கீழே உள்ள உயர் இலக்கிய வாக்கியத்தை சரளமாகப் பேசவும்\nSpeak aloud advanced literary Tamil passage:",
            "target_text": "இலக்கியப் பயிற்சி மனித உணர்வுகளையும் ஆளுமையையும் உயர்த்தும் வற்றாத ஊற்றாகும்"
        }
    ],
    "bn": [
        {
            "id": 1, "stage": 1, "difficulty": 1, "skill_type": "READ",
            "question_title": "প্রশ্ন ১/৯ [স্তর ১] — বর্ণ ও ধ্বনি পরিচয় (Question 1/9 [Level 1] — Phonetics)",
            "question_text": "কোন শব্দটিতে 'ঋ' কার যুক্ত বর্ণ রয়েছে?\nWhich word contains the 'Ri' vowel sound in Bengali?",
            "options": [
                {"id": "a", "text": "কৃপা", "is_correct": True},
                {"id": "b", "text": "কাজ", "is_correct": False},
                {"id": "c", "text": "জল", "is_correct": False},
                {"id": "d", "text": "ফুল", "is_correct": False}
            ]
        },
        {
            "id": 2, "stage": 2, "difficulty": 2, "skill_type": "WRITE",
            "question_title": "প্রশ্ন ২/৯ [স্তর ২] — বানান ও শব্দ লিখন (Question 2/9 [Level 2] — Spelling)",
            "question_text": "বই রাখার স্থানটি সঠিক বানানে লিখুন\nType the correct Bengali word for Library:",
            "accepted_answers": ["গ্রন্থাগার", "পুস্তকাগার"]
        },
        {
            "id": 3, "stage": 3, "difficulty": 3, "skill_type": "SPEAK",
            "question_title": "প্রশ্ন ৩/৯ [স্তর ৩] — বাক্যের স্পষ্ট উচ্চারণ (Question 3/9 [Level 3] — Speech)",
            "question_text": "মাইক্রোফোন চেপে নিচের বাক্যটি স্পষ্ট করে বলুন\nPress microphone and speak aloud Bengali sentence:",
            "target_text": "ভাষা মানুষের চিন্তাকে রূপ দেওয়ার অমূল্য বাহন"
        },
        {
            "id": 4, "stage": 4, "difficulty": 4, "skill_type": "READ",
            "question_title": "প্রশ্ন ৪/৯ [স্তর ৪] — সমার্থক শব্দ জ্ঞান (Question 4/9 [Level 4] — Synonyms)",
            "question_text": "'সূর্য' শব্দের সঠিক সমার্থক শব্দ কোনটি?\nSelect the exact Bengali synonym for 'Sun':",
            "options": [
                {"id": "a", "text": "রবি", "is_correct": True},
                {"id": "b", "text": "নদী", "is_correct": False},
                {"id": "c", "text": "পাহাড়", "is_correct": False},
                {"id": "d", "text": "বাতাস", "is_correct": False}
            ]
        },
        {
            "id": 5, "stage": 5, "difficulty": 5, "skill_type": "WRITE",
            "question_title": "প্রশ্ন ৫/৯ [স্তর ৫] — সন্ধি ও ব্যাকরণ লিখন (Question 5/9 [Level 5] — Grammar)",
            "question_text": "'বিদ্যা + আলয়' যুক্ত করে সঠিক শব্দটি লিখুন\nType the combined Sandhi word for 'Vidya + Alaya':",
            "accepted_answers": ["বিদ্যালয়", "বিদ্যানিকেতন"]
        },
        {
            "id": 6, "stage": 6, "difficulty": 6, "skill_type": "SPEAK",
            "question_title": "প্রশ্ন ৬/৯ [স্তর ৬] — জটিল বাক্য উচ্চারণ (Question 6/9 [Level 6] — Articulation)",
            "question_text": "মাইক্রোফোন চেপে নিচের জটিল বাক্যটি পড়ুন\nSpeak aloud complex Bengali sentence:",
            "target_text": "নিরন্তর সাধনা ও অধ্যবসায়ের দ্বারাই ভাষার দক্ষতা অর্জন সম্ভব"
        },
        {
            "id": 7, "stage": 7, "difficulty": 7, "skill_type": "READ",
            "question_title": "প্রশ্ন ৭/৯ [স্তর ৭] — সাহিত্যিক গদ্য বোধগম্যতা (Question 7/9 [Level 7] — Prose Reading)",
            "question_text": "বাক্য: 'সন্ধ্যাবেলার শান্ত পরিবেশ মনকে আনন্দ দেয়।' এর মূল ভাব কী?\nWhat is the primary tone of the passage?",
            "options": [
                {"id": "a", "text": "শান্তি ও আনন্দ", "is_correct": True},
                {"id": "b", "text": "ভয় ও উদ্বেগ", "is_correct": False},
                {"id": "c", "text": "রাগ ও ক্ষোভ", "is_correct": False},
                {"id": "d", "text": "কোলাহল", "is_correct": False}
            ]
        },
        {
            "id": 8, "stage": 8, "difficulty": 8, "skill_type": "WRITE",
            "question_title": "প্রশ্ন ৮/৯ [স্তর ৮] — উচ্চ সাহিত্যিক শব্দ গঠন (Question 8/9 [Level 8] — Advanced Spelling)",
            "question_text": "জ্ঞানী ব্যক্তি নির্দেশক সঠিক শব্দটি লিখুন\nType the correct Bengali word for Scholar:",
            "accepted_answers": ["বিদ্বান", "জ্ঞানী"]
        },
        {
            "id": 9, "stage": 9, "difficulty": 9, "skill_type": "SPEAK",
            "question_title": "প্রশ্ন ৯/৯ [স্তর ৯] — সাবলীল সাহিত্যিক প্রকাশ (Question 9/9 [Level 9] — High Fluency)",
            "question_text": "মাইক্রোফোন চেপে নিচের সাহিত্যিক বাক্যটি সাবলীলভাবে বলুন\nSpeak aloud advanced literary Bengali passage:",
            "target_text": "সাহিত্যের অনুশীলন মানব চেতনা ও ব্যক্তিত্ব বিকাশের শাশ্বত উৎস"
        }
    ],
    "mr": [
        {
            "id": 1, "stage": 1, "difficulty": 1, "skill_type": "READ",
            "question_title": "प्रश्न १/९ [पातळी १] — वर्णमाला व ध्वनी ओळख (Question 1/9 [Level 1] — Phonetics)",
            "question_text": "खालीलपैकी 'ऋ' ची मात्रा असलेला योग्य शब्द निवडा\nWhich Marathi word contains the 'Ri' sound?",
            "options": [
                {"id": "a", "text": "कृपा", "is_correct": True},
                {"id": "b", "text": "काम", "is_correct": False},
                {"id": "c", "text": "पान", "is_correct": False},
                {"id": "d", "text": "घर", "is_correct": False}
            ]
        },
        {
            "id": 2, "stage": 2, "difficulty": 2, "skill_type": "WRITE",
            "question_title": "प्रश्न २/९ [पातळी २] — शब्द वर्तनी व लेखन (Question 2/9 [Level 2] — Spelling)",
            "question_text": "पुस्तकांचे संग्रह असलेल्या ठिकाणासाठी योग्य मराठी शब्द लिहा\nType the correct Marathi word for Library:",
            "accepted_answers": ["ग्रंथालय", "पुस्तकालय"]
        },
        {
            "id": 3, "stage": 3, "difficulty": 3, "skill_type": "SPEAK",
            "question_title": "प्रश्न ३/९ [पातळी ३] — भाषा उच्चारण वाक्य (Question 3/9 [Level 3] — Speech)",
            "question_text": "माईक दाबून खालील मराठी वाक्य स्पष्ट बोला\nPress microphone and speak aloud Marathi sentence:",
            "target_text": "भाषा ही विचारांना व्यक्त करण्याचे अमूल्य साधन आहे"
        },
        {
            "id": 4, "stage": 4, "difficulty": 4, "skill_type": "READ",
            "question_title": "प्रश्न ४/९ [पातळी ४] — समानार्थी शब्द ज्ञान (Question 4/9 [Level 4] — Synonyms)",
            "question_text": "'सूर्य' या शब्दाचा अचूक समानार्थी शब्द निवडा\nSelect the exact Marathi synonym for 'Sun':",
            "options": [
                {"id": "a", "text": "भास्कर", "is_correct": True},
                {"id": "b", "text": "चंद्र", "is_correct": False},
                {"id": "c", "text": "तलाव", "is_correct": False},
                {"id": "d", "text": "वारा", "is_correct": False}
            ]
        },
        {
            "id": 5, "stage": 5, "difficulty": 5, "skill_type": "WRITE",
            "question_title": "प्रश्न ५/९ [पातळी ५] — संधी व व्याकरण लेखन (Question 5/9 [Level 5] — Grammar)",
            "question_text": "'विद्या + आलय' एकत्र करून होणारा शब्द लिहा\nType the combined Sandhi word for 'Vidya + Alaya':",
            "accepted_answers": ["विद्यालय", "विद्याधाम"]
        },
        {
            "id": 6, "stage": 6, "difficulty": 6, "skill_type": "SPEAK",
            "question_title": "प्रश्न ६/९ [पातळी ६] — कठीण वाक्य वाचन (Question 6/9 [Level 6] — Articulation)",
            "question_text": "माईक दाबून खालील कठीण वाक्य मोठ्याने वाचा\nSpeak aloud complex Marathi sentence:",
            "target_text": "सततचा सराव आणि अभ्यासानेच भाषेत प्रगती आणि प्रभुत्व मिळते"
        },
        {
            "id": 7, "stage": 7, "difficulty": 7, "skill_type": "READ",
            "question_title": "प्रश्न ७/९ [पातळी ७] — साहित्यिक उतारा समज (Question 7/9 [Level 7] — Prose Reading)",
            "question_text": "वाक्य: 'संध्याकाळची शांतता मनाला असीम समाधान देते.' याचा अर्थ काय?\nWhat is the primary tone of the passage?",
            "options": [
                {"id": "a", "text": "शांतता आणि समाधान", "is_correct": True},
                {"id": "b", "text": "भीती आणि चिंता", "is_correct": False},
                {"id": "c", "text": "रागाचा उद्रेक", "is_correct": False},
                {"id": "d", "text": "आवाज", "is_correct": False}
            ]
        },
        {
            "id": 8, "stage": 8, "difficulty": 8, "skill_type": "WRITE",
            "question_title": "प्रश्न ८/९ [पातळी ८] — उच्च साहित्यिक शब्द रचना (Question 8/9 [Level 8] — Advanced Spelling)",
            "question_text": "मोठ्या विद्वान व्यक्तीसाठी प्रयुक्त योग्य शब्द लिहा\nType the correct Marathi word for Scholar:",
            "accepted_answers": ["विद्वान", "ज्ञानवंत"]
        },
        {
            "id": 9, "stage": 9, "difficulty": 9, "skill_type": "SPEAK",
            "question_title": "प्रश्न ९/९ [पातळी ९] — उच्च साहित्यिक भाषा प्रवाह (Question 9/9 [Level 9] — High Fluency)",
            "question_text": "माईक दाबून खालील उच्च साहित्यिक वाक्य आत्मविश्वासाने बोला\nSpeak aloud advanced literary Marathi passage:",
            "target_text": "साहित्याचा अभ्यास मानवी चेतना आणि व्यक्तिमत्त्व विकासाचा अक्षय स्रोत आहे"
        }
    ],
    "kn": [
        {
            "id": 1, "stage": 1, "difficulty": 1, "skill_type": "READ",
            "question_title": "ಪ್ರಶ್ನೆ 1/9 [ಹಂತ 1] — ಅಕ್ಷರ ಮತ್ತು ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ (Question 1/9 [Level 1] — Phonetics)",
            "question_text": "ಕೆಳಗಿನವುಗಳಲ್ಲಿ 'ಕೃ' (ಕ + ಋ) ಗುಣಿತಾಕ್ಷರವಿರುವ ಸರಿಯಾದ ಪದವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ\nWhich Kannada word contains the 'Kru' sound?",
            "options": [
                {"id": "a", "text": "ಕೃಪೆ", "is_correct": True},
                {"id": "b", "text": "ಕಥೆ", "is_correct": False},
                {"id": "c", "text": "ಕಲಂ", "is_correct": False},
                {"id": "d", "text": "ಮರ", "is_correct": False}
            ]
        },
        {
            "id": 2, "stage": 2, "difficulty": 2, "skill_type": "WRITE",
            "question_title": "ಪ್ರಶ್ನೆ 2/9 [ಹಂತ 2] — ಪದ ಕಾಗುಣಿತ ಬರವಣಿಗೆ (Question 2/9 [Level 2] — Spelling)",
            "question_text": "ಪುಸ್ತಕಗಳ ಭಂಡಾರವನ್ನು ಸೂಚಿಸುವ ಕನ್ನಡ ಪದವನ್ನು ಬರೆಯಿರಿ\nType the correct Kannada word for Library:",
            "accepted_answers": ["ಗ್ರಂಥಾಲಯ", "ಪುಸ್ತಕಾಲಯ"]
        },
        {
            "id": 3, "stage": 3, "difficulty": 3, "skill_type": "SPEAK",
            "question_title": "ಪ್ರಶ್ನೆ 3/9 [ಹಂತ 3] — ಭಾಷಾ ಉಚ್ಚಾರಣೆ (Question 3/9 [Level 3] — Speech)",
            "question_text": "ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ ಕೆಳಗಿನ ಕನ್ನಡ ವಾಕ್ಯವನ್ನು ಸ್ಪಷ್ಟವಾಗಿ ಓದಿ\nPress microphone and speak aloud Kannada sentence:",
            "target_text": "ಭಾಷೆಯು ವಿಚಾರಗಳನ್ನು ವ್ಯಕ್ತಪಡಿಸುವ ಅಮೂಲ್ಯವಾದ ಸಾಧನವಾಗಿದೆ"
        },
        {
            "id": 4, "stage": 4, "difficulty": 4, "skill_type": "READ",
            "question_title": "ಪ್ರಶ್ನೆ 4/9 [ಹಂತ 4] — ಸಮಾನಾರ್ಥಕ ಪದಗಳು (Question 4/9 [Level 4] — Synonyms)",
            "question_text": "'ಸೂರ್ಯ' ಪದಕ್ಕೆ ಸರಿಯಾದ ಸಮಾನಾರ್ಥಕ ಪದವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ\nSelect exact Kannada synonym for 'Sun':",
            "options": [
                {"id": "a", "text": "ರವಿ", "is_correct": True},
                {"id": "b", "text": "ಚಂದ್ರ", "is_correct": False},
                {"id": "c", "text": "ಗಾಳಿ", "is_correct": False},
                {"id": "d", "text": "ನೀರು", "is_correct": False}
            ]
        },
        {
            "id": 5, "stage": 5, "difficulty": 5, "skill_type": "WRITE",
            "question_title": "ಪ್ರಶ್ನೆ 5/9 [ಹಂತ 5] — ಸಂಧಿ ಮತ್ತು ವ್ಯಾಕರಣ ಬರವಣಿಗೆ (Question 5/9 [Level 5] — Grammar)",
            "question_text": "'ದೇವ + ಆಲಯ' ಸೇರಿಸಿ ಬರೆದಾಗ ಬರುವ ಪದವನ್ನು ಟೈಪ್ ಮಾಡಿ\nType the combined Sandhi word for 'Deva + Alaya':",
            "accepted_answers": ["ದೇವಾಲಯ", "ದೇವಮಂದಿರ"]
        },
        {
            "id": 6, "stage": 6, "difficulty": 6, "skill_type": "SPEAK",
            "question_title": "ಪ್ರಶ್ನೆ 6/9 [ಹಂತ 6] — ಸಂಕೀರ್ಣ ವಾಕ್ಯ ಉಚ್ಚಾರಣೆ (Question 6/9 [Level 6] — Articulation)",
            "question_text": "ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ ಕೆಳಗಿನ ಸಂಕೀರ್ಣ ವಾಕ್ಯವನ್ನು ಓದಿ\nSpeak aloud complex Kannada sentence:",
            "target_text": "ನಿರಂತರ ಅಭ್ಯಾಸ ಮತ್ತು ಅಧ್ಯಯನದಿಂದ ಮಾತ್ರ ಭಾಷೆಯಲ್ಲಿ ಪಾಂಡಿತ್ಯ ಸಿಗುತ್ತದೆ"
        },
        {
            "id": 7, "stage": 7, "difficulty": 7, "skill_type": "READ",
            "question_title": "ಪ್ರಶ್ನೆ 7/9 [ಹಂತ 7] — ಸಾಹಿತ್ಯ ಗದ್ಯ ಗ್ರಹಿಕೆ (Question 7/9 [Level 7] — Prose Reading)",
            "question_text": "ವಾಕ್ಯ: 'ಸಂಜೆಯ ಪ್ರಶಾಂತ ವಾತಾವರಣವು ಮನಸ್ಸಿಗೆ ಸಂತಸ ನೀಡುತ್ತದೆ.' ಇದರ ಮೂಲ ಭಾವವೇನು?\nWhat is the primary tone of the passage?",
            "options": [
                {"id": "a", "text": "ಶಾಂತಿ ಮತ್ತು ಸಂತೋಷ", "is_correct": True},
                {"id": "b", "text": "ಭಯ ಮತ್ತು ಆತಂಕ", "is_correct": False},
                {"id": "c", "text": "ಕೋಪ", "is_correct": False},
                {"id": "d", "text": "ಗದ್ದಲ", "is_correct": False}
            ]
        },
        {
            "id": 8, "stage": 8, "difficulty": 8, "skill_type": "WRITE",
            "question_title": "ಪ್ರಶ್ನೆ 8/9 [ಹಂತ 8] — ಪ್ರೌಢ ಸಾಹಿತ್ಯಿಕ ಪದ ರಚನೆ (Question 8/9 [Level 8] — Advanced Spelling)",
            "question_text": "ಜ್ಞಾನವುಳ್ಳ ಪಂಡಿತ ಎಂಬ ಅರ್ಥ ನೀಡುವ ಕನ್ನಡ ಪದ ಬರೆಯಿರಿ\nType the correct Kannada word for Scholar:",
            "accepted_answers": ["ವಿದ್ವಾಂಸ", "ಪಂಡಿತ"]
        },
        {
            "id": 9, "stage": 9, "difficulty": 9, "skill_type": "SPEAK",
            "question_title": "ಪ್ರಶ್ನೆ 9/9 [ಹಂತ 9] — ಪ್ರೌಢ ಸಾಹಿತ್ಯಿಕ ಭಾಷಾ ಶೈಲಿ (Question 9/9 [Level 9] — High Fluency)",
            "question_text": "ಮೈಕ್ರೋಫೋನ್ ಒತ್ತಿ ಕೆಳಗಿನ ಪ್ರೌಢ ಸಾಹಿತ್ಯಿಕ ವಾಕ್ಯವನ್ನು ಓದಿ\nSpeak aloud advanced literary Kannada passage:",
            "target_text": "ಸಾಹಿತ್ಯದ ಅಧ್ಯಯನವು ಮಾನವ ಚೇತನ ಮತ್ತು ವ್ಯಕ್ತಿತ್ವ ವಿಕಾಸದ ಅಕ್ಷಯ ಮೂಲವಾಗಿದೆ"
        }
    ],
    "es": [
        {
            "id": 1, "stage": 1, "difficulty": 1, "skill_type": "READ",
            "question_title": "Pregunta 1/9 [Nivel 1] — Identificación Fonética (Question 1/9 [Level 1] — Phonetics)",
            "question_text": "¿Cuál palabra contiene la letra con tilde en español?\nWhich word contains an accented vowel in Spanish?",
            "options": [
                {"id": "a", "text": "Canción", "is_correct": True},
                {"id": "b", "text": "Mesa", "is_correct": False},
                {"id": "c", "text": "Casa", "is_correct": False},
                {"id": "d", "text": "Sol", "is_correct": False}
            ]
        },
        {
            "id": 2, "stage": 2, "difficulty": 2, "skill_type": "WRITE",
            "question_title": "Pregunta 2/9 [Nivel 2] — Ortografía y Escritura (Question 2/9 [Level 2] — Spelling)",
            "question_text": "Escriba la palabra correcta para el lugar donde se guardan libros:\nType the correct Spanish word for library:",
            "accepted_answers": ["Biblioteca", "biblioteca"]
        },
        {
            "id": 3, "stage": 3, "difficulty": 3, "skill_type": "SPEAK",
            "question_title": "Pregunta 3/9 [Nivel 3] — Pronunciación de Oraciones (Question 3/9 [Level 3] — Speech)",
            "question_text": "Presione el micrófono y pronuncie la siguiente oración\nPress microphone and speak aloud Spanish sentence:",
            "target_text": "El lenguaje transforma el conocimiento y la expresión humana"
        },
        {
            "id": 4, "stage": 4, "difficulty": 4, "skill_type": "READ",
            "question_title": "Pregunta 4/9 [Nivel 4] — Sinónimos y Vocabulario (Question 4/9 [Level 4] — Synonyms)",
            "question_text": "Seleccione el sinónimo exacto de la palabra 'PERSEVERANTE':\nSelect exact Spanish synonym for 'PERSEVERANTE':",
            "options": [
                {"id": "a", "text": "Constante y Determinado", "is_correct": True},
                {"id": "b", "text": "Temporal", "is_correct": False},
                {"id": "c", "text": "Dudoso", "is_correct": False},
                {"id": "d", "text": "Descuidado", "is_correct": False}
            ]
        },
        {
            "id": 5, "stage": 5, "difficulty": 5, "skill_type": "WRITE",
            "question_title": "Pregunta 5/9 [Nivel 5] — Gramática y Conjugación (Question 5/9 [Level 5] — Grammar)",
            "question_text": "Escriba el participio del verbo 'Escribir':\nType past participle of verb 'Escribir':",
            "accepted_answers": ["escrito", "Escrito"]
        },
        {
            "id": 6, "stage": 6, "difficulty": 6, "skill_type": "SPEAK",
            "question_title": "Pregunta 6/9 [Nivel 6] — Articulación Compleja (Question 6/9 [Level 6] — Articulation)",
            "question_text": "Presione el micrófono y lea la oración compleja en voz alta\nSpeak aloud complex Spanish sentence:",
            "target_text": "Aunque el camino sea desafiante la práctica constante brinda claridad y confianza"
        },
        {
            "id": 7, "stage": 7, "difficulty": 7, "skill_type": "READ",
            "question_title": "Pregunta 7/9 [Nivel 7] — Comprensión Literaria (Question 7/9 [Level 7] — Prose Reading)",
            "question_text": "Pasaje: 'El profundo silencio de la tarde traía paz al espíritu.' ¿Cuál es el tono principal?\nWhat is the primary tone of the passage?",
            "options": [
                {"id": "a", "text": "Tranquilidad y Paz", "is_correct": True},
                {"id": "b", "text": "Temor y Caos", "is_correct": False},
                {"id": "c", "text": "Ira y Enojo", "is_correct": False},
                {"id": "d", "text": "Ruido", "is_correct": False}
            ]
        },
        {
            "id": 8, "stage": 8, "difficulty": 8, "skill_type": "WRITE",
            "question_title": "Pregunta 8/9 [Nivel 8] — Ortografía Avanzada (Question 8/9 [Level 8] — Advanced Spelling)",
            "question_text": "Escriba la palabra correcta para la capacidad de hablar con elocuencia:\nType correct word for Eloquence:",
            "accepted_answers": ["Elocuencia", "elocuencia"]
        },
        {
            "id": 9, "stage": 9, "difficulty": 9, "skill_type": "SPEAK",
            "question_title": "Pregunta 9/9 [Nivel 9] — Fluidez Literaria Avanzada (Question 9/9 [Level 9] — High Fluency)",
            "question_text": "Presione el micrófono y pronuncie el pasaje literario con fluidez\nSpeak aloud advanced literary Spanish passage:",
            "target_text": "El dominio del lenguaje transforma el pensamiento en comunicación elocuente y sabiduría"
        }
    ]
}

LANGUAGE_BENCHMARKS = {
    "en": {
        "language_name": "English",
        "tiers": [
            {
                "tier": "FOUNDATIONAL",
                "score_range": "0 – 44 Marks",
                "title": "Alphabet & Phonemes Benchmark",
                "description": "Mastery over letter-sound associations, long/short vowel phonemes, and basic 2-letter syllable blends.",
                "competencies": ["Phoneme Identification", "Single Syllable Reading", "Simple Word Spelling"]
            },
            {
                "tier": "FUNCTIONAL",
                "score_range": "45 – 74 Marks",
                "title": "Vocabulary & Grammar Benchmark",
                "description": "Ability to form words with prefixes/suffixes, manage noun-verb agreement, and comprehend compound sentences.",
                "competencies": ["Synonym & Antonym Usage", "Verb Tense Conjugation", "Compound Sentence Reading"]
            },
            {
                "tier": "PROFICIENT",
                "score_range": "75 – 100 Marks",
                "title": "Advanced Literary Fluency Benchmark",
                "description": "Full competence in prose passage comprehension, orthography, and articulate public speech expression.",
                "competencies": ["Literary Passage Analysis", "Orthographic Accuracy", "Fluent Articulate Speech"]
            }
        ]
    },
    "te": {
        "language_name": "తెలుగు (Telugu)",
        "tiers": [
            {
                "tier": "FOUNDATIONAL",
                "score_range": "0 – 44 మార్కులు",
                "title": "అక్షరాలు మరియు గుణింతాల ప్రమాణం (Foundational Tier)",
                "description": "అచ్చులు, హల్లులు, గుణింతాల గుర్తులు మరియు ఒత్తులను గుర్తించి పలికే ప్రాథమిక సామర్థ్యం.",
                "competencies": ["అక్షర ధ్వని గుర్తింపు", "ప్రాథమిక పఠనం", "సరళ పద నిర్మాణం"]
            },
            {
                "tier": "FUNCTIONAL",
                "score_range": "45 – 74 మార్కులు",
                "title": "పదజాలం మరియు వ్యాకరణ ప్రమాణం (Functional Tier)",
                "description": "పర్యాయపదాలు, నానార్థాలు, సంధులు మరియు వాక్య వ్యాకరణంలో ప్రావీణ్యం సాధించే స్థాయి.",
                "competencies": ["పర్యాయపదాల ఉపయోగం", "తెలుగు సంధులు", "వాక్య నిర్మాణం"]
            },
            {
                "tier": "PROFICIENT",
                "score_range": "75 – 100 మార్కులు",
                "title": "ఉన్నత సాహిత్య ప్రవీణతా ప్రమాణం (Proficient Tier)",
                "description": "ఉన్నత సాహిత్య గద్యాలను అవగాహన చేసుకోవడం మరియు అనర్గళంగా భావ వ్యక్తీకరణ చేయడం.",
                "competencies": ["సాహిత్య అర్థ గ్రహణ", "అనర్గళ భాషా ప్రసంగం", "ప్రౌఢ పద రచన"]
            }
        ]
    },
    "hi": {
        "language_name": "हिन्दी (Hindi)",
        "tiers": [
            {
                "tier": "FOUNDATIONAL",
                "score_range": "0 – 44 अंक",
                "title": "वर्णमाला एवं मात्रा ज्ञान मानक (Foundational Tier)",
                "description": "स्वर, व्यंजन, मात्राओं एवं संयुक्त अक्षरों की सही पहचान तथा उच्चारण की क्षमता।",
                "competencies": ["वर्ण ध्वनि पहचान", "मात्रा ज्ञान", "सरल शब्द वाचन"]
            },
            {
                "tier": "FUNCTIONAL",
                "score_range": "45 – 74 अंक",
                "title": "शब्दावली एवं व्याकरण मानक (Functional Tier)",
                "description": "पर्यायवाची, विलोम शब्द, संधि एवं व्याकरणिक वाक्य संरचना में दक्षता।",
                "competencies": ["पर्यायवाची प्रयोग", "हिंदी संधि व समास", "शुद्ध वाक्य रचना"]
            },
            {
                "tier": "PROFICIENT",
                "score_range": "75 – 100 अंक",
                "title": "उच्च साहित्यिक निपुणता मानक (Proficient Tier)",
                "description": "साहित्यिक गद्यांशों की गंभीर समझ तथा धाराप्रवाह भाषाई अभिव्यक्ति की पूर्ण क्षमता।",
                "competencies": ["साहित्यिक बोध", "धाराप्रवाह अभिव्यक्ति", "प्रौढ़ शब्द प्रयोग"]
            }
        ]
    },
    "ta": {
        "language_name": "தமிழ் (Tamil)",
        "tiers": [
            {
                "tier": "FOUNDATIONAL",
                "score_range": "0 – 44 மதிப்பெண்கள்",
                "title": "எழுத்துக்கள் மற்றும் உயிர்மெய் தரநிலை (Foundational Tier)",
                "description": "உயிர் எழுத்துக்கள், மெய் எழுத்துக்கள் மற்றும் உயிர்மெய் எழுத்துக்களின் ஒலிப்பு முறை மற்றும் அடிப்படை வாசிப்பு திறன்.",
                "competencies": ["எழுத்து ஒலிப்பு அறிதல்", "அடிப்படை சொல் வாசிப்பு", "எளிய சொல் எழுதுதல்"]
            },
            {
                "tier": "FUNCTIONAL",
                "score_range": "45 – 74 மதிப்பெண்கள்",
                "title": "சொற்களஞ்சியம் மற்றும் இலக்கண தரநிலை (Functional Tier)",
                "description": "இணைச்சொற்கள், எதிர்ச்சொற்கள், தமிழ் புணர்ச்சி விதிகள் மற்றும் வாக்கிய அமைப்பில் தேர்ச்சி பெறும் நிலை.",
                "competencies": ["சொல் பயன்பாடு", "தமிழ் புணர்ச்சி இலக்கணம்", "சரியான வாக்கிய அமைப்பு"]
            },
            {
                "tier": "PROFICIENT",
                "score_range": "75 – 100 மதிப்பெண்கள்",
                "title": "உயர்ந்த இலக்கிய புலமை தரநிலை (Proficient Tier)",
                "description": "உயர்ந்த தமிழ் இலக்கிய உரைநடைகளைப் புரிந்து கொள்ளுதல் மற்றும் தெளிவான வாய்மொழி வெளிப்பாடு.",
                "competencies": ["இலக்கிய கருத்தறிதல்", "தெளிவான பேச்சாற்றல்", "உயர் நடை எழுத்தாக்கம்"]
            }
        ]
    },
    "bn": {
        "language_name": "বাংলা (Bengali)",
        "tiers": [
            {
                "tier": "FOUNDATIONAL",
                "score_range": "0 – 44 নম্বর",
                "title": "বর্ণমালা ও কার-ফলা জ্ঞান মানদণ্ড (Foundational Tier)",
                "description": "স্বরবর্ণ, ব্যঞ্জনবর্ণ, কার-ফলা এবং যুক্তবর্ণের সঠিক উচ্চারণ ও চেনার প্রাথমিক দক্ষতা।",
                "competencies": ["বর্ণ ও শব্দ চেনা", "কার-ফলা উচ্চারণ", "সহজ শব্দ লিখন"]
            },
            {
                "tier": "FUNCTIONAL",
                "score_range": "45 – 74 নম্বর",
                "title": "শব্দভাণ্ডার ও ব্যাকরণ মানদণ্ড (Functional Tier)",
                "description": "সমার্থক শব্দ, বিপরীত শব্দ, সন্ধি এবং সঠিক বাক্য গঠনে দক্ষতা অর্জনের স্তর।",
                "competencies": ["শব্দভাণ্ডার বিকাশ", "বাংলা সন্ধি ও সমাস", "সঠিক বাক্য গঠন"]
            },
            {
                "tier": "PROFICIENT",
                "score_range": "75 – 100 নম্বর",
                "title": "উচ্চ সাহিত্যিক দক্ষতা মানদণ্ড (Proficient Tier)",
                "description": "গদ্য সাহিত্য পাঠের গভীর বোধ এবং সাবলীল বাংলা ভাষা প্রকাশের পূর্ণ সক্ষমতা।",
                "competencies": ["সাহিত্য পাঠ বোধগম্যতা", "সাবলীল বাকপটুতা", "উচ্চাঙ্গের রচনা শৈলী"]
            }
        ]
    },
    "mr": {
        "language_name": "मराठी (Marathi)",
        "tiers": [
            {
                "tier": "FOUNDATIONAL",
                "score_range": "0 – 44 गुण",
                "title": "मुळाक्षरे व मात्रा ज्ञान मानक (Foundational Tier)",
                "description": "स्वर, व्यंजन, बाराखडी व जोडाक्षरांची अचूक ओळख व उच्चारणाची मूलभूत क्षमता.",
                "competencies": ["वर्ण ध्वनी ओळख", "बाराखडी वाचन", "सोप्या शब्दांचे लेखन"]
            },
            {
                "tier": "FUNCTIONAL",
                "score_range": "45 – 74 गुण",
                "title": "शब्दसंग्रह व व्याकरण मानक (Functional Tier)",
                "description": "समानार्थी शब्द, विरुद्धार्थी शब्द, संधी व वाक्यरचनेतील व्याकरणाचे ज्ञान.",
                "competencies": ["शब्दसंग्रह वाढवणे", "मराठी संधी व समास", "शुद्ध वाक्यरचना"]
            },
            {
                "tier": "PROFICIENT",
                "score_range": "75 – 100 गुण",
                "title": "उच्च साहित्यिक नैपुण्य मानक (Proficient Tier)",
                "description": "मराठी गद्य साहित्याचे आकलन आणि ओघवत्या भाषेतील अभिव्यक्तीची क्षमता.",
                "competencies": ["साहित्य आकलन", "ओघवती भाषण कला", "प्रौढ लेखन शैली"]
            }
        ]
    },
    "kn": {
        "language_name": "ಕನ್ನಡ (Kannada)",
        "tiers": [
            {
                "tier": "FOUNDATIONAL",
                "score_range": "0 – 44 ಅಂಕಗಳು",
                "title": "ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಕಾಗುಣಿತ ಪ್ರಮಾಣ (Foundational Tier)",
                "description": "ಸ್ವರಗಳು, ವ್ಯಂಜನಗಳು, ಕಾಗುಣಿತದ ಗುರುತುಗಳು ಮತ್ತು ಒತ್ತಕ್ಷರಗಳನ್ನು ಗುರುತಿಸಿ ಓದುವ ಸಾಮರ್ಥ್ಯ.",
                "competencies": ["ಅಕ್ಷರ ಧ್ವನಿ ಗುರುತಿಸುವಿಕೆ", "ಪ್ರಾಥಮಿಕ ವಾಚನ", "ಸರಳ ಪದ ರಚನೆ"]
            },
            {
                "tier": "FUNCTIONAL",
                "score_range": "45 – 74 ಅಂಕಗಳು",
                "title": "ಪದಸಂಪತ್ತು ಮತ್ತು ವ್ಯಾಕರಣ ಪ್ರಮಾಣ (Functional Tier)",
                "description": "ಸಮಾನಾರ್ಥಕ ಪದಗಳು, ವಿರುದ್ಧಾರ್ಥಕ ಪದಗಳು, ಸಂಧಿಗಳು ಮತ್ತು ವಾಕ್ಯ ವ್ಯಾಕರಣದಲ್ಲಿ ಪ್ರಾವೀಣ್ಯತೆ.",
                "competencies": ["ಪದಸಂಪತ್ತಿನ ಬಳಕೆ", "ಕನ್ನಡ ಸಂಧಿಗಳು", "ಶುದ್ಧ ವಾಕ್ಯ ರಚನೆ"]
            },
            {
                "tier": "PROFICIENT",
                "score_range": "75 – 100 ಅಂಕಗಳು",
                "title": "ಉನ್ನತ ಸಾಹಿತ್ಯಿಕ ಪ್ರಾವೀಣ್ಯತೆ ಪ್ರಮಾಣ (Proficient Tier)",
                "description": "ಉನ್ನತ ಕನ್ನಡ ಸಾಹಿತ್ಯದ ಗದ್ಯ ಭಾಗಗಳ ಅರ್ಥಗ್ರಹಣ ಮತ್ತು ಸ್ಪಷ್ಟ ವಾಕ್-ಸಂಪನ್ನತೆ.",
                "competencies": ["ಸಾಹಿತ್ಯ ಗ್ರಹಿಕೆ", "ಸ್ಪಷ್ಟ ವಾಕ್-ಪ್ರಸಂಗ", "ಪ್ರೌಢ ಶೈಲಿಯ ಬರವಣಿಗೆ"]
            }
        ]
    },
    "es": {
        "language_name": "Español (Spanish)",
        "tiers": [
            {
                "tier": "FOUNDATIONAL",
                "score_range": "0 – 44 Puntos",
                "title": "Estándar de Alfabeto y Fonética (Foundational Tier)",
                "description": "Dominio de la asociación letra-sonido, vocales acentuadas y sílabas básicas en español.",
                "competencies": ["Reconocimiento Fonético", "Lectura de Sílabas Simples", "Ortografía Básica"]
            },
            {
                "tier": "FUNCTIONAL",
                "score_range": "45 – 74 Puntos",
                "title": "Estándar de Vocabulario y Gramática (Functional Tier)",
                "description": "Capacidad para usar sinónimos, conjugación verbal y lectura comprensiva de oraciones complejas.",
                "competencies": ["Uso de Sinónimos", "Conjugación Gramatical", "Comprensión de Oraciones"]
            },
            {
                "tier": "PROFICIENT",
                "score_range": "75 – 100 Puntos",
                "title": "Estándar de Fluidez Literaria Avanzada (Proficient Tier)",
                "description": "Competencia completa en comprensión de textos literarios, ortografía avanzada y expresión oral articulada.",
                "competencies": ["Análisis Literario", "Precisión Ortográfica", "Expresión Oral Fluida"]
            }
        ]
    }
}

@router.get("/diagnostic-questions")
def get_diagnostic_questions(lang: str = Query("en", min_length=2, max_length=5)):
    clean_lang = lang.strip().lower()
    target_questions = DIAGNOSTIC_QUESTIONS_BY_LANG.get(clean_lang, DIAGNOSTIC_QUESTIONS_BY_LANG["en"])
    return target_questions

@router.get("/benchmarks")
def get_language_proficiency_benchmarks(lang: str = Query("en", min_length=2, max_length=5)):
    clean_lang = lang.strip().lower()
    target_benchmark = LANGUAGE_BENCHMARKS.get(clean_lang, LANGUAGE_BENCHMARKS["en"])
    return target_benchmark

class AnswerItem(BaseModel):
    stage: Optional[int] = None
    question_id: Optional[int] = None
    skill_type: str
    selected_option_id: Optional[str] = None
    written_text: Optional[str] = None
    spoken_text: Optional[str] = None
    is_correct: Optional[bool] = False

class AssessmentSubmission(BaseModel):
    lang: Optional[str] = "en"
    answers: List[AnswerItem]

@router.post("/submit")
def submit_initial_assessment(
    payload: AssessmentSubmission,
    current_learner: Optional[models.Learner] = Depends(get_optional_current_learner),
    db: Session = Depends(get_db)
):
    lang_code = (payload.lang or "en").lower()
    questions_list = DIAGNOSTIC_QUESTIONS_BY_LANG.get(lang_code, DIAGNOSTIC_QUESTIONS_BY_LANG["en"])
    question_map = {q["stage"]: q for q in questions_list}
    for q in questions_list:
        if "id" in q:
            question_map[q["id"]] = q

    # 1. Obtain Learner (from auth context or DB fallback) & Update current_lang_id (Step 1.3)
    learner_obj = current_learner or db.query(models.Learner).first()
    learner_id = learner_obj.learner_id if learner_obj else 1

    lang_record = db.query(models.Language).filter(models.Language.iso_code == lang_code).first()
    if lang_record and learner_obj:
        learner_obj.current_lang_id = lang_record.lang_id
        db.commit()

    # 2. Find or create Diagnostic Assessment DB record
    assessment_obj = db.query(models.Assessment).filter(
        models.Assessment.assessment_type == "DIAGNOSTIC",
        models.Assessment.title == f"Diagnostic Placement Test ({lang_code.upper()})"
    ).first()

    if not assessment_obj:
        assessment_obj = models.Assessment(
            assessment_type="DIAGNOSTIC",
            title=f"Diagnostic Placement Test ({lang_code.upper()})",
            total_marks=100
        )
        db.add(assessment_obj)
        db.commit()
        db.refresh(assessment_obj)

    correct_count = 0
    validated_details = []

    for idx, ans in enumerate(payload.answers):
        q_id = ans.stage or (idx + 1)
        q_def = question_map.get(q_id) or (questions_list[idx] if idx < len(questions_list) else None)

        is_q_correct = False
        user_answer_str = "No Answer Submitted"
        correct_answer_str = ""

        if q_def:
            skill_type = q_def.get("skill_type", "READ")

            if skill_type == "READ":
                selected = (ans.selected_option_id or "").strip().lower()
                user_opt = next((opt for opt in q_def.get("options", []) if opt.get("id", "").strip().lower() == selected), None)
                if user_opt:
                    user_answer_str = f"Option {user_opt.get('id', '').upper()}: {user_opt.get('text', '')}"
                elif ans.selected_option_id:
                    user_answer_str = f"Option {ans.selected_option_id.upper()}"

                correct_opt = next((opt for opt in q_def.get("options", []) if opt.get("is_correct")), None)
                if correct_opt:
                    correct_answer_str = f"Option {correct_opt.get('id', '').upper()}: {correct_opt.get('text', '')}"

                if correct_opt and selected == correct_opt.get("id", "").strip().lower():
                    is_q_correct = True

            elif skill_type == "WRITE":
                written = (ans.written_text or "").strip()
                if len(written) > 0:
                    user_answer_str = written

                accepted_list = q_def.get("accepted_answers", [])
                correct_answer_str = ", ".join(accepted_list) if accepted_list else ""

                if written and written.lower() in [a.strip().lower() for a in accepted_list]:
                    is_q_correct = True

            elif skill_type == "SPEAK":
                spoken = (ans.spoken_text or "").strip()
                if len(spoken) > 0:
                    user_answer_str = spoken
                else:
                    user_answer_str = "No Voice Speech Captured"

                target = (q_def.get("target_text") or "").strip()
                correct_answer_str = target

                if not spoken or len(spoken) == 0:
                    is_q_correct = False
                else:
                    import re
                    target_words = [re.sub(r'[^\w]', '', w) for w in target.lower().split() if len(re.sub(r'[^\w]', '', w)) > 1]
                    spoken_words = [re.sub(r'[^\w]', '', w) for w in spoken.lower().split() if len(re.sub(r'[^\w]', '', w)) > 1]
                    target_set = set(target_words)
                    matching_words = [w for w in spoken_words if w in target_set]
                    is_q_correct = len(target_words) > 0 and (len(matching_words) / len(target_words)) >= 0.5
        else:
            # Fallback if question id not found directly
            is_q_correct = bool(ans.is_correct)

        if is_q_correct:
            correct_count += 1

        # 3. Find or create AssessmentQuestion row in DB
        db_q = None
        if q_def:
            db_q = db.query(models.AssessmentQuestion).filter(
                models.AssessmentQuestion.assessment_id == assessment_obj.assessment_id,
                models.AssessmentQuestion.question_text == q_def.get("question_text")
            ).first()

            if not db_q:
                import json
                db_q = models.AssessmentQuestion(
                    assessment_id=assessment_obj.assessment_id,
                    question_text=q_def.get("question_text", ""),
                    question_type=q_def.get("skill_type", "READ"),
                    options_json=json.dumps(q_def.get("options", [])) if q_def.get("options") else None,
                    correct_answer=correct_answer_str
                )
                db.add(db_q)
                db.commit()
                db.refresh(db_q)

        # 4. Write individual question result to AssessmentResult table
        q_score = 12.0 if (idx == 8 and is_q_correct) else (11.0 if is_q_correct else 0.0)

        result_row = models.AssessmentResult(
            learner_id=learner_id,
            assessment_id=assessment_obj.assessment_id,
            question_id=db_q.question_id if db_q else None,
            score=q_score,
            is_correct=is_q_correct,
            user_answer=user_answer_str,
            attempt_no=1
        )
        db.add(result_row)
        db.flush()

        validated_details.append({
            "result_id": result_row.result_id,
            "db_question_id": db_q.question_id if db_q else None,
            "question_id": q_id,
            "stage": q_def.get("stage", idx + 1) if q_def else (idx + 1),
            "difficulty": q_def.get("difficulty", idx + 1) if q_def else (idx + 1),
            "skill_type": q_def.get("skill_type", "READ") if q_def else "READ",
            "question_title": q_def.get("question_title", f"Question {idx+1}/9") if q_def else f"Question {idx+1}/9",
            "question_text": q_def.get("question_text", "") if q_def else "",
            "user_answer": user_answer_str,
            "correct_answer": correct_answer_str,
            "is_correct": is_q_correct
        })

    db.commit()

    read_correct = sum(1 for v in validated_details if v["skill_type"] == "READ" and v["is_correct"])
    write_correct = sum(1 for v in validated_details if v["skill_type"] == "WRITE" and v["is_correct"])
    speak_correct = sum(1 for v in validated_details if v["skill_type"] == "SPEAK" and v["is_correct"])

    reading_score = min(33, read_correct * 11)
    writing_score = min(33, write_correct * 11)
    voice_score = 34 if speak_correct == 3 else (speak_correct * 11)

    total_score = reading_score + writing_score + voice_score

    skill_breakdown = {
        "reading_score": reading_score,
        "reading_max": 33,
        "writing_score": writing_score,
        "writing_max": 33,
        "voice_score": voice_score,
        "voice_max": 34
    }

    proficiency_level = "FOUNDATIONAL"
    if total_score >= 75:
        proficiency_level = "PROFICIENT"
    elif total_score >= 45:
        proficiency_level = "FUNCTIONAL"

    # Step 1.2: Calculate granular skill breakdown percentages
    reading_pct = round((reading_score / 33.0) * 100.0, 1)
    comprehension_pct = round((writing_score / 33.0) * 100.0, 1)
    voice_pct = round((voice_score / 34.0) * 100.0, 1)

    # Find or create LearnerProfile and update granular skill percentages
    learner_profile = db.query(models.LearnerProfile).filter(
        models.LearnerProfile.learner_id == learner_id
    ).first()

    if not learner_profile:
        learner_profile = models.LearnerProfile(
            learner_id=learner_id,
            literacy_level=proficiency_level,
            reading_pct=reading_pct,
            comprehension_pct=comprehension_pct,
            voice_pct=voice_pct
        )
        db.add(learner_profile)
    else:
        learner_profile.literacy_level = proficiency_level
        learner_profile.reading_pct = reading_pct
        learner_profile.comprehension_pct = comprehension_pct
        learner_profile.voice_pct = voice_pct

    db.commit()

    # Generate personalized learning path for the learner based on diagnostic test analysis using AI Learning Path Engine
    from app.services.learning_path_engine import generate_learning_path, get_active_path
    from app.routers.learning_path import generate_personalized_path

    # Trigger AI / Rule-Based Learning Path Engine
    try:
        engine_path_id = generate_learning_path(learner_id, db=db)
        ai_active_path = get_active_path(learner_id, db=db)
    except Exception as e:
        print(f"[AI ENGINE NOTICE] Learning path engine notice: {e}")
        ai_active_path = None

    target_lang_iso = payload.lang if hasattr(payload, 'lang') and payload.lang else None
    if not target_lang_iso and learner_obj and learner_obj.current_lang_id:
        lang_rec = db.query(models.Language).filter(models.Language.lang_id == learner_obj.current_lang_id).first()
        target_lang_iso = lang_rec.iso_code if lang_rec else "en"
    if not target_lang_iso:
        target_lang_iso = "en"

    # Execute personalized path generation for legacy frontend view compatibility
    import asyncio
    try:
        path_data = asyncio.run(generate_personalized_path(learner_id, target_lang_iso, db))
    except Exception as e:
        try:
            loop = asyncio.get_event_loop()
            path_data = loop.run_until_complete(generate_personalized_path(learner_id, target_lang_iso, db))
        except Exception:
            path_data = None

    if ai_active_path:
        target_prof = ai_active_path.get("target_proficiency", "BASIC")
        if not path_data:
            path_data = {}
        
        path_data["path_id"] = ai_active_path.get("path_id", 1)
        path_data["current_level"] = ai_active_path.get("current_level", proficiency_level)
        path_data["target_proficiency"] = target_prof
        path_data["path_title"] = f"AI-Generated Personalized Literacy Path ({proficiency_level} → {target_prof})"
        path_data["personalization_reason"] = f"Generated by AI Model based on diagnostic test analysis: Evaluated Reading, Writing, and Voice scores. Target proficiency goal set to {target_prof}."
        path_data["completion_percentage"] = path_data.get("completion_percentage", 0)
        path_data["path_lessons"] = ai_active_path.get("path_lessons", [])
        path_data["ai_active_path"] = ai_active_path

    return {
        "status": "success",
        "total_score": total_score,
        "correct_answers": correct_count,
        "total_questions": len(payload.answers) if payload.answers else len(questions_list),
        "proficiency_level": proficiency_level,
        "skill_breakdown": skill_breakdown,
        "learning_path": path_data,
        "validated_details": validated_details
    }
