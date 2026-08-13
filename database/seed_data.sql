-- ============================================================================
-- AksharAI Seed Data — Complete Multilingual Literacy Curriculums (8 Languages)
-- Languages: Hindi, English, Tamil, Telugu, Marathi, Bengali, Kannada, Spanish
-- ============================================================================

-- 1. Languages
INSERT INTO language (lang_id, lang_name, iso_code) VALUES
(1, 'Hindi (हिन्दी)', 'hi'),
(2, 'English', 'en'),
(3, 'Tamil (தமிழ்)', 'ta'),
(4, 'Telugu (తెలుగు)', 'te'),
(5, 'Marathi (मराठी)', 'mr'),
(6, 'Bengali (বাংলা)', 'bn'),
(7, 'Kannada (ಕನ್ನಡ)', 'kn'),
(8, 'Spanish (Español)', 'es')
ON CONFLICT (iso_code) DO NOTHING;

-- 2. Curriculums (1 FOUNDATIONAL per language = 8 total)
INSERT INTO curriculum (curriculum_id, lang_id, title, level, description) VALUES
(1, 1, 'हिन्दी भाषा साक्षरता एवं उच्च साहित्य (Hindi Literacy & Literature)', 'FOUNDATIONAL', 'सीखें वर्णमाला, शब्द संरचना, व्याकरण एवं साहित्यिक वाचन।'),
(2, 2, 'English Language Literacy & Advanced Fluency', 'FOUNDATIONAL', 'Master phonemes, vocabulary, grammar, and literary expression.'),
(3, 3, 'தமிழ் மொழி எழுத்தறிவு மற்றும் இலக்கியம் (Tamil Literacy & Literature)', 'FOUNDATIONAL', 'எழுத்துக்கள், சொற்கள், இலக்கணம் மற்றும் இலக்கிய வாசிப்பு.'),
(4, 4, 'తెలుగు భాషా అక్షరాస్యత మరియు సాహిత్య ప్రవీణత (Telugu Literacy & Literature)', 'FOUNDATIONAL', 'అక్షరాలు, గుణింతాలు, సంధులు, సమాసాలు మరియు సాహిత్య గద్య పఠనం.'),
(5, 5, 'मराठी भाषा साक्षरता व साहित्य (Marathi Literacy & Literature)', 'FOUNDATIONAL', 'वर्णमाला, शब्दसंग्रह, व्याकरण व साहित्यिक वाचन शिका.'),
(6, 6, 'বাংলা ভাষা সাক্ষরতা ও সাহিত্য (Bengali Literacy & Literature)', 'FOUNDATIONAL', 'বর্ণমালা, শব্দভাণ্ডার, ব্যাকরণ ও সাহিত্যিক পাঠ শিখুন।'),
(7, 7, 'ಕನ್ನಡ ಭಾಷಾ ಸಾಕ್ಷರತೆ ಮತ್ತು ಸಾಹಿತ್ಯ (Kannada Literacy & Literature)', 'FOUNDATIONAL', 'ಅಕ್ಷರಮಾಲೆ, ಶಬ್ದಕೋಶ, ವ್ಯಾಕರಣ ಮತ್ತು ಸಾಹಿತ್ಯ ಓದುವಿಕೆ ಕಲಿಯಿರಿ.'),
(8, 8, 'Alfabetización y Literatura en Español (Spanish Literacy & Literature)', 'FOUNDATIONAL', 'Dominio del alfabeto, vocabulario, gramática y expresión literaria.')
ON CONFLICT (curriculum_id) DO NOTHING;

