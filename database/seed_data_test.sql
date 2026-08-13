-- ============================================================================
-- AksharAI Seed Data Test — Proficiency Benchmarks, Test Learner & Assessment Data
-- ============================================================================

-- 1. Proficiency Benchmarks (4 level bands per skill_type)
INSERT INTO proficiency_benchmark (benchmark_id, skill_type, level_name, min_score, max_score) VALUES
-- Reading & Pronunciation
(1, 'Reading & Pronunciation', 'FOUNDATIONAL', 0, 40),
(2, 'Reading & Pronunciation', 'BASIC', 41, 60),
(3, 'Reading & Pronunciation', 'INTERMEDIATE', 61, 80),
(4, 'Reading & Pronunciation', 'ADVANCED', 81, 100),

-- Word Formation
(5, 'Word Formation', 'FOUNDATIONAL', 0, 40),
(6, 'Word Formation', 'BASIC', 41, 60),
(7, 'Word Formation', 'INTERMEDIATE', 61, 80),
(8, 'Word Formation', 'ADVANCED', 81, 100),

-- Grammar
(9, 'Grammar', 'FOUNDATIONAL', 0, 40),
(10, 'Grammar', 'BASIC', 41, 60),
(11, 'Grammar', 'INTERMEDIATE', 61, 80),
(12, 'Grammar', 'ADVANCED', 81, 100),

-- Literature
(13, 'Literature', 'FOUNDATIONAL', 0, 40),
(14, 'Literature', 'BASIC', 41, 60),
(15, 'Literature', 'INTERMEDIATE', 61, 80),
(16, 'Literature', 'ADVANCED', 81, 100);

-- 2. Test Learner & Learner Profile
INSERT INTO learner (learner_id, email, password_hash, username, registration_date, current_lang_id) VALUES
(100, 'test@aksharai.dev', '$2b$12$eImiTXuWVxfM37uY4JANjO5E.5W/jN6vO3nU78aJ91gYv.g5Vqg4S', 'testlearner', CURRENT_TIMESTAMP, 2);

INSERT INTO learner_profile (profile_id, learner_id, first_name, last_name, age_group, literacy_level, streak_count, total_points, reading_pct, comprehension_pct, voice_pct) VALUES
(100, 100, 'Test', 'Learner', 'Adult (18-35)', 'FUNCTIONAL', 5, 120, 88.0, 55.0, 72.0);

-- 3. Assessments for English Modules (Modules 5, 6, 7, 8)
INSERT INTO assessment (assessment_id, module_id, assessment_type, title, total_marks) VALUES
(101, 5, 'QUIZ', 'Phonemes & Reading Pronunciation Quiz', 100),
(102, 6, 'QUIZ', 'Vocabulary & Word Formation Quiz', 100),
(103, 7, 'QUIZ', 'Sentence Grammar & Syntax Quiz', 100),
(104, 8, 'QUIZ', 'Advanced Literary Fluency Quiz', 100);

-- 4. Assessment Questions (2-3 questions per assessment)
INSERT INTO assessment_question (question_id, assessment_id, question_text, question_type, options_json, correct_answer) VALUES
-- Assessment 101 (Module 5 - Reading & Pronunciation)
(1001, 101, 'Which word contains the long vowel sound /eɪ/ as in Grace?', 'READ', '["Grace", "Track", "Bell", "Rock"]', 'Grace'),
(1002, 101, 'Press microphone and speak aloud: Graceful articulation requires patience and practice', 'SPEAK', NULL, 'Graceful articulation requires patience and practice'),

-- Assessment 102 (Module 6 - Word Formation)
(1003, 102, 'Type the correctly spelled word for a place where books are kept:', 'WRITE', NULL, 'library'),
(1004, 102, 'Select the exact synonym for PERSISTENT:', 'READ', '["Persevering", "Temporary", "Hesitant"]', 'Persevering'),

-- Assessment 103 (Module 7 - Grammar)
(1005, 103, 'Type the past perfect form of the verb write:', 'WRITE', NULL, 'had written'),
(1006, 103, 'Identify the correct subject-verb agreement sentence:', 'READ', '["She writes an essay", "She write an essay"]', 'She writes an essay'),

-- Assessment 104 (Module 8 - Literature)
(1007, 104, 'What is the primary tone of the passage on evening silence?', 'READ', '["Tranquil and Reflective", "Chaotic and Noisy"]', 'Tranquil and Reflective'),
(1008, 104, 'Speak aloud: Mastery over language transforms thought into eloquent communication', 'SPEAK', NULL, 'Mastery over language transforms thought into eloquent communication');

-- 5. Assessment Results for Test Learner (Varied Scores)
INSERT INTO assessment_result (result_id, learner_id, assessment_id, benchmark_id, score, attempt_no, submitted_at) VALUES
-- Reading & Pronunciation (Assessment 101): High Score = 88.0 -> ADVANCED
(1001, 100, 101, 4, 88.0, 1, CURRENT_TIMESTAMP),

-- Word Formation (Assessment 102): Medium-High Score = 72.0 -> INTERMEDIATE
(1002, 100, 102, 7, 72.0, 1, CURRENT_TIMESTAMP),

-- Grammar (Assessment 103): Medium-Low Score = 55.0 -> BASIC
(1003, 100, 103, 10, 55.0, 1, CURRENT_TIMESTAMP),

-- Literature (Assessment 104): Low Score = 35.0 -> FOUNDATIONAL
(1004, 100, 104, 13, 35.0, 1, CURRENT_TIMESTAMP);
