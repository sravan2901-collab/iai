"""
Phonetic & Phonological Pronunciation Evaluation Service for AksharAI.

Implements:
1. Epitran-Style Grapheme-to-Phoneme (G2P) IPA Transducers for 8 Languages:
   (Telugu, Hindi, Tamil, Kannada, Bengali, Marathi, English, Spanish)
2. PanPhon Distinctive Articulatory Feature Vector Matrix (22 Phonological Traits)
3. Fine-Grained Articulatory Distance & Phoneme Sequence Alignment
4. Actionable Articulatory Remediation Guidance
"""

import re
import unicodedata
from typing import Dict, List, Any, Tuple, Optional

# =====================================================================
# 1. PANPHON ARTICULATORY FEATURE VECTORS (22 DISTINCTIVE FEATURES)
# =====================================================================
# Features:
# [syl, son, cons, cont, delrel, nas, lat, voi, sg, cg, ant, cor, distr, lab, hi, lo, back, round, tense, retro, dental, velar]

PANPHON_FEATURE_MAP: Dict[str, List[int]] = {
    # Vowels
    'a':  [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0],
    'aː': [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0],
    'i':  [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    'iː': [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
    'u':  [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0],
    'uː': [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0],
    'e':  [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    'eː': [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
    'o':  [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0],
    'oː': [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0],
    'ai': [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0],
    'au': [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0],
    'ɔ':  [1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0],
    'rɨ': [1, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0],

    # Velar Stops
    'k':  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    'kʰ': [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    'ɡ':  [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    'ɡʱ': [0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],
    'ŋ':  [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1],

    # Palatal Affricates
    't͡ʃ':  [0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    't͡ʃʰ': [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    'd͡ʒ':  [0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    'd͡ʒʱ': [0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    'ɲ':   [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],

    # Retroflex Stops
    'ʈ':  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    'ʈʰ': [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    'ɖ':  [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    'ɖʱ': [0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    'ɳ':  [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],

    # Dental Stops
    't̪':  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    't̪ʰ': [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    'd̪':  [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    'd̪ʱ': [0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    'n':  [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    'n̪':  [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],

    # Labial Stops
    'p':  [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    'pʰ': [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    'b':  [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    'bʱ': [0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    'm':  [0, 1, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],

    # Liquids, Fricatives & Glides
    'j': [0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    'ɾ': [0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'r': [0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'l': [0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'ɭ': [0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    'ʋ': [0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    'ʃ': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],
    'ʂ': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    's': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    'h': [0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    'f': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    'v': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
    'z': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    'θ': [0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
    'ð': [0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
}


def panphon_articulatory_distance(p1: str, p2: str) -> float:
    """
    Computes fine-grained phonological feature distance between two IPA phonemes.
    Returns a value between 0.0 (identical phonemes) and 1.0 (maximally distinct).
    """
    if p1 == p2:
        return 0.0

    v1 = PANPHON_FEATURE_MAP.get(p1)
    v2 = PANPHON_FEATURE_MAP.get(p2)

    if not v1 or not v2:
        # Fallback if unmapped IPA symbol
        return 0.5

    diff_sum = sum(abs(a - b) for a, b in zip(v1, v2))
    return diff_sum / len(v1)


# =====================================================================
# 2. EPITRAN-STYLE G2P (GRAPHEME-TO-PHONEME) IPA TRANSDUCERS
# =====================================================================

TELUGU_G2P = {
    'అ': 'a', 'ఆ': 'aː', 'ఇ': 'i', 'ఈ': 'iː', 'ఉ': 'u', 'ఊ': 'uː', 'ఋ': 'rɨ',
    'ఎ': 'e', 'ఏ': 'eː', 'ఐ': 'ai', 'ఒ': 'o', 'ఓ': 'oː', 'ఔ': 'au',
    'క': 'k', 'ఖ': 'kʰ', 'గ': 'ɡ', 'ఘ': 'ɡʱ', 'ఙ': 'ŋ',
    'చ': 't͡ʃ', 'ఛ': 't͡ʃʰ', 'జ': 'd͡ʒ', 'ఝ': 'd͡ʒʱ', 'ఞ': 'ɲ',
    'ట': 'ʈ', 'ఠ': 'ʈʰ', 'డ': 'ɖ', 'ఢ': 'ɖʱ', 'ణ': 'ɳ',
    'త': 't̪', 'థ': 't̪ʰ', 'ద': 'd̪', 'ధ': 'd̪ʱ', 'న': 'n',
    'ప': 'p', 'ఫ': 'pʰ', 'బ': 'b', 'భ': 'bʱ', 'మ': 'm',
    'య': 'j', 'ర': 'ɾ', 'ల': 'l', 'వ': 'ʋ', 'శ': 'ʃ', 'ష': 'ʂ', 'స': 's', 'హ': 'h', 'ళ': 'ɭ'
}
TELUGU_MATRA = {
    'ా': 'aː', 'ి': 'i', 'ీ': 'iː', 'ు': 'u', 'ూ': 'uː', 'ృ': 'rɨ',
    'ె': 'e', 'ే': 'eː', 'ై': 'ai', 'ొ': 'o', 'ో': 'oː', 'ౌ': 'au'
}

DEVANAGARI_G2P = {
    'अ': 'a', 'आ': 'aː', 'इ': 'i', 'ई': 'iː', 'उ': 'u', 'ऊ': 'uː', 'ऋ': 'rɨ',
    'ए': 'eː', 'ऐ': 'ai', 'ओ': 'oː', 'औ': 'au',
    'क': 'k', 'ख': 'kʰ', 'ग': 'ɡ', 'घ': 'ɡʱ', 'ङ': 'ŋ',
    'च': 't͡ʃ', 'छ': 't͡ʃʰ', 'ज': 'd͡ʒ', 'झ': 'd͡ʒʱ', 'ञ': 'ɲ',
    'ट': 'ʈ', 'ठ': 'ʈʰ', 'ड': 'ɖ', 'ढ': 'ɖʱ', 'ण': 'ɳ',
    'त': 't̪', 'थ': 't̪ʰ', 'द': 'd̪', 'ध': 'd̪ʱ', 'न': 'n',
    'प': 'p', 'फ': 'pʰ', 'ब': 'b', 'भ': 'bʱ', 'म': 'm',
    'य': 'j', 'र': 'ɾ', 'ल': 'l', 'व': 'ʋ', 'श': 'ʃ', 'ष': 'ʂ', 'स': 's', 'ह': 'h',
    'ड़': 'ɖ', 'ढ़': 'ɖʱ', 'ज़': 'z', 'फ़': 'f'
}
DEVANAGARI_MATRA = {
    'ा': 'aː', 'ि': 'i', 'ी': 'iː', 'ु': 'u', 'ू': 'uː', 'ृ': 'rɨ',
    'े': 'eː', 'ै': 'ai', 'ो': 'oː', 'ौ': 'au'
}

TAMIL_G2P = {
    'அ': 'a', 'ஆ': 'aː', 'இ': 'i', 'ஈ': 'iː', 'உ': 'u', 'ஊ': 'uː',
    'எ': 'e', 'ஏ': 'eː', 'ஐ': 'ai', 'ஒ': 'o', 'ஓ': 'oː', 'ஔ': 'au',
    'க': 'k', 'ங': 'ŋ', 'ச': 't͡ʃ', 'ஞ': 'ɲ', 'ட': 'ʈ', 'ண': 'ɳ',
    'த': 't̪', 'ந': 'n̪', 'ப': 'p', 'ம': 'm', 'ய': 'j', 'ர': 'ɾ',
    'ல': 'l', 'வ': 'ʋ', 'ழ': 'ɻ', 'ள': 'ɭ', 'ற': 'r', 'ன': 'n'
}
TAMIL_MATRA = {
    'ா': 'aː', 'ி': 'i', 'ீ': 'iː', 'ு': 'u', 'ூ': 'uː',
    'ெ': 'e', 'ே': 'eː', 'ை': 'ai', 'ொ': 'o', 'ோ': 'oː', 'ௌ': 'au'
}

KANNADA_G2P = {
    'ಅ': 'a', 'ಆ': 'aː', 'ಇ': 'i', 'ಈ': 'iː', 'ಉ': 'u', 'ಊ': 'uː', 'ಋ': 'rɨ',
    'ಎ': 'e', 'ಏ': 'eː', 'ಐ': 'ai', 'ಒ': 'o', 'ಓ': 'oː', 'ಔ': 'au',
    'ಕ': 'k', 'ಖ': 'kʰ', 'ಗ': 'ɡ', 'ಘ': 'ɡʱ', 'ಙ': 'ŋ',
    'ಚ': 't͡ʃ', 'ಛ': 't͡ʃʰ', 'ಜ': 'd͡ʒ', 'ಝ': 'd͡ʒʱ', 'ಞ': 'ɲ',
    'ಟ': 'ʈ', 'ಠ': 'ʈʰ', 'ಡ': 'ɖ', 'ಢ': 'ɖʱ', 'ಣ': 'ɳ',
    'ತ': 't̪', 'ಥ': 't̪ʰ', 'ದ': 'd̪', 'ಧ': 'd̪ʱ', 'ನ': 'n',
    'ಪ': 'p', 'ಫ': 'pʰ', 'ಬ': 'b', 'ಭ': 'bʱ', 'ಮ': 'm',
    'ಯ': 'j', 'ರ': 'ɾ', 'ಲ': 'l', 'ವ': 'ʋ', 'ಶ': 'ʃ', 'ಷ': 'ʂ', 'ಸ': 's', 'ಹ': 'h', 'ಳ': 'ɭ'
}
KANNADA_MATRA = {
    'ಾ': 'aː', 'ಿ': 'i', 'ೀ': 'iː', 'ು': 'u', 'ೂ': 'uː', 'ೃ': 'rɨ',
    'ೆ': 'e', 'ೇ': 'eː', 'ೈ': 'ai', 'ೊ': 'o', 'ೋ': 'oː', 'ೌ': 'au'
}

BENGALI_G2P = {
    'অ': 'ɔ', 'আ': 'a', 'ই': 'i', 'ঈ': 'i', 'উ': 'u', 'ঊ': 'u', 'ঋ': 'rɨ',
    'এ': 'e', 'ঐ': 'oi', 'ও': 'o', 'ঔ': 'ou',
    'ক': 'k', 'খ': 'kʰ', 'গ': 'ɡ', 'ঘ': 'ɡʱ', 'ঙ': 'ŋ',
    'চ': 't͡ʃ', 'ছ': 't͡ʃʰ', 'জ': 'd͡ʒ', 'ঝ': 'd͡ʒʱ', 'ঞ': 'ɲ',
    'ট': 'ʈ', 'ঠ': 'ʈʰ', 'ড': 'ɖ', 'ঢ': 'ɖʱ', 'ণ': 'n',
    'ত': 't̪', 'থ': 't̪ʰ', 'দ': 'd̪', 'ধ': 'd̪ʱ', 'ন': 'n',
    'প': 'p', 'ফ': 'pʰ', 'ব': 'b', 'ভ': 'bʱ', 'ম': 'm',
    'য': 'd͡ʒ', 'র': 'r', 'ল': 'l', 'শ': 'ʃ', 'ষ': 'ʃ', 'স': 's', 'হ': 'h', 'ড়': 'r'
}
BENGALI_MATRA = {
    'া': 'a', 'ি': 'i', 'ী': 'i', 'ু': 'u', 'ূ': 'u', 'ৃ': 'rɨ',
    'ে': 'e', 'ৈ': 'oi', 'ো': 'o', 'ৌ': 'ou'
}


def normalize_text_for_eval(text: str) -> str:
    """Normalizes Unicode characters, removes punctuation, and trims excess whitespace."""
    if not text:
        return ""
    normalized = unicodedata.normalize("NFC", text.strip().lower())
    clean = re.sub(r'[\.,!?;:\'\"\\\/\-_—।॥\(\)\[\]\{\}]', ' ', normalized)
    return ' '.join(clean.split())


def indic_to_ipa(text: str, g2p_map: dict, matra_map: dict, virama_char: str, nasal_char: str = None) -> List[str]:
    """Transduces Brahmic / Indic script word into standard IPA phonemes."""
    ipa_list: List[str] = []
    i = 0
    clean = unicodedata.normalize("NFC", text)

    while i < len(clean):
        c = clean[i]
        if c in g2p_map:
            # Check next char for virama (vowel suppression)
            if i + 1 < len(clean) and clean[i+1] == virama_char:
                ipa_list.append(g2p_map[c])
                i += 2
                continue
            # Check next char for matra (dependent vowel)
            elif i + 1 < len(clean) and clean[i+1] in matra_map:
                ipa_list.append(g2p_map[c])
                ipa_list.append(matra_map[clean[i+1]])
                i += 2
                continue
            else:
                ipa_list.append(g2p_map[c])
                # Append inherent vowel if consonant
                if c not in ['అ', 'ఆ', 'ఇ', 'ఈ', 'ఉ', 'ఊ', 'ఋ', 'ఎ', 'ఏ', 'ఐ', 'ఒ', 'ఓ', 'ఔ',
                             'अ', 'आ', 'इ', 'ई', 'उ', 'ऊ', 'ऋ', 'ए', 'ऐ', 'ओ', 'औ',
                             'அ', 'ஆ', 'இ', 'ஈ', 'உ', 'ஊ', 'எ', 'ஏ', 'ஐ', 'ஒ', 'ஓ', 'ஔ',
                             'ಅ', 'ಆ', 'ಇ', 'ಈ', 'ಉ', 'ಊ', 'ಋ', 'ಎ', 'ಏ', 'ಐ', 'ಒ', 'ಓ', 'ಔ',
                             'অ', 'আ', 'ই', 'ঈ', 'উ', 'ঊ', 'ঋ', 'এ', 'ঐ', 'ও', 'ঔ']:
                    ipa_list.append('a')
        elif nasal_char and c == nasal_char:
            ipa_list.append('m')
        elif c in ['ం', 'ं', 'ং', 'ಂ']:
            ipa_list.append('m')
        elif c in ['ః', 'ः', 'ঃ', 'ಃ']:
            ipa_list.append('h')
        i += 1

    return ipa_list


def latin_to_ipa(text: str, lang: str = "en") -> List[str]:
    """Transduces English / Spanish words to broad IPA phoneme sequences."""
    ipa_list: List[str] = []
    clean = text.lower().strip()
    
    # English G2P rules
    rules = [
        (r'th', 't̪'),
        (r'sh', 'ʃ'),
        (r'ch', 't͡ʃ'),
        (r'ph', 'f'),
        (r'wh', 'w'),
        (r'ee|ea', 'iː'),
        (r'oo', 'uː'),
        (r'ai|ay', 'ai'),
        (r'ou|ow', 'au'),
        (r'a', 'a'),
        (r'e', 'e'),
        (r'i', 'i'),
        (r'o', 'o'),
        (r'u', 'u'),
        (r'b', 'b'),
        (r'c', 'k'),
        (r'd', 'd̪'),
        (r'f', 'f'),
        (r'g', 'ɡ'),
        (r'h', 'h'),
        (r'j', 'd͡ʒ'),
        (r'k', 'k'),
        (r'l', 'l'),
        (r'm', 'm'),
        (r'n', 'n'),
        (r'p', 'p'),
        (r'r', 'ɾ'),
        (r's', 's'),
        (r't', 't̪'),
        (r'v', 'v'),
        (r'w', 'ʋ'),
        (r'y', 'j'),
        (r'z', 'z'),
    ]

    rem = clean
    while rem:
        matched = False
        for pat, ipa_sym in rules:
            m = re.match(pat, rem)
            if m:
                ipa_list.append(ipa_sym)
                rem = rem[m.end():]
                matched = True
                break
        if not matched:
            rem = rem[1:]

    return ipa_list


def word_to_ipa(word: str, lang_code: str = "en") -> List[str]:
    """Converts a word to a list of IPA phoneme strings using the appropriate G2P transducer."""
    clean = unicodedata.normalize("NFC", word).strip()
    if not clean:
        return []

    # Detect by script or explicit language code
    if re.search(r'[\u0C00-\u0C7F]', clean) or lang_code in ("te", "te-in"):
        return indic_to_ipa(clean, TELUGU_G2P, TELUGU_MATRA, virama_char='్')
    elif re.search(r'[\u0900-\u097F]', clean) or lang_code in ("hi", "hi-in", "mr", "mr-in"):
        return indic_to_ipa(clean, DEVANAGARI_G2P, DEVANAGARI_MATRA, virama_char='्')
    elif re.search(r'[\u0B80-\u0BFF]', clean) or lang_code in ("ta", "ta-in"):
        return indic_to_ipa(clean, TAMIL_G2P, TAMIL_MATRA, virama_char='்')
    elif re.search(r'[\u0C80-\u0CFF]', clean) or lang_code in ("kn", "kn-in"):
        return indic_to_ipa(clean, KANNADA_G2P, KANNADA_MATRA, virama_char='್')
    elif re.search(r'[\u0980-\u09FF]', clean) or lang_code in ("bn", "bn-in"):
        return indic_to_ipa(clean, BENGALI_G2P, BENGALI_MATRA, virama_char='্')
    else:
        return latin_to_ipa(clean, lang=lang_code)


# =====================================================================
# 3. PHONOLOGICAL NEEDLEMAN-WUNSCH ALIGNMENT & ACCURACY SCORING
# =====================================================================

def phonetic_word_similarity(target_word: str, spoken_word: str, lang_code: str = "en") -> float:
    """
    Computes the true phonological articulatory similarity between two words
    by converting to IPA and aligning feature vectors (PanPhon distance).
    """
    target_ipa = word_to_ipa(target_word, lang_code)
    spoken_ipa = word_to_ipa(spoken_word, lang_code)

    if not target_ipa and not spoken_ipa:
        return 1.0
    if not target_ipa or not spoken_ipa:
        return 0.0

    m, n = len(target_ipa), len(spoken_ipa)
    # Dynamic programming alignment matrix
    dp = [[0.0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = float(i)
    for j in range(n + 1):
        dp[0][j] = float(j)

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            p1 = target_ipa[i - 1]
            p2 = spoken_ipa[j - 1]
            cost = panphon_articulatory_distance(p1, p2)
            dp[i][j] = min(
                dp[i - 1][j] + 1.0,        # deletion
                dp[i][j - 1] + 1.0,        # insertion
                dp[i - 1][j - 1] + cost    # articulatory substitution cost
            )

    min_edit = dp[m][n]
    max_len = max(m, n)
    sim = max(0.0, 1.0 - (min_edit / max_len)) if max_len > 0 else 1.0
    return sim


def evaluate_pronunciation(target_text: str, spoken_text: str, language_code: str = "en") -> Dict[str, Any]:
    """
    Evaluates learner pronunciation against target lesson text using
    true IPA Phonetic G2P Transduction and PanPhon Articulatory Feature Distance.
    """
    if not target_text or not target_text.strip():
        return {
            "overall_score": 0.0,
            "phoneme_accuracy": 0.0,
            "syllable_score": 0.0,
            "word_feedback": {},
            "remediation_tip": "No target text provided for this lesson."
        }

    # Clean punctuation and split into words
    clean_target_words = [w.strip() for w in re.sub(r'[\.,!?;:\'\"\\\/\-_—।॥\(\)\[\]\{\}]', ' ', target_text).split() if w.strip()]
    clean_spoken_words = [w.strip() for w in re.sub(r'[\.,!?;:\'\"\\\/\-_—।॥\(\)\[\]\{\}]', ' ', spoken_text).split() if w.strip()]

    if not clean_spoken_words:
        word_feedback = {tw: "red" for tw in clean_target_words}
        return {
            "overall_score": 0.0,
            "phoneme_accuracy": 0.0,
            "syllable_score": 0.0,
            "word_feedback": word_feedback,
            "remediation_tip": "No speech was detected. Press the microphone and speak aloud clearly."
        }

    word_feedback = {}
    total_sim = 0.0
    used_spoken = set()

    for i, tw in enumerate(clean_target_words):
        best_sim = 0.0
        best_idx = -1

        for j, sw in enumerate(clean_spoken_words):
            if j in used_spoken:
                continue
            sim = phonetic_word_similarity(tw, sw, language_code)
            if sim > best_sim:
                best_sim = sim
                best_idx = j

        if best_idx >= 0 and best_sim > 0.35:
            used_spoken.add(best_idx)

        pct = best_sim * 100.0
        if pct >= 80.0:
            word_feedback[tw] = "green"
        elif pct >= 50.0:
            word_feedback[tw] = "yellow"
        else:
            word_feedback[tw] = "red"

        total_sim += best_sim

    num_words = len(clean_target_words)
    phoneme_acc = (total_sim / num_words) * 100.0 if num_words else 0.0
    syllables_correct = sum(1 for v in word_feedback.values() if v != "red")
    syllable_score = (syllables_correct / num_words) * 100.0 if num_words else 0.0

    # Weighted composite: 65% Phonemic articulatory accuracy + 35% Syllabic coverage
    overall = round(phoneme_acc * 0.65 + syllable_score * 0.35, 1)

    red_words = [k for k, v in word_feedback.items() if v == "red"]
    yellow_words = [k for k, v in word_feedback.items() if v == "yellow"]

    # Actionable Phonetic Guidance
    if overall >= 90.0:
        remediation_tip = "Excellent pronunciation! Your phonemes closely match the benchmark."
    elif overall >= 70.0:
        issues = ", ".join((yellow_words + red_words)[:3])
        remediation_tip = f"Good effort! Practice articulating these phonemes clearly: {issues}."
    elif overall >= 50.0:
        issues = ", ".join((red_words + yellow_words)[:3])
        remediation_tip = f"Keep practicing. Focus on pronouncing: {issues}. Listen to the reference audio first."
    else:
        remediation_tip = "Listen to the reference audio, then repeat slowly one syllable at a time."

    return {
        "overall_score": min(max(overall, 0.0), 100.0),
        "phoneme_accuracy": round(min(phoneme_acc, 100.0), 1),
        "syllable_score": round(min(syllable_score, 100.0), 1),
        "word_feedback": word_feedback,
        "remediation_tip": remediation_tip
    }
