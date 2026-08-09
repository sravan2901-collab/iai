from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# Auth & Registration
class LearnerRegister(BaseModel):
    email: str
    username: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    native_lang_id: Optional[int] = 1
    selected_lang: Optional[str] = "en"

class LearnerLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    literacy_level: str
    verification_token: Optional[str] = None

class VerifyEmail(BaseModel):
    token: str

class ForgotPassword(BaseModel):
    email: str

class VerifyResetOTP(BaseModel):
    email: str
    otp_code: str

class ResetPassword(BaseModel):
    email: str
    otp_code: str
    new_password: str

# Learner Profile
class LearnerProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    native_lang_id: Optional[int] = None
    preferred_learning_style: Optional[str] = None
    literacy_level: Optional[str] = None

class LearnerProfileOut(BaseModel):
    profile_id: int
    learner_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    age_group: Optional[str]
    literacy_level: str
    streak_count: int
    total_points: int

    class Config:
        from_attributes = True

# Curriculum & Lessons
class LanguageOut(BaseModel):
    lang_id: int
    lang_name: str
    iso_code: str

    class Config:
        from_attributes = True

class LessonOut(BaseModel):
    lesson_id: int
    module_id: int
    title: str
    content_type: str
    content_url: Optional[str]
    target_text: Optional[str]
    phonetic_script: Optional[str]
    difficulty_level: str

    class Config:
        from_attributes = True

class ModuleOut(BaseModel):
    module_id: int
    module_name: str
    sequence_no: int
    skill_type: str
    lessons: List[LessonOut] = []

    class Config:
        from_attributes = True

# Assessment
class AssessmentQuestionOut(BaseModel):
    question_id: int
    question_text: str
    question_type: str
    options_json: Optional[str]

    class Config:
        from_attributes = True

class AssessmentSubmit(BaseModel):
    assessment_id: int
    answers: dict  # {question_id: answer_text}

class AssessmentResultOut(BaseModel):
    result_id: int
    score: float
    benchmark_level: str
    recommended_path: str

# Voice & Pronunciation
class PronunciationEvaluationOut(BaseModel):
    session_id: int
    recognized_text: str
    phoneme_accuracy: float
    syllable_score: float
    overall_score: float
    word_feedback: dict
    remediation_tip: str
