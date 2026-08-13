"""
Re-export module for services/recommendation_engine.py
"""

from app.services.recommendation_engine import (
    generate_recommendations,
    get_recommendations,
)

__all__ = [
    "generate_recommendations",
    "get_recommendations",
]