-- 3. Modules (4 per curriculum = 32 total)
INSERT INTO module (module_id, curriculum_id, module_name, sequence_no, skill_type) VALUES
-- Hindi (curriculum 1)
(1, 1, 'वर्णमाला एवं मात्रा ज्ञान (Alphabet & Phonemes)', 1, 'Reading & Pronunciation'),
(2, 1, 'शब्दावली एवं शब्द निर्माण (Vocabulary & Words)', 2, 'Word Formation'),
(3, 1, 'व्याकरण एवं वाक्य संरचना (Grammar & Syntax)', 3, 'Grammar'),
(4, 1, 'उच्च साहित्यिक वाचन (Literary Fluency)', 4, 'Literature'),
-- English (curriculum 2)
(5, 2, 'Phonemes & Alphabet Fundamentals', 1, 'Reading & Pronunciation'),
(6, 2, 'Vocabulary & Word Formation', 2, 'Word Formation'),
(7, 2, 'Sentence Grammar & Syntax', 3, 'Grammar'),
(8, 2, 'Advanced Literary Fluency', 4, 'Literature'),
-- Tamil (curriculum 3)
(9, 3, 'எழுத்துக்கள் மற்றும் ஒலிகள் (Alphabet & Phonemes - Tamil)', 1, 'Reading & Pronunciation'),
(10, 3, 'சொற்களஞ்சியம் மற்றும் சொல் உருவாக்கம் (Vocabulary & Words - Tamil)', 2, 'Word Formation'),
(11, 3, 'இலக்கணம் மற்றும் வாக்கிய அமைப்பு (Grammar & Syntax - Tamil)', 3, 'Grammar'),
(12, 3, 'உயர் இலக்கிய வாசிப்பு (Literary Fluency - Tamil)', 4, 'Literature'),
-- Telugu (curriculum 4)
(13, 4, 'అక్షరాలు, వర్ణమాల మరియు గుణింతాలు (Alphabet & Phonemes - Telugu)', 1, 'Reading & Pronunciation'),
(14, 4, 'పదజాలం మరియు పద నిర్మాణం (Vocabulary & Words - Telugu)', 2, 'Word Formation'),
(15, 4, 'సంధులు, సమాసాలు మరియు వ్యాకరణం (Grammar & Syntax - Telugu)', 3, 'Grammar'),
(16, 4, 'సాహిత్య గద్య పఠనం (Literary Fluency - Telugu)', 4, 'Literature'),
-- Marathi (curriculum 5)
(17, 5, 'वर्णमाला व ध्वनी ओळख (Alphabet & Phonemes - Marathi)', 1, 'Reading & Pronunciation'),
(18, 5, 'शब्दसंग्रह व शब्दनिर्मिती (Vocabulary & Words - Marathi)', 2, 'Word Formation'),
(19, 5, 'व्याकरण व वाक्यरचना (Grammar & Syntax - Marathi)', 3, 'Grammar'),
(20, 5, 'उच्च साहित्यिक वाचन (Literary Fluency - Marathi)', 4, 'Literature'),
-- Bengali (curriculum 6)
(21, 6, 'বর্ণমালা ও ধ্বনি পরিচয় (Alphabet & Phonemes - Bengali)', 1, 'Reading & Pronunciation'),
(22, 6, 'শব্দভাণ্ডার ও শব্দগঠন (Vocabulary & Words - Bengali)', 2, 'Word Formation'),
(23, 6, 'ব্যাকরণ ও বাক্যগঠন (Grammar & Syntax - Bengali)', 3, 'Grammar'),
(24, 6, 'উচ্চ সাহিত্যিক পাঠ (Literary Fluency - Bengali)', 4, 'Literature'),
-- Kannada (curriculum 7)
(25, 7, 'ಅಕ್ಷರಮಾಲೆ ಮತ್ತು ಉಚ್ಚಾರಣೆ (Alphabet & Phonemes - Kannada)', 1, 'Reading & Pronunciation'),
(26, 7, 'ಶಬ್ದಕೋಶ ಮತ್ತು ಪದರಚನೆ (Vocabulary & Words - Kannada)', 2, 'Word Formation'),
(27, 7, 'ವ್ಯಾಕರಣ ಮತ್ತು ವಾಕ್ಯರಚನೆ (Grammar & Syntax - Kannada)', 3, 'Grammar'),
(28, 7, 'ಸಾಹಿತ್ಯಿಕ ಓದುವಿಕೆ (Literary Fluency - Kannada)', 4, 'Literature'),
-- Spanish (curriculum 8)
(29, 8, 'Fonemas y Fundamentos del Alfabeto (Alphabet & Phonemes - Spanish)', 1, 'Reading & Pronunciation'),
(30, 8, 'Vocabulario y Formación de Palabras (Vocabulary & Words - Spanish)', 2, 'Word Formation'),
(31, 8, 'Gramática y Sintaxis de Oraciones (Grammar & Syntax - Spanish)', 3, 'Grammar'),
(32, 8, 'Fluidez Literaria Avanzada (Literary Fluency - Spanish)', 4, 'Literature')
ON CONFLICT (module_id) DO NOTHING;

