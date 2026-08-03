/**
 * Client-Side Multilingual Content Repository Service for AksharAI.
 * Manages pure language literacy categories, phonetics, grammar, and literature across languages.
 */

export const MULTILINGUAL_REPOSITORY = {
  en: {
    lang_name: "English",
    categories: [
      { id: 1, title: "Phonemes & Alphabet Fundamentals", description: "Vowel sounds, consonant blends, and syllable stress", lessonsCount: 4 },
      { id: 2, title: "Vocabulary & Word Formation", description: "Prefixes, suffixes, root words, synonyms, and antonyms", lessonsCount: 4 },
      { id: 3, title: "Sentence Grammar & Syntax", description: "Noun-verb agreement, tenses, and complex sentence structures", lessonsCount: 3 },
      { id: 4, title: "Advanced Literary Fluency & Expression", description: "Passage reading comprehension and articulate speech", lessonsCount: 3 }
    ]
  },
  hi: {
    lang_name: "हिन्दी (Hindi)",
    categories: [
      { id: 1, title: "वर्णमाला, स्वर एवं मात्रा ज्ञान", description: "स्वर, व्यंजन, मात्राएँ एवं वर्ण संयोजन अभ्यास", lessonsCount: 4 },
      { id: 2, title: "शब्दावली एवं शब्द निर्माण", description: "पर्यायवाची, विलोम शब्द एवं शब्द संरचना", lessonsCount: 4 },
      { id: 3, title: "संधि, समास एवं वाक्य व्याकरण", description: "संधि नियम, समास एवं शुद्ध वाक्य रचना", lessonsCount: 3 },
      { id: 4, title: "उच्च साहित्यिक वाचन एवं अभिव्यक्ति", description: "साहित्यिक गद्यांश वाचन और धाराप्रवाह अभिव्यक्ति", lessonsCount: 3 }
    ]
  },
  te: {
    lang_name: "తెలుగు (Telugu)",
    categories: [
      { id: 1, title: "అక్షరాలు, వర్ణమాల మరియు గుణింతాలు", description: "అచ్చులు, హల్లులు, గుణింతాల గుర్తులు మరియు ఒత్తులు", lessonsCount: 4 },
      { id: 2, title: "పదజాలం, పర్యాయపదాలు మరియు అర్థాలు", description: "పర్యాయపదాలు, నానార్థాలు మరియు పద ఉత్పత్తి", lessonsCount: 4 },
      { id: 3, title: "సంధులు, సమాసాలు మరియు వ్యాకరణం", description: "తెలుగు సంధులు, సమాసాలు మరియు వాక్య నిర్మాణం", lessonsCount: 3 },
      { id: 4, title: "సాహిత్య గద్య పఠనం మరియు భావ వ్యక్తీకరణ", description: "సాహిత్య గద్య పఠనం మరియు అనర్గళ భాషా ప్రసంగం", lessonsCount: 3 }
    ]
  }
};

export function getCategoriesByLanguage(langCode = 'en') {
  return MULTILINGUAL_REPOSITORY[langCode]?.categories || MULTILINGUAL_REPOSITORY['en'].categories;
}
