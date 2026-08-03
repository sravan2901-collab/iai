-- ============================================================================
-- AksharAI Seed Data (Pure Language Literacy Curriculums across Languages)
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

-- 2. Curriculums for All Languages
INSERT INTO curriculum (curriculum_id, lang_id, title, level, description) VALUES
(1, 1, 'हिन्दी भाषा साक्षरता एवं उच्च साहित्य (Hindi Literacy & Literature)', 'FOUNDATIONAL', 'सीखें वर्णमाला, शब्द संरचना, व्याकरण एवं साहित्यिक वाचन।'),
(2, 2, 'English Language Literacy & Advanced Fluency', 'FOUNDATIONAL', 'Master phonemes, vocabulary, grammar, and literary expression.'),
(3, 3, 'தமிழ் மொழி எழுத்தறிவு மற்றும் இலக்கியம் (Tamil Literacy & Literature)', 'FOUNDATIONAL', 'எழுத்துக்கள், சொற்கள், இலக்கணம் மற்றும் இலக்கிய வாசிப்பு.'),
(4, 4, 'తెలుగు భాషా అక్షరాస్యత మరియు సాహిత్య ప్రవీణత (Telugu Literacy & Literature)', 'FOUNDATIONAL', 'అక్షరాలు, గుణింతాలు, సంధులు, సమాసాలు మరియు సాహిత్య గద్య పఠనం.')
ON CONFLICT (curriculum_id) DO NOTHING;

-- 3. Modules across Curriculums
INSERT INTO module (module_id, curriculum_id, module_name, sequence_no, skill_type) VALUES
(1, 1, 'वर्णमाला एवं मात्रा ज्ञान (Alphabet & Phonemes)', 1, 'Reading & Pronunciation'),
(2, 1, 'शब्दावली एवं शब्द निर्माण (Vocabulary & Words)', 2, 'Word Formation'),
(3, 1, 'व्याकरण एवं वाक्य संरचना (Grammar & Syntax)', 3, 'Grammar'),
(4, 1, 'उच्च साहित्यिक वाचन (Literary Fluency)', 4, 'Literature'),

(5, 2, 'Phonemes & Alphabet Fundamentals', 1, 'Reading & Pronunciation'),
(6, 2, 'Vocabulary & Word Formation', 2, 'Word Formation'),
(7, 2, 'Sentence Grammar & Syntax', 3, 'Grammar'),
(8, 2, 'Advanced Literary Fluency', 4, 'Literature'),

(9, 4, 'అక్షరాలు, వర్ణమాల మరియు గుణింతాలు (Alphabet & Phonemes - Telugu)', 1, 'Reading & Pronunciation'),
(10, 4, 'పదజాలం మరియు పద నిర్మాణం (Vocabulary & Words - Telugu)', 2, 'Word Formation'),
(11, 4, 'సంధులు, సమాసాలు మరియు వ్యాకరణం (Grammar & Syntax - Telugu)', 3, 'Grammar'),
(12, 4, 'సాహిత్య గద్య పఠనం (Literary Fluency - Telugu)', 4, 'Literature')
ON CONFLICT (module_id) DO NOTHING;

-- 4. Lessons
INSERT INTO lesson (lesson_id, module_id, title, content_type, content_url, target_text, phonetic_script, difficulty_level) VALUES
(1, 1, 'स्वर एवं व्यंजन उच्चारण', 'Voice Practice', '/audio/hi/phonetics.mp3', 'भाषा विचारों को अभिव्यक्त करने का अमूल्य माध्यम है', '["भा-षा", "वि-चा-रों"]', 'FOUNDATIONAL'),
(2, 5, 'Vowel Sounds & Phoneme Synthesis', 'Voice Practice', '/audio/en/phonetics.mp3', 'Language unlocks knowledge, wisdom, and human expression', '["Lan-guage", "un-locks"]', 'FOUNDATIONAL'),
(3, 9, 'అచ్చులు మరియు హల్లుల ఉచ్చారణ', 'Voice Practice', '/audio/te/phonetics.mp3', 'భాష అనేది ఆలోచనలకు రూపాన్ని ఇచ్చే అమూల్యమైన సాధనం', '["భా-ష", "ఆ-లో-చ-న-లు"]', 'FOUNDATIONAL')
ON CONFLICT (lesson_id) DO NOTHING;