-- 4. Lessons (2 per module = 64 total)
INSERT INTO lesson (lesson_id, module_id, title, content_type, content_url, target_text, phonetic_script, difficulty_level) VALUES
-- Hindi Lessons (modules 1-4)
(1, 1, 'स्वर एवं व्यंजन उच्चारण', 'Voice Practice', '/audio/hi/phonetics.mp3', 'भाषा विचारों को अभिव्यक्त करने का अमूल्य माध्यम है', '["भा-षा", "वि-चा-रों", "अ-भि-व्य-क्त"]', 'FOUNDATIONAL'),
(2, 1, 'मात्राएँ एवं संयुक्त अक्षर', 'Voice Practice', '/audio/hi/matras.mp3', 'कृपा और क्षमा मानव जीवन के आधार हैं', '["कृ-पा", "क्ष-मा", "मा-न-व"]', 'FUNCTIONAL'),
(3, 2, 'पर्यायवाची एवं विलोम शब्द', 'Functional Reading', '/audio/hi/vocabulary.mp3', 'सूर्य और दिनकर प्रकाश के प्रतीक हैं', '["सू-र्य", "दिन-कर", "प्र-का-श"]', 'FOUNDATIONAL'),
(4, 2, 'शब्द निर्माण एवं उपसर्ग प्रत्यय', 'Functional Reading', '/audio/hi/words.mp3', 'विद्यालय में विद्यार्थी ज्ञान प्राप्त करते हैं', '["विद्-या-ल-य", "ज्ञा-न"]', 'FUNCTIONAL'),
(5, 3, 'हिंदी संधि एवं समास', 'Functional Reading', '/audio/hi/grammar.mp3', 'विद्या और आलय से मिलकर विद्यालय बनता है', '["विद्-या-ल-य", "सं-धि"]', 'FOUNDATIONAL'),
(6, 3, 'शुद्ध वाक्य रचना एवं व्याकरण', 'Functional Reading', '/audio/hi/syntax.mp3', 'राम ने श्याम को पुस्तक दी जो बहुत अच्छी थी', '["पु-स्त-क", "व्या-क-र-ण"]', 'FUNCTIONAL'),
(7, 4, 'साहित्यिक गद्यांश वाचन', 'Voice Practice', '/audio/hi/passage.mp3', 'साहित्य का अनुशीलन मानव चेतना और व्यक्तित्व विकास का शाश्वत स्रोत है', '["सा-हि-त्य", "चे-त-ना"]', 'FOUNDATIONAL'),
(8, 4, 'धाराप्रवाह भाषा अभिव्यक्ति', 'Voice Practice', '/audio/hi/fluency.mp3', 'निरंतर अभ्यास और अध्ययन से ही भाषा में निपुणता प्राप्त होती है', '["नि-रं-त-र", "नि-पु-ण-ता"]', 'FUNCTIONAL'),

