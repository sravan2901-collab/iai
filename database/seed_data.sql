-- ============================================================================
-- AksharAI Seed Data (Initial Population for Regional Languages & Curriculum)
-- ============================================================================

-- 1. Languages
INSERT INTO language (lang_id, lang_name, iso_code) VALUES
(1, 'Hindi (हिन्दी)', 'hi'),
(2, 'English', 'en'),
(3, 'Tamil (தமிழ்)', 'ta'),
(4, 'Telugu (తెలుగు)', 'te'),
(5, 'Marathi (मराठी)', 'mr'),
(6, 'Bengali (বাংলা)', 'bn'),
(7, 'Kannada (கன்னட)', 'kn'),
(8, 'Spanish (Español)', 'es')
ON CONFLICT (iso_code) DO NOTHING;

-- 2. Registration Steps
INSERT INTO registration_step (step_id, step_name, sequence_no, description, is_required) VALUES
(1, 'Select Native Language', 1, 'Choose preferred regional language for audio and UI', TRUE),
(2, 'Learner Background Survey', 2, 'Basic profile info and learning targets', TRUE),
(3, 'Diagnostic Placement Test', 3, '3-stage initial assessment to benchmark skill level', TRUE)
ON CONFLICT (step_id) DO NOTHING;

-- 3. Proficiency Benchmarks
INSERT INTO proficiency_benchmark (benchmark_id, skill_type, level_name, min_score, max_score) VALUES
(1, 'General Reading & Speech', 'FOUNDATIONAL', 0, 40),
(2, 'General Reading & Speech', 'FUNCTIONAL', 41, 75),
(3, 'General Reading & Speech', 'FLUENT', 76, 100)
ON CONFLICT (benchmark_id) DO NOTHING;

-- 4. Achievements
INSERT INTO achievement (achievement_id, achievement_name, description, criteria) VALUES
(1, 'First Words', 'Completed your first voice pronunciation lesson', 'COMPLETE_LESSON_1'),
(2, '3-Day Streak', 'Practiced continuous literacy for 3 consecutive days', 'STREAK_3_DAYS'),
(3, '7-Day Streak', 'Maintained a strong 7-day daily learning habit', 'STREAK_7_DAYS'),
(4, 'Financial Literacy Champ', 'Mastered reading ATM screens and UPI receipts', 'COMPLETE_FINANCE_MODULE'),
(5, 'Health & Safety Guardian', 'Learned to read prescription dosages and medicine labels', 'COMPLETE_HEALTH_MODULE'),
(6, 'Fluency Champion', 'Achieved over 85% accuracy in advanced reading passages', 'PRONUNCIATION_SCORE_85')
ON CONFLICT (achievement_id) DO NOTHING;

-- 5. Hindi Curriculum & Modules
INSERT INTO curriculum (curriculum_id, lang_id, title, level, description) VALUES
(1, 1, 'हिन्दी बुनियादी साक्षरता (Hindi Foundational Literacy)', 'FOUNDATIONAL', 'सीखें बुनियादी अक्षर, शब्द और दैनिक बोलचाल।')
ON CONFLICT (curriculum_id) DO NOTHING;

INSERT INTO module (module_id, curriculum_id, module_name, sequence_no, skill_type) VALUES
(1, 1, 'दैनिक जीवन के शब्द (Everyday Essentials)', 1, 'Reading & Pronunciation'),
(2, 1, 'वित्तीय एवं डिजिटल साक्षरता (Financial & Digital Literacy)', 2, 'Functional Reading'),
(3, 1, 'स्वास्थ्य एवं सुरक्षा (Healthcare & Medicine)', 3, 'Comprehension'),
(4, 1, 'कार्यस्थल संवाद (Workplace Communication)', 4, 'Fluency')
ON CONFLICT (module_id) DO NOTHING;

-- 6. Sample Lessons for Hindi Modules
INSERT INTO lesson (lesson_id, module_id, title, content_type, content_url, target_text, phonetic_script, difficulty_level) VALUES
(1, 1, 'नमस्ते और अभिवादन (Greetings & Hello)', 'Voice Practice', '/audio/hi/greetings.mp3', 'नमस्ते आप कैसे हैं', '["ना-मस्-ते", "आप", "कै-से", "हैं"]', 'FOUNDATIONAL'),
(2, 1, 'संख्याएँ 1 से 10 (Numbers 1 to 10)', 'Voice Practice', '/audio/hi/numbers.mp3', 'एक दो तीन चार पाँच छह सात आठ नौ दस', '["एक", "दो", "तीन", "चार", "पाँच"]', 'FOUNDATIONAL'),
(3, 2, 'एटीएम पिन सुरक्षा (ATM PIN Safety)', 'Functional Reading', '/audio/hi/atm_pin.mp3', 'अपना एटीएम पिन किसी को न बताएँ', '["अप-ना", "ए-टी-एम", "पिन", "गुप्-त", "र-खें"]', 'FUNCTIONAL'),
(4, 2, 'यूपीआई रसीद पढ़ना (Reading UPI Receipts)', 'Functional Reading', '/audio/hi/upi_receipt.mp3', 'भुगतान सफल रहा सौ रुपये', '["भुग्-तान", "स-फ-ल", "सौ", "रु-प-ये"]', 'FUNCTIONAL'),
(5, 3, 'दवा की खुराक (Medicine Dosage)', 'Comprehension', '/audio/hi/dosage.mp3', 'दिन में दो बार भोजन के बाद लें', '["दिन", "में", "दो", "बार", "भोज-न"]', 'FUNCTIONAL')
ON CONFLICT (lesson_id) DO NOTHING;

-- 7. Initial Assessment for Diagnostic Test
INSERT INTO assessment (assessment_id, module_id, assessment_type, title, total_marks) VALUES
(1, 1, 'DIAGNOSTIC_PLACEMENT', 'प्रारंभिक दक्षता परीक्षण (Initial Literacy Placement Test)', 100)
ON CONFLICT (assessment_id) DO NOTHING;

INSERT INTO assessment_question (question_id, assessment_id, question_text, question_type, options_json, correct_answer) VALUES
(1, 1, 'अक्षर "न" से शुरू होने वाला शब्द कौन सा है?', 'MCQ', '["नमस्ते", "कलम", "घर", "पानी"]', 'नमस्ते'),
(2, 1, 'चित्र पहचानें: एटीएम मशीन', 'MCQ', '["बैंक एटीएम", "अस्पताल", "डाकघर", "बस स्टॉप"]', 'बैंक एटीएम'),
(3, 1, 'नीचे दिए गए वाक्य को बोलकर पढ़ें: "कृपया अपना नाम लिखें"', 'VOICE_READ', '[]', 'कृपया अपना नाम लिखें')
ON CONFLICT (question_id) DO NOTHING;
