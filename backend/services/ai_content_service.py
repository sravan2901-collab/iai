"""
Re-export module for services/ai_content_service.py
"""

from app.services.ai_content_service import (
    is_ai_available,
    generate_path_plan,
    generate_lesson_content,
)

__all__ = [
    "is_ai_available",
    "generate_path_plan",
    "generate_lesson_content",
]