-- English Lessons (modules 5-8)
(9, 5, 'Vowel Sounds & Phoneme Synthesis', 'Voice Practice', '/audio/en/phonetics.mp3', 'Language unlocks knowledge, wisdom, and human expression', '["Lan-guage", "un-locks", "know-ledge"]', 'FOUNDATIONAL'),
(10, 5, 'Consonant Blends & Syllables', 'Voice Practice', '/audio/en/syllables.mp3', 'Graceful articulation requires patience and practice', '["Grace-ful", "ar-ti-cu-la-tion"]', 'FUNCTIONAL'),
(11, 6, 'Prefixes, Suffixes & Root Words', 'Functional Reading', '/audio/en/vocabulary.mp3', 'Understanding root words enhances vocabulary comprehension', '["Un-der-stand-ing", "vo-ca-bu-la-ry"]', 'FOUNDATIONAL'),
(12, 6, 'Synonyms & Antonyms Mastery', 'Functional Reading', '/audio/en/synonyms.mp3', 'Persist with determination to achieve true fluency', '["Per-sist", "de-ter-mi-na-tion"]', 'FUNCTIONAL'),
(13, 7, 'Noun-Verb Agreement & Tenses', 'Functional Reading', '/audio/en/grammar.mp3', 'She had written an eloquent essay before sunrise', '["writ-ten", "el-o-quent", "es-say"]', 'FOUNDATIONAL'),
(14, 7, 'Complex Sentence Construction', 'Functional Reading', '/audio/en/syntax.mp3', 'Although the journey was long the destination proved worthwhile', '["jour-ney", "des-ti-na-tion"]', 'FUNCTIONAL'),
(15, 8, 'Prose & Passage Comprehension', 'Voice Practice', '/audio/en/passage.mp3', 'Mastery over language transforms thought into eloquent communication', '["Mas-te-ry", "trans-forms", "com-mu-ni-ca-tion"]', 'FOUNDATIONAL'),
(16, 8, 'Fluent Speech & Public Articulation', 'Voice Practice', '/audio/en/fluency.mp3', 'The profound silence of evening was broken by the gentle rustle of leaves', '["pro-found", "si-lence", "gen-tle"]', 'FUNCTIONAL'),

-- Tamil Lessons (modules 9-12)
(17, 9, 'உயிர் எழுத்துக்கள் மற்றும் மெய் எழுத்துக்கள்', 'Voice Practice', '/audio/ta/phonetics.mp3', 'மொழி மனித எண்ணங்களின் உயரிய வெளிப்பாடாகும்', '["மொ-ழி", "எண்-ணங்-க-ளின்"]', 'FOUNDATIONAL'),
(18, 9, 'உயிர்மெய் எழுத்துக்கள் மற்றும் கூட்டெழுத்து', 'Voice Practice', '/audio/ta/syllables.mp3', 'அறிவும் கல்வியும் வாழ்வின் அடிப்படை ஆகும்', '["அ-றி-வும்", "கல்-வி-யும்"]', 'FUNCTIONAL'),
(19, 10, 'இணைச்சொற்கள் மற்றும் எதிர்ச்சொற்கள்', 'Functional Reading', '/audio/ta/vocabulary.mp3', 'பரிதி என்பது சூரியனின் மறுபெயர் ஆகும்', '["ப-ரி-தி", "சூ-ரி-ய-னின்"]', 'FOUNDATIONAL'),
(20, 10, 'சொல்லாக்கம் மற்றும் பொருள் விளக்கம்', 'Functional Reading', '/audio/ta/words.mp3', 'நூலகம் என்பது நூல்களின் சேமிப்புக் கிடங்கு ஆகும்', '["நூ-ல-கம்", "சே-மிப்-பு"]', 'FUNCTIONAL'),
(21, 11, 'புணர்ச்சி விதிகள் மற்றும் இலக்கணம்', 'Functional Reading', '/audio/ta/grammar.mp3', 'தமிழ் மொழி இலக்கணம் மிகவும் பழமையானது', '["இ-லக்-க-ணம்", "ப-ழ-மை"]', 'FOUNDATIONAL'),
(22, 11, 'வாக்கிய அமைப்பு மற்றும் தொடர் நிலை', 'Functional Reading', '/audio/ta/syntax.mp3', 'கல்வி கற்றவன் கண் இருப்பவனுக்கு நிகர்', '["கல்-வி", "கற்-ற-வன்"]', 'FUNCTIONAL'),
(23, 12, 'இலக்கிய உரைநடை வாசிப்பு', 'Voice Practice', '/audio/ta/passage.mp3', 'இலக்கியப் பயிற்சி மனித உணர்வுகளையும் ஆளுமையையும் உயர்த்தும் வற்றாத ஊற்றாகும்', '["இ-லக்-கி-யம்", "ஊற்-றா-கும்"]', 'FOUNDATIONAL'),
(24, 12, 'சரளமான பேச்சாற்றல் பயிற்சி', 'Voice Practice', '/audio/ta/fluency.mp3', 'தொடர் பயிற்சியும் தீவிர முயற்சியும் மட்டுமே மொழியில் தேர்ச்சியைத் தரும்', '["ப-யிற்-சி", "தேர்ச்-சி"]', 'FUNCTIONAL'),

