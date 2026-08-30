from sqlalchemy import Column, Integer, String, Text, Boolean, Numeric, DateTime, Date, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# 1. LANGUAGE
class Language(Base):
    __tablename__ = "language"
    
    lang_id = Column(Integer, primary_key=True, index=True)
    lang_name = Column(String(50), nullable=False)
    iso_code = Column(String(10), unique=True, nullable=False)
    
    curriculums = relationship("Curriculum", back_populates="language", cascade="all, delete-orphan")
    learners = relationship("Learner", back_populates="current_language")

# 2. CURRICULUM
class Curriculum(Base):
    __tablename__ = "curriculum"
    
    curriculum_id = Column(Integer, primary_key=True, index=True)
    lang_id = Column(Integer, ForeignKey("language.lang_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    level = Column(String(30), nullable=False)
    description = Column(Text)
    
    language = relationship("Language", back_populates="curriculums")
    modules = relationship("Module", back_populates="curriculum", cascade="all, delete-orphan")

# 3. MODULE
class Module(Base):
    __tablename__ = "module"
    
    module_id = Column(Integer, primary_key=True, index=True)
    curriculum_id = Column(Integer, ForeignKey("curriculum.curriculum_id", ondelete="CASCADE"), nullable=False)
    module_name = Column(String(150), nullable=False)
    sequence_no = Column(Integer, nullable=False)
    skill_type = Column(String(50), nullable=False)
    
    curriculum = relationship("Curriculum", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")
    assessments = relationship("Assessment", back_populates="module", cascade="all, delete-orphan")
    progress_records = relationship("ProgressTracking", back_populates="module", cascade="all, delete-orphan")

# 4. LESSON
class Lesson(Base):
    __tablename__ = "lesson"
    
    lesson_id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("module.module_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(150), nullable=False)
    content_type = Column(String(50), nullable=False)
    content_url = Column(String(255))
    target_text = Column(Text)
    phonetic_script = Column(Text)
    difficulty_level = Column(String(30), nullable=False)
    
    module = relationship("Module", back_populates="lessons")
    path_lessons = relationship("PathLesson", back_populates="lesson", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="lesson", cascade="all, delete-orphan")
    voice_sessions = relationship("VoiceSession", back_populates="lesson", cascade="all, delete-orphan")

# 5. ASSESSMENT
class Assessment(Base):
    __tablename__ = "assessment"
    
    assessment_id = Column(Integer, primary_key=True, index=True)
    module_id = Column(Integer, ForeignKey("module.module_id", ondelete="CASCADE"))
    assessment_type = Column(String(50), nullable=False)
    title = Column(String(150), nullable=False)
    total_marks = Column(Integer, default=100)
    
    module = relationship("Module", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="assessment", cascade="all, delete-orphan")
    results = relationship("AssessmentResult", back_populates="assessment", cascade="all, delete-orphan")

# 6. ASSESSMENT_QUESTION
class AssessmentQuestion(Base):
    __tablename__ = "assessment_question"
    
    question_id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessment.assessment_id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    options_json = Column(Text)
    correct_answer = Column(Text, nullable=False)
    
    assessment = relationship("Assessment", back_populates="questions")

# 7. PROFICIENCY_BENCHMARK
class ProficiencyBenchmark(Base):
    __tablename__ = "proficiency_benchmark"
    
    benchmark_id = Column(Integer, primary_key=True, index=True)
    skill_type = Column(String(50), nullable=False)
    level_name = Column(String(50), nullable=False)
    min_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    
    results = relationship("AssessmentResult", back_populates="benchmark")

# 8. LEARNER
class Learner(Base):
    __tablename__ = "learner"
    
    learner_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    registration_date = Column(DateTime(timezone=True), server_default=func.now())
    current_lang_id = Column(Integer, ForeignKey("language.lang_id", ondelete="SET NULL"))
    
    # Verification & Reset Fields
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String(255), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_expires = Column(DateTime, nullable=True)
    
    current_language = relationship("Language", back_populates="learners")
    profile = relationship("LearnerProfile", back_populates="learner", uselist=False, cascade="all, delete-orphan")
    assessment_results = relationship("AssessmentResult", back_populates="learner", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="learner", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="learner", cascade="all, delete-orphan")
    voice_sessions = relationship("VoiceSession", back_populates="learner", cascade="all, delete-orphan")
    progress_records = relationship("ProgressTracking", back_populates="learner", cascade="all, delete-orphan")
    reports = relationship("LearningReport", back_populates="learner", cascade="all, delete-orphan")
    achievements = relationship("LearnerAchievement", back_populates="learner", cascade="all, delete-orphan")
    registration_progress = relationship("LearnerRegistrationProgress", back_populates="learner", cascade="all, delete-orphan")

# 9. LEARNER_PROFILE
class LearnerProfile(Base):
    __tablename__ = "learner_profile"
    
    profile_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    age_group = Column(String(20))
    literacy_level = Column(String(30), default="FOUNDATIONAL")
    streak_count = Column(Integer, default=0)
    total_points = Column(Integer, default=0)
    
    # Granular Skill Breakdown Percentages (Step 1.2)
    reading_pct = Column(Float, default=0.0)
    comprehension_pct = Column(Float, default=0.0)
    voice_pct = Column(Float, default=0.0)
    last_activity_date = Column(Date, nullable=True)
    
    learner = relationship("Learner", back_populates="profile")

# 10. ASSESSMENT_RESULT
class AssessmentResult(Base):
    __tablename__ = "assessment_result"
    
    result_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    assessment_id = Column(Integer, ForeignKey("assessment.assessment_id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("assessment_question.question_id", ondelete="SET NULL"), nullable=True)
    benchmark_id = Column(Integer, ForeignKey("proficiency_benchmark.benchmark_id"), nullable=True)
    score = Column(Float, nullable=False)
    is_correct = Column(Boolean, nullable=True, default=False)
    user_answer = Column(Text, nullable=True)
    attempt_no = Column(Integer, default=1)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    learner = relationship("Learner", back_populates="assessment_results")
    assessment = relationship("Assessment", back_populates="results")
    benchmark = relationship("ProficiencyBenchmark", back_populates="results")
    question = relationship("AssessmentQuestion")


# 11. LEARNING_PATH
class LearningPath(Base):
    __tablename__ = "learning_path"
    
    path_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    target_proficiency = Column(String(50), nullable=False)
    generated_on = Column(DateTime(timezone=True), server_default=func.now())
    current_level = Column(String(30), nullable=False)
    completion_percentage = Column(Float, default=0.0)
    status = Column(String(20), default="ACTIVE")
    
    learner = relationship("Learner", back_populates="learning_paths")
    path_lessons = relationship("PathLesson", back_populates="path", cascade="all, delete-orphan")

# 12. PATH_LESSON
class PathLesson(Base):
    __tablename__ = "path_lesson"
    
    path_lesson_id = Column(Integer, primary_key=True, index=True)
    path_id = Column(Integer, ForeignKey("learning_path.path_id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lesson.lesson_id", ondelete="CASCADE"), nullable=False)
    sequence_no = Column(Integer, nullable=False)
    status = Column(String(20), default="UNLOCKED")
    
    path = relationship("LearningPath", back_populates="path_lessons")
    lesson = relationship("Lesson", back_populates="path_lessons")

# 13. RECOMMENDATION
class Recommendation(Base):
    __tablename__ = "recommendation"
    
    recommendation_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lesson.lesson_id", ondelete="CASCADE"), nullable=True)
    recommended_on = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String(500))
    model_version = Column(String(50), default="rule-based")
    priority = Column(String(20), default="MEDIUM")
    skill_focus = Column(String(50), default="READING")
    rec_type = Column(String(50), default="practice_weak_area")
    title = Column(String(200))
    
    learner = relationship("Learner", back_populates="recommendations")
    lesson = relationship("Lesson", back_populates="recommendations")

# 13b. AI_GENERATED_CONTENT
class AIGeneratedContent(Base):
    __tablename__ = "ai_generated_content"
    
    content_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    language_code = Column(String(10), nullable=False)
    skill_type = Column(String(50), nullable=False)
    difficulty_level = Column(String(30), nullable=False)
    title = Column(String(200), nullable=False)
    content_json = Column(Text, nullable=False)
    generated_by = Column(String(50), default="rule-based")
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    is_approved = Column(Boolean, default=True)
    
    learner = relationship("Learner")

# 14. VOICE_SESSION
class VoiceSession(Base):
    __tablename__ = "voice_session"
    
    session_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    lesson_id = Column(Integer, ForeignKey("lesson.lesson_id", ondelete="CASCADE"), nullable=False)
    audio_url = Column(String(255))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())
    duration_sec = Column(Integer, default=0)
    
    learner = relationship("Learner", back_populates="voice_sessions")
    lesson = relationship("Lesson", back_populates="voice_sessions")
    pronunciation_score = relationship("PronunciationScore", back_populates="session", uselist=False, cascade="all, delete-orphan")

# 15. PRONUNCIATION_SCORE
class PronunciationScore(Base):
    __tablename__ = "pronunciation_score"
    
    score_id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("voice_session.session_id", ondelete="CASCADE"), unique=True, nullable=False)
    recognized_text = Column(Text)
    phoneme_accuracy = Column(Float)
    syllable_score = Column(Float)
    word_feedback_json = Column(Text)
    overall_score = Column(Float, nullable=False)
    
    session = relationship("VoiceSession", back_populates="pronunciation_score")

# 16. PROGRESS_TRACKING
class ProgressTracking(Base):
    __tablename__ = "progress_tracking"
    
    progress_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("module.module_id", ondelete="CASCADE"), nullable=False)
    completion_percent = Column(Float, default=0.0)
    time_spent_min = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True), server_default=func.now())
    
    learner = relationship("Learner", back_populates="progress_records")
    module = relationship("Module", back_populates="progress_records")

