-- ============================================================================
-- AksharAI Database Schema (PostgreSQL DDL) - 21 Relational Tables
-- ============================================================================

-- 1. LANGUAGE
CREATE TABLE IF NOT EXISTS language (
    lang_id SERIAL PRIMARY KEY,
    lang_name VARCHAR(50) NOT NULL,
    iso_code VARCHAR(10) NOT NULL UNIQUE
);

-- 2. CURRICULUM
CREATE TABLE IF NOT EXISTS curriculum (
    curriculum_id SERIAL PRIMARY KEY,
    lang_id INT NOT NULL REFERENCES language(lang_id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    level VARCHAR(30) NOT NULL,
    description TEXT
);

-- 3. MODULE
CREATE TABLE IF NOT EXISTS module (
    module_id SERIAL PRIMARY KEY,
    curriculum_id INT NOT NULL REFERENCES curriculum(curriculum_id) ON DELETE CASCADE,
    module_name VARCHAR(150) NOT NULL,
    sequence_no INT NOT NULL,
    skill_type VARCHAR(50) NOT NULL
);

-- 4. LESSON
CREATE TABLE IF NOT EXISTS lesson (
    lesson_id SERIAL PRIMARY KEY,
    module_id INT NOT NULL REFERENCES module(module_id) ON DELETE CASCADE,
    title VARCHAR(150) NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    content_url VARCHAR(255),
    target_text TEXT,
    phonetic_script TEXT,
    difficulty_level VARCHAR(30) NOT NULL
);

-- 5. ASSESSMENT
CREATE TABLE IF NOT EXISTS assessment (
    assessment_id SERIAL PRIMARY KEY,
    module_id INT REFERENCES module(module_id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) NOT NULL,
    title VARCHAR(150) NOT NULL,
    total_marks INT NOT NULL DEFAULT 100
);

-- 6. ASSESSMENT_QUESTION
CREATE TABLE IF NOT EXISTS assessment_question (
    question_id SERIAL PRIMARY KEY,
    assessment_id INT NOT NULL REFERENCES assessment(assessment_id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL,
    options_json TEXT,
    correct_answer TEXT NOT NULL
);

-- 7. PROFICIENCY_BENCHMARK
CREATE TABLE IF NOT EXISTS proficiency_benchmark (
    benchmark_id SERIAL PRIMARY KEY,
    skill_type VARCHAR(50) NOT NULL,
    level_name VARCHAR(50) NOT NULL,
    min_score INT NOT NULL,
    max_score INT NOT NULL
);

-- 8. LEARNER
CREATE TABLE IF NOT EXISTS learner (
    learner_id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    current_lang_id INT REFERENCES language(lang_id) ON DELETE SET NULL,
    is_email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    password_reset_token VARCHAR(255),
    password_reset_expires DATETIME
);

-- 9. LEARNER_PROFILE
CREATE TABLE IF NOT EXISTS learner_profile (
    profile_id SERIAL PRIMARY KEY,
    learner_id INT UNIQUE NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    age_group VARCHAR(20),
    literacy_level VARCHAR(30) DEFAULT 'FOUNDATIONAL',
    streak_count INT DEFAULT 0,
    total_points INT DEFAULT 0,
    reading_pct FLOAT DEFAULT 0.0,
    comprehension_pct FLOAT DEFAULT 0.0,
    voice_pct FLOAT DEFAULT 0.0
);

-- 10. ASSESSMENT_RESULT
CREATE TABLE IF NOT EXISTS assessment_result (
    result_id SERIAL PRIMARY KEY,
    learner_id INT NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    assessment_id INT NOT NULL REFERENCES assessment(assessment_id) ON DELETE CASCADE,
    question_id INT REFERENCES assessment_question(question_id) ON DELETE SET NULL,
    benchmark_id INT REFERENCES proficiency_benchmark(benchmark_id),
    score DECIMAL(5,2) NOT NULL,
    is_correct BOOLEAN DEFAULT FALSE,
    user_answer TEXT,
    attempt_no INT DEFAULT 1,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 11. LEARNING_PATH
CREATE TABLE IF NOT EXISTS learning_path (
    path_id SERIAL PRIMARY KEY,
    learner_id INT NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    target_proficiency VARCHAR(50) NOT NULL,
    generated_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    current_level VARCHAR(30) NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- 12. PATH_LESSON
CREATE TABLE IF NOT EXISTS path_lesson (
    path_lesson_id SERIAL PRIMARY KEY,
    path_id INT NOT NULL REFERENCES learning_path(path_id) ON DELETE CASCADE,
    lesson_id INT NOT NULL REFERENCES lesson(lesson_id) ON DELETE CASCADE,
    sequence_no INT NOT NULL,
    status VARCHAR(20) DEFAULT 'UNLOCKED'
);

-- 13. RECOMMENDATION
CREATE TABLE IF NOT EXISTS recommendation (
    recommendation_id SERIAL PRIMARY KEY,
    learner_id INT NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    lesson_id INT NOT NULL REFERENCES lesson(lesson_id) ON DELETE CASCADE,
    recommended_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(255),
    model_version VARCHAR(50) DEFAULT 'scikit-learn-v1'
);

-- 14. VOICE_SESSION
CREATE TABLE IF NOT EXISTS voice_session (
    session_id SERIAL PRIMARY KEY,
    learner_id INT NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    lesson_id INT NOT NULL REFERENCES lesson(lesson_id) ON DELETE CASCADE,
    audio_url VARCHAR(255),
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration_sec INT DEFAULT 0
);

-- 15. PRONUNCIATION_SCORE
CREATE TABLE IF NOT EXISTS pronunciation_score (
    score_id SERIAL PRIMARY KEY,
    session_id INT UNIQUE NOT NULL REFERENCES voice_session(session_id) ON DELETE CASCADE,
    recognized_text TEXT,
    phoneme_accuracy DECIMAL(5,2),
    syllable_score DECIMAL(5,2),
    word_feedback_json TEXT,
    overall_score DECIMAL(5,2) NOT NULL
);

-- 16. PROGRESS_TRACKING
CREATE TABLE IF NOT EXISTS progress_tracking (
    progress_id SERIAL PRIMARY KEY,
    learner_id INT NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    module_id INT NOT NULL REFERENCES module(module_id) ON DELETE CASCADE,
    completion_percent DECIMAL(5,2) DEFAULT 0.00,
    last_activity_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 17. LEARNING_REPORT
CREATE TABLE IF NOT EXISTS learning_report (
    report_id SERIAL PRIMARY KEY,
    learner_id INT NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    reporting_period VARCHAR(50) NOT NULL,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    overall_progress DECIMAL(5,2) DEFAULT 0.00
);

-- 18. ACHIEVEMENT
CREATE TABLE IF NOT EXISTS achievement (
    achievement_id SERIAL PRIMARY KEY,
    achievement_name VARCHAR(100) NOT NULL,
    description TEXT,
    criteria VARCHAR(255) NOT NULL
);

-- 19. LEARNER_ACHIEVEMENT
CREATE TABLE IF NOT EXISTS learner_achievement (
    learner_achievement_id SERIAL PRIMARY KEY,
    learner_id INT NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    achievement_id INT NOT NULL REFERENCES achievement(achievement_id) ON DELETE CASCADE,
    earned_on TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 20. REGISTRATION_STEP
CREATE TABLE IF NOT EXISTS registration_step (
    step_id SERIAL PRIMARY KEY,
    step_name VARCHAR(50) NOT NULL,
    sequence_no INT NOT NULL,
    description TEXT,
    is_required BOOLEAN DEFAULT TRUE
);

-- 21. LEARNER_REGISTRATION_PROGRESS
CREATE TABLE IF NOT EXISTS learner_registration_progress (
    progress_id SERIAL PRIMARY KEY,
    learner_id INT NOT NULL REFERENCES learner(learner_id) ON DELETE CASCADE,
    step_id INT NOT NULL REFERENCES registration_step(step_id) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'IN_PROGRESS',
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_learner_email ON learner(email);
CREATE INDEX IF NOT EXISTS idx_curriculum_lang ON curriculum(lang_id);
CREATE INDEX IF NOT EXISTS idx_module_curriculum ON module(curriculum_id);
CREATE INDEX IF NOT EXISTS idx_lesson_module ON lesson(module_id);
CREATE INDEX IF NOT EXISTS idx_voice_session_learner ON voice_session(learner_id);
CREATE INDEX IF NOT EXISTS idx_progress_learner ON progress_tracking(learner_id);