-- Telugu Lessons (modules 13-16)
(25, 13, 'అచ్చులు మరియు హల్లుల ఉచ్చారణ', 'Voice Practice', '/audio/te/phonetics.mp3', 'భాష అనేది ఆలోచనలకు రూపాన్ని ఇచ్చే అమూల్యమైన సాధనం', '["భా-ష", "ఆ-లో-చ-న-లు"]', 'FOUNDATIONAL'),
(26, 13, 'గుణింతాలు మరియు ఒత్తుల సాధన', 'Voice Practice', '/audio/te/syllables.mp3', 'కృప మరియు కరుణతో కూడిన మాటలు సమాజాన్ని రక్షిస్తాయి', '["కృ-ప", "క-రు-ణ"]', 'FUNCTIONAL'),
(27, 14, 'పర్యాయపదాలు మరియు నానార్థాలు', 'Functional Reading', '/audio/te/vocabulary.mp3', 'అమృతం అనగా సుధ మరియు పీయూషము', '["అ-మృ-తం", "సు-ధ"]', 'FOUNDATIONAL'),
(28, 14, 'పద నిర్మాణం మరియు అర్థ విశ్లేషణ', 'Functional Reading', '/audio/te/words.mp3', 'విద్యాలయం అనగా విద్య నేర్చుకునే ప్రదేశం', '["విద్-యా-ల-యం", "ప్ర-దే-శం"]', 'FUNCTIONAL'),
(29, 15, 'తెలుగు సంధులు మరియు సమాసాలు', 'Functional Reading', '/audio/te/grammar.mp3', 'దేవ మరియు ఆలయం కలిస్తే దేవాలయము అవుతుంది', '["దే-వా-ల-య-ము", "సం-ధి"]', 'FOUNDATIONAL'),
(30, 15, 'వాక్య నిర్మాణం మరియు వ్యాకరణం', 'Functional Reading', '/audio/te/syntax.mp3', 'నిరంతర సాధన ద్వారా భాషా ప్రావీణ్యం లభిస్తుంది', '["నిరం-త-ర", "ప్రా-వీ-ణ్యం"]', 'FUNCTIONAL'),
(31, 16, 'సాహిత్య గద్య పఠనం మరియు అర్థ గ్రహణ', 'Voice Practice', '/audio/te/passage.mp3', 'సాహిత్యానుశీలనం మానవ చైతన్యానికి మరియు వ్యక్తిత్వ వికాసానికి అక్షయమైన నిధి', '["సా-హి-త్యా-ను-శీ-ల-నం"]', 'FOUNDATIONAL'),
(32, 16, 'అనర్గళ భాషా ప్రసంగం', 'Voice Practice', '/audio/te/fluency.mp3', 'నిరంతర సాధన మరియు అధ్యయనం ద్వారా మాత్రమే భాషా ప్రావీణ్యం లభిస్తుంది', '["నిరం-త-ర", "అధ్య-య-నం"]', 'FUNCTIONAL'),

