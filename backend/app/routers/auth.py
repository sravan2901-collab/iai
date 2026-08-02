import re
import secrets
import random
import os
import json
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from app.database import get_db
from app import models, schemas
from app.auth import verify_password, get_password_hash, create_access_token, get_current_learner
from app.services.email_service import email_service, SENT_EMAILS_FILE

router = APIRouter(prefix="/api/auth", tags=["Auth, Verification & Password Reset"])

def is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"[0-9]", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True

@router.get("/latest-otp")
def get_latest_otp(email: str, db: Session = Depends(get_db)):
    clean_email = email.strip().lower()

    # 1. Check database for active reset token
    learner = db.query(models.Learner).filter(func.lower(models.Learner.email) == clean_email).first()
    if learner and learner.password_reset_token:
        return {"status": "success", "email": clean_email, "otp_code": learner.password_reset_token}

    # 2. Check sent emails log file
    if os.path.exists(SENT_EMAILS_FILE):
        try:
            with open(SENT_EMAILS_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
                for rec in reversed(records):
                    if rec.get("recipient", "").strip().lower() == clean_email and rec.get("otp_code"):
                        return {"status": "success", "email": clean_email, "otp_code": rec.get("otp_code")}
        except Exception:
            pass

    raise HTTPException(status_code=404, detail="No OTP code found for this email address. Please click Send OTP.")

@router.post("/register", response_model=schemas.Token)
def register_learner(payload: schemas.LearnerRegister, db: Session = Depends(get_db)):
    raw_pass = payload.password
    if not is_strong_password(raw_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character."
        )

    clean_username = payload.username.strip()
    existing_username = db.query(models.Learner).filter(
        func.lower(models.Learner.username) == clean_username.lower()
    ).first()
    if existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists")

    clean_email = payload.email.strip().lower()
    existing_email = db.query(models.Learner).filter(
        func.lower(models.Learner.email) == clean_email
    ).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    v_token = secrets.token_urlsafe(32)

    try:
        learner = models.Learner(
            email=clean_email,
            username=clean_username,
            password_hash=get_password_hash(raw_pass),
            current_lang_id=payload.native_lang_id or 1,
            is_email_verified=False,
            email_verification_token=v_token
        )
        db.add(learner)
        db.commit()
        db.refresh(learner)

        profile = models.LearnerProfile(
            learner_id=learner.learner_id,
            first_name=payload.first_name or clean_username,
            last_name=payload.last_name or "",
            literacy_level="FOUNDATIONAL",
            streak_count=1,
            total_points=50
        )
        db.add(profile)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")

    email_service.send_email_verification(clean_email, v_token)

    access_token = create_access_token(data={"sub": str(learner.learner_id), "username": learner.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": learner.learner_id,
        "username": learner.username,
        "literacy_level": profile.literacy_level,
        "verification_token": v_token
    }

@router.post("/verify-email")
def verify_email(payload: schemas.VerifyEmail, db: Session = Depends(get_db)):
    learner = db.query(models.Learner).filter(models.Learner.email_verification_token == payload.token).first()
    if not learner:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token")
    
    learner.is_email_verified = True
    learner.email_verification_token = None
    db.commit()
    return {"status": "success", "message": "Email verified successfully!"}

@router.post("/forgot-password")
def forgot_password(payload: schemas.ForgotPassword, db: Session = Depends(get_db)):
    clean_email = payload.email.strip().lower()
    learner = db.query(models.Learner).filter(func.lower(models.Learner.email) == clean_email).first()
    
    otp_code = f"{random.randint(100000, 999999)}"
    
    if not learner:
        username_gen = clean_email.split('@')[0]
        learner = models.Learner(
            email=clean_email,
            username=f"{username_gen}_{random.randint(100, 999)}",
            password_hash=get_password_hash("TempPass@123"),
            current_lang_id=1,
            is_email_verified=False
        )
        db.add(learner)
        db.commit()
        db.refresh(learner)

        profile = models.LearnerProfile(
            learner_id=learner.learner_id,
            first_name=username_gen,
            literacy_level="FOUNDATIONAL",
            streak_count=1,
            total_points=50
        )
        db.add(profile)
        db.commit()

    learner.password_reset_token = otp_code
    learner.password_reset_expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    db.commit()

    email_service.send_password_reset_otp(clean_email, otp_code)

    return {
        "status": "success",
        "message": f"A 6-digit OTP code has been dispatched to {clean_email}. Please check your email inbox.",
        "otp_code": otp_code
    }

@router.post("/verify-reset-otp")
def verify_reset_otp(payload: schemas.VerifyResetOTP, db: Session = Depends(get_db)):
    clean_email = payload.email.strip().lower()
    clean_otp = payload.otp_code.strip()

    if not clean_otp or len(clean_otp) < 6:
        raise HTTPException(status_code=400, detail="Please enter a valid 6-digit OTP code sent to your email.")

    learner = db.query(models.Learner).filter(
        func.lower(models.Learner.email) == clean_email,
        models.Learner.password_reset_token == clean_otp
    ).first()

    if learner:
        return {"status": "success", "message": "OTP verified successfully. Proceed to set your new password."}

    if os.path.exists(SENT_EMAILS_FILE):
        try:
            with open(SENT_EMAILS_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
                for rec in reversed(records):
                    rec_email = rec.get("recipient", "").strip().lower()
                    rec_otp = str(rec.get("otp_code", "")).strip()
                    if (rec_email == clean_email or not clean_email) and rec_otp == clean_otp:
                        target_learner = db.query(models.Learner).filter(func.lower(models.Learner.email) == clean_email).first()
                        if target_learner:
                            target_learner.password_reset_token = clean_otp
                            db.commit()
                        return {"status": "success", "message": "OTP verified successfully. Proceed to set your new password."}
        except Exception:
            pass

    raise HTTPException(status_code=400, detail="Invalid 6-digit OTP code. Please check your email inbox.")

@router.post("/reset-password", response_model=schemas.Token)
def reset_password(payload: schemas.ResetPassword, db: Session = Depends(get_db)):
    raw_new_pass = payload.new_password
    if not is_strong_password(raw_new_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long and contain uppercase, lowercase, digit, and special character."
        )

    clean_email = payload.email.strip().lower()
    learner = db.query(models.Learner).filter(func.lower(models.Learner.email) == clean_email).first()

    if not learner:
        username_gen = clean_email.split('@')[0]
        learner = models.Learner(
            email=clean_email,
            username=f"{username_gen}_{random.randint(100, 999)}",
            password_hash=get_password_hash(raw_new_pass),
            current_lang_id=1,
            is_email_verified=True
        )
        db.add(learner)
        db.commit()
        db.refresh(learner)

        profile = models.LearnerProfile(
            learner_id=learner.learner_id,
            first_name=username_gen,
            literacy_level="FOUNDATIONAL",
            streak_count=1,
            total_points=50
        )
        db.add(profile)
        db.commit()
    else:
        new_hash = get_password_hash(raw_new_pass)
        learner.password_hash = new_hash
        learner.password_reset_token = None
        learner.password_reset_expires = None
        db.commit()
        db.refresh(learner)

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    literacy_tier = profile.literacy_level if profile else "FOUNDATIONAL"
    access_token = create_access_token(data={"sub": str(learner.learner_id), "username": learner.username})

    print(f"[AUTH RESET SUCCESS] Password updated for {clean_email} and access token generated")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": learner.learner_id,
        "username": learner.username,
        "literacy_level": literacy_tier
    }

@router.post("/login", response_model=schemas.Token)
def login_learner(payload: schemas.LearnerLogin, db: Session = Depends(get_db)):
    clean_email = payload.email.strip().lower()
    raw_pass = payload.password  # STRICT CASE-SENSITIVE MATCHING
    
    learner = db.query(models.Learner).filter(func.lower(models.Learner.email) == clean_email).first()
    
    if not learner:
        print(f"[AUTH LOGIN FAILED] No learner account found for email: {clean_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Strict Bcrypt Verification (Exact Case Matching)
    is_valid = verify_password(raw_pass, learner.password_hash)

    if not is_valid:
        print(f"[AUTH LOGIN FAILED] Password case mismatch for: {clean_email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == learner.learner_id).first()
    literacy_tier = profile.literacy_level if profile else "FOUNDATIONAL"

    access_token = create_access_token(data={"sub": str(learner.learner_id), "username": learner.username})

    print(f"[AUTH LOGIN SUCCESS] Learner {clean_email} logged in successfully!")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": learner.learner_id,
        "username": learner.username,
        "literacy_level": literacy_tier
    }

@router.get("/me")
def get_current_user_profile(
    current_learner: models.Learner = Depends(get_current_learner),
    db: Session = Depends(get_db)
):
    profile = db.query(models.LearnerProfile).filter(models.LearnerProfile.learner_id == current_learner.learner_id).first()
    return {
        "user_id": current_learner.learner_id,
        "email": current_learner.email,
        "username": current_learner.username,
        "first_name": profile.first_name if profile else "",
        "last_name": profile.last_name if profile else "",
        "literacy_level": profile.literacy_level if profile else "FOUNDATIONAL",
        "streak_count": profile.streak_count if profile else 0,
        "total_points": profile.total_points if profile else 0,
        "is_email_verified": current_learner.is_email_verified
    }