# 17. LEARNING_REPORT
class LearningReport(Base):
    __tablename__ = "learning_report"
    
    report_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    reporting_period = Column(String(50), nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    overall_progress = Column(Float, default=0.0)
    summary_json = Column(Text, nullable=True)
    narrative = Column(Text, nullable=True)
    
    learner = relationship("Learner", back_populates="reports")

# 18. ACHIEVEMENT
class Achievement(Base):
    __tablename__ = "achievement"
    
    achievement_id = Column(Integer, primary_key=True, index=True)
    achievement_name = Column(String(100), nullable=False)
    description = Column(Text)
    criteria = Column(String(255), nullable=False)
    
    learner_achievements = relationship("LearnerAchievement", back_populates="achievement", cascade="all, delete-orphan")

# 19. LEARNER_ACHIEVEMENT
class LearnerAchievement(Base):
    __tablename__ = "learner_achievement"
    
    learner_achievement_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(Integer, ForeignKey("achievement.achievement_id", ondelete="CASCADE"), nullable=False)
    earned_on = Column(DateTime(timezone=True), server_default=func.now())
    
    learner = relationship("Learner", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="learner_achievements")

# 20. REGISTRATION_STEP
class RegistrationStep(Base):
    __tablename__ = "registration_step"
    
    step_id = Column(Integer, primary_key=True, index=True)
    step_name = Column(String(50), nullable=False)
    sequence_no = Column(Integer, nullable=False)
    description = Column(Text)
    is_required = Column(Boolean, default=True)
    
    progress_records = relationship("LearnerRegistrationProgress", back_populates="step", cascade="all, delete-orphan")

# 21. LEARNER_REGISTRATION_PROGRESS
class LearnerRegistrationProgress(Base):
    __tablename__ = "learner_registration_progress"
    
    progress_id = Column(Integer, primary_key=True, index=True)
    learner_id = Column(Integer, ForeignKey("learner.learner_id", ondelete="CASCADE"), nullable=False)
    step_id = Column(Integer, ForeignKey("registration_step.step_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), default="IN_PROGRESS")
    completed_at = Column(DateTime(timezone=True))
    
    learner = relationship("Learner", back_populates="registration_progress")
    step = relationship("RegistrationStep", back_populates="progress_records")