-- Marathi Lessons (modules 17-20)
(33, 17, 'स्वर व व्यंजन उच्चारण', 'Voice Practice', '/audio/mr/phonetics.mp3', 'भाषा ही विचारांना व्यक्त करण्याचे अमूल्य साधन आहे', '["भा-षा", "वि-चा-रां-ना"]', 'FOUNDATIONAL'),
(34, 17, 'मात्रा व जोडाक्षरे', 'Voice Practice', '/audio/mr/syllables.mp3', 'कृपा आणि क्षमा हे मानवी जीवनाचे आधारस्तंभ आहेत', '["कृ-पा", "क्ष-मा"]', 'FUNCTIONAL'),
(35, 18, 'समानार्थी व विरुद्धार्थी शब्द', 'Functional Reading', '/audio/mr/vocabulary.mp3', 'भास्कर हा सूर्याचा समानार्थी शब्द आहे', '["भा-स्क-र", "सू-र्या-चा"]', 'FOUNDATIONAL'),
(36, 18, 'शब्दनिर्मिती व उपसर्ग प्रत्यय', 'Functional Reading', '/audio/mr/words.mp3', 'ग्रंथालय म्हणजे पुस्तकांचे संग्रहालय', '["ग्रं-था-ल-य", "सं-ग्र-हा-ल-य"]', 'FUNCTIONAL'),
(37, 19, 'मराठी संधी व समास', 'Functional Reading', '/audio/mr/grammar.mp3', 'विद्या आणि आलय यांचा संधी विद्यालय होतो', '["विद्-या-ल-य", "सं-धी"]', 'FOUNDATIONAL'),
(38, 19, 'शुद्ध वाक्यरचना व व्याकरण', 'Functional Reading', '/audio/mr/syntax.mp3', 'सततचा सराव आणि अभ्यासानेच भाषेत प्रगती होते', '["स-रा-व", "प्र-ग-ती"]', 'FUNCTIONAL'),
(39, 20, 'साहित्यिक उतारा वाचन', 'Voice Practice', '/audio/mr/passage.mp3', 'साहित्याचा अभ्यास मानवी चेतना आणि व्यक्तिमत्त्व विकासाचा अक्षय स्रोत आहे', '["सा-हि-त्या-चा", "चे-त-ना"]', 'FOUNDATIONAL'),
(40, 20, 'धाराप्रवाह भाषा व्यक्तीकरण', 'Voice Practice', '/audio/mr/fluency.mp3', 'संध्याकाळची शांतता मनाला असीम समाधान देते', '["शां-त-ता", "स-मा-धा-न"]', 'FUNCTIONAL'),

-- Bengali Lessons (modules 21-24)
(41, 21, 'স্বরবর্ণ ও ব্যঞ্জনবর্ণ উচ্চারণ', 'Voice Practice', '/audio/bn/phonetics.mp3', 'ভাষা মানুষের চিন্তাকে রূপ দেওয়ার অমূল্য বাহন', '["ভা-ষা", "মা-নু-ষের"]', 'FOUNDATIONAL'),
(42, 21, 'মাত্রা ও যুক্তাক্ষর অভ্যাস', 'Voice Practice', '/audio/bn/syllables.mp3', 'কৃপা ও ক্ষমা মানব জীবনের ভিত্তি', '["কৃ-পা", "ক্ষ-মা"]', 'FUNCTIONAL'),
(43, 22, 'সমার্থক ও বিপরীতার্থক শব্দ', 'Functional Reading', '/audio/bn/vocabulary.mp3', 'রবি হলো সূর্যের সমার্থক শব্দ', '["র-বি", "সূ-র্যের"]', 'FOUNDATIONAL'),
(44, 22, 'শব্দগঠন ও উপসর্গ প্রত্যয়', 'Functional Reading', '/audio/bn/words.mp3', 'গ্রন্থাগার মানে বইয়ের সংগ্রহশালা', '["গ্রন্-থা-গা-র", "সং-গ্র-হ"]', 'FUNCTIONAL'),
(45, 23, 'বাংলা সন্ধি ও সমাস', 'Functional Reading', '/audio/bn/grammar.mp3', 'বিদ্যা ও আলয় যুক্ত হলে বিদ্যালয় হয়', '["বিদ্-যা-ল-য়", "স-ন্ধি"]', 'FOUNDATIONAL'),
(46, 23, 'শুদ্ধ বাক্যগঠন ও ব্যাকরণ', 'Functional Reading', '/audio/bn/syntax.mp3', 'নিরন্তর সাধনা ও অধ্যবসায়ের দ্বারাই ভাষার দক্ষতা অর্জন সম্ভব', '["নি-রন্-তর", "দক্ষ-তা"]', 'FUNCTIONAL'),
(47, 24, 'সাহিত্যিক গদ্য পাঠ', 'Voice Practice', '/audio/bn/passage.mp3', 'সাহিত্যের অনুশীলন মানব চেতনা ও ব্যক্তিত্ব বিকাশের শাশ্বত উৎস', '["সা-হি-ত্যের", "চে-ত-না"]', 'FOUNDATIONAL'),
(48, 24, 'সাবলীল ভাষা প্রকাশ', 'Voice Practice', '/audio/bn/fluency.mp3', 'সন্ধ্যাবেলার শান্ত পরিবেশ মনকে আনন্দ দেয়', '["শা-ন্ত", "আ-ন-ন্দ"]', 'FUNCTIONAL'),

