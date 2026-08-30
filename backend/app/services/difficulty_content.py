# -*- coding: utf-8 -*-
"""
Aggregates all language content files into a single DIFFICULTY_CONTENT dict.
"""

from app.services.content.en_content import EN_CONTENT
from app.services.content.hi_content import HI_CONTENT
from app.services.content.te_content import TE_CONTENT
from app.services.content.ta_content import TA_CONTENT
from app.services.content.mr_content import MR_CONTENT
from app.services.content.bn_content import BN_CONTENT
from app.services.content.kn_content import KN_CONTENT
from app.services.content.es_content import ES_CONTENT

# Master content dictionary: lang_code -> difficulty_level -> skill_type -> [lessons]
DIFFICULTY_CONTENT = {
    "en": EN_CONTENT,
    "hi": HI_CONTENT,
    "te": TE_CONTENT,
    "ta": TA_CONTENT,
    "mr": MR_CONTENT,
    "bn": BN_CONTENT,
    "kn": KN_CONTENT,
    "es": ES_CONTENT,
}

# The 8 difficulty levels in order (Zero is already seeded)
DIFFICULTY_LEVELS = [
    "Zero",
    "Absolute Beginner",
    "Beginner",
    "Elementary",
    "Intermediate",
    "Upper Intermediate",
    "Advanced",
    "Mastery"
]

# Skill type to content_type mapping
SKILL_CONTENT_TYPE = {
    "SPOKEN": "Voice Practice",
    "WRITTEN": "Written Practice",
    "READING": "Functional Reading"
}