-- Kannada Lessons (modules 25-28)
(49, 25, 'ಸ್ವರ ಮತ್ತು ವ್ಯಂಜನ ಉಚ್ಚಾರಣೆ', 'Voice Practice', '/audio/kn/phonetics.mp3', 'ಭಾಷೆಯು ವಿಚಾರಗಳನ್ನು ವ್ಯಕ್ತಪಡಿಸುವ ಅಮೂಲ್ಯವಾದ ಸಾಧನವಾಗಿದೆ', '["ಭಾ-ಷೆ", "ವಿ-ಚಾ-ರ"]', 'FOUNDATIONAL'),
(50, 25, 'ಗುಣಿತಾಕ್ಷರ ಮತ್ತು ಒತ್ತಕ್ಷರ ಅಭ್ಯಾಸ', 'Voice Practice', '/audio/kn/syllables.mp3', 'ಕೃಪೆ ಮತ್ತು ಕರುಣೆ ಮಾನವ ಜೀವನದ ಆಧಾರ', '["ಕೃ-ಪೆ", "ಕ-ರು-ಣೆ"]', 'FUNCTIONAL'),
(51, 26, 'ಸಮಾನಾರ್ಥಕ ಮತ್ತು ವಿರುದ್ಧಾರ್ಥಕ ಪದಗಳು', 'Functional Reading', '/audio/kn/vocabulary.mp3', 'ರವಿ ಎಂಬುದು ಸೂರ್ಯನ ಸಮಾನಾರ್ಥಕ ಪದ', '["ರ-ವಿ", "ಸೂ-ರ್ಯ"]', 'FOUNDATIONAL'),
(52, 26, 'ಪದರಚನೆ ಮತ್ತು ಉಪಸರ್ಗ ಪ್ರತ್ಯಯ', 'Functional Reading', '/audio/kn/words.mp3', 'ಗ್ರಂಥಾಲಯ ಎಂದರೆ ಪುಸ್ತಕಗಳ ಭಂಡಾರ', '["ಗ್ರಂ-ಥಾ-ಲ-ಯ", "ಭಂ-ಡಾ-ರ"]', 'FUNCTIONAL'),
(53, 27, 'ಕನ್ನಡ ಸಂಧಿ ಮತ್ತು ಸಮಾಸ', 'Functional Reading', '/audio/kn/grammar.mp3', 'ದೇವ ಮತ್ತು ಆಲಯ ಸೇರಿ ದೇವಾಲಯ ಆಗುತ್ತದೆ', '["ದೇ-ವಾ-ಲ-ಯ", "ಸಂ-ಧಿ"]', 'FOUNDATIONAL'),
(54, 27, 'ಶುದ್ಧ ವಾಕ್ಯರಚನೆ ಮತ್ತು ವ್ಯಾಕರಣ', 'Functional Reading', '/audio/kn/syntax.mp3', 'ನಿರಂತರ ಅಭ್ಯಾಸ ಮತ್ತು ಅಧ್ಯಯನದಿಂದ ಮಾತ್ರ ಭಾಷೆಯಲ್ಲಿ ಪಾಂಡಿತ್ಯ ಸಿಗುತ್ತದೆ', '["ನಿ-ರಂ-ತ-ರ", "ಪಾಂ-ಡಿ-ತ್ಯ"]', 'FUNCTIONAL'),
(55, 28, 'ಸಾಹಿತ್ಯಿಕ ಗದ್ಯ ಓದುವಿಕೆ', 'Voice Practice', '/audio/kn/passage.mp3', 'ಸಾಹಿತ್ಯದ ಅಧ್ಯಯನವು ಮಾನವ ಚೇತನ ಮತ್ತು ವ್ಯಕ್ತಿತ್ವ ವಿಕಾಸದ ಅಕ್ಷಯ ಮೂಲವಾಗಿದೆ', '["ಸಾ-ಹಿ-ತ್ಯ", "ಚೇ-ತ-ನ"]', 'FOUNDATIONAL'),
(56, 28, 'ಸರಳ ಭಾಷಾ ಅಭಿವ್ಯಕ್ತಿ', 'Voice Practice', '/audio/kn/fluency.mp3', 'ಸಂಜೆಯ ಪ್ರಶಾಂತ ವಾತಾವರಣವು ಮನಸ್ಸಿಗೆ ಸಂತಸ ನೀಡುತ್ತದೆ', '["ಪ್ರ-ಶಾಂ-ತ", "ಸಂ-ತ-ಸ"]', 'FUNCTIONAL'),

-- Spanish Lessons (modules 29-32)
(57, 29, 'Sonidos Vocálicos y Síntesis Fonémica', 'Voice Practice', '/audio/es/phonetics.mp3', 'El lenguaje transforma el conocimiento y la expresión humana', '["len-gua-je", "trans-for-ma"]', 'FOUNDATIONAL'),
(58, 29, 'Combinaciones de Consonantes y Sílabas', 'Voice Practice', '/audio/es/syllables.mp3', 'La articulación clara requiere paciencia y práctica constante', '["ar-ti-cu-la-ción", "pa-cien-cia"]', 'FUNCTIONAL'),
(59, 30, 'Prefijos, Sufijos y Raíces de Palabras', 'Functional Reading', '/audio/es/vocabulary.mp3', 'Comprender las raíces de las palabras mejora la comprensión', '["com-pren-der", "ra-í-ces"]', 'FOUNDATIONAL'),
(60, 30, 'Sinónimos y Antónimos', 'Functional Reading', '/audio/es/synonyms.mp3', 'Perseverar con determinación para lograr la verdadera fluidez', '["per-se-ve-rar", "de-ter-mi-na-ción"]', 'FUNCTIONAL'),
(61, 31, 'Concordancia Sustantivo-Verbo y Tiempos', 'Functional Reading', '/audio/es/grammar.mp3', 'Ella había escrito un ensayo elocuente antes del amanecer', '["es-cri-to", "e-lo-cuen-te"]', 'FOUNDATIONAL'),
(62, 31, 'Construcción de Oraciones Complejas', 'Functional Reading', '/audio/es/syntax.mp3', 'Aunque el viaje fue largo el destino resultó valioso', '["via-je", "des-ti-no"]', 'FUNCTIONAL'),
(63, 32, 'Comprensión de Prosa y Pasajes', 'Voice Practice', '/audio/es/passage.mp3', 'El dominio del lenguaje transforma el pensamiento en comunicación elocuente', '["do-mi-nio", "co-mu-ni-ca-ción"]', 'FOUNDATIONAL'),
(64, 32, 'Expresión Oral Fluida', 'Voice Practice', '/audio/es/fluency.mp3', 'La práctica continua y la dedicación son la clave del dominio lingüístico', '["prác-ti-ca", "do-mi-nio"]', 'FUNCTIONAL')
ON CONFLICT (lesson_id) DO NOTHING;
