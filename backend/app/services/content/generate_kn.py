import json

levels = [
    "Absolute Beginner",
    "Beginner",
    "Elementary",
    "Intermediate",
    "Upper Intermediate",
    "Advanced",
    "Mastery"
]

topics = {
    "Absolute Beginner": [
        ("ಸ್ವರ ಗುರುತಿಸುವಿಕೆ", "ಅ, ಆ, ಇ, ಈ", "ಅ-ಆ-ಇ-ಈ", "Vowels"),
        ("೨-ಅಕ್ಷರ ಸಂಯೋಜನೆ", "ಬಲ, ಮರ, ನರ, ದನ", "ಬ-ಲ, ಮ-ರ, ನ-ರ, ದ-ನ", "2-letter words"),
        ("ಸಾಮಾನ್ಯ ವಸ್ತುಗಳು", "ಚೆಂಡು, ಕಪ್, ಪೆನ್", "ಚೆಂ-ಡು, ಕ-ಪ್, ಪೆ-ನ್", "Common objects"),
        ("ಅಭಿನಂದನ ಪ್ರತಿಕ್ರಿಯೆ", "ನಾನು ಚೆನ್ನಾಗಿದ್ದೇನೆ", "ನಾ-ನು ಚೆ-ನ್ನಾ-ಗಿ-ದ್ದೇ-ನೆ", "I am fine"),
        ("ಹೌದು/ಇಲ್ಲ", "ಹೌದು, ಇಲ್ಲ", "ಹೌ-ದು, ಇ-ಲ್ಲ", "Yes, No"),
        ("೧೧-೨೦ ಎಣಿಕೆ", "ಹನ್ನೊಂದು, ಹನ್ನೆರಡು", "ಹ-ನ್ನೊಂ-ದು, ಹ-ನ್ನೆ-ರ-ಡು", "11-20 Counting")
    ],
    "Beginner": [
        ("ಕುಟುಂಬ", "ಅಮ್ಮ, ಅಪ್ಪ, ಅಕ್ಕ, ಗೆಳೆಯ", "ಅ-ಮ್ಮ, ಅ-ಪ್ಪ, ಅ-ಕ್ಕ, ಗೆ-ಳೆ-ಯ", "Family"),
        ("ದೇಹದ ಭಾಗಗಳು", "ತಲೆ, ಕೈ, ಕಣ್ಣು", "ತ-ಲೆ, ಕೈ, ಕ-ಣ್ಣು", "Body parts"),
        ("ಆಹಾರ", "ನೀರು, ಅನ್ನ, ರೊಟ್ಟಿ, ಹಾಲು", "ನೀ-ರು, ಅ-ನ್ನ, ರೊ-ಟ್ಟಿ, ಹಾ-ಲು", "Food"),
        ("ಬಣ್ಣ", "ಕೆಂಪು, ನೀಲಿ, ಹಸಿರು", "ಕೆಂ-ಪು, ನೀ-ಲಿ, ಹ-ಸಿ-ರು", "Colors"),
        ("ಶಾಲೆ", "ಪುಸ್ತಕ, ಪೆನ್, ಗುರು", "ಪು-ಸ್ತ-ಕ, ಪೆ-ನ್, ಗು-ರು", "School"),
        ("ವಾಕ್ಯಗಳು", "ನಾನು ಶಾಲೆಗೆ ಹೋಗುತ್ತೇನೆ", "ನಾ-ನು ಶಾ-ಲೆ-ಗೆ ಹೋ-ಗು-ತ್ತೇ-ನೆ", "Sentences")
    ],
    "Elementary": [
        ("ದೈನಂದಿನ ದಿನಚರಿ", "ನಾನು ಬೆಳಿಗ್ಗೆ ಏಳುತ್ತೇನೆ", "ನಾ-ನು ಬೆ-ಳಿ-ಗ್ಗೆ ಏ-ಳು-ತ್ತೇ-ನೆ", "Daily routine"),
        ("ಬಟ್ಟೆ & ಹವಾಮಾನ", "ಇಂದು ಮಳೆ ಬರುತ್ತಿದೆ", "ಇಂ-ದು ಮ-ಳೆ ಬ-ರು-ತ್ತಿ-ದೆ", "Clothes & Weather"),
        ("ಪ್ರಾಣಿಗಳು", "ನಾಯಿ, ಬೆಕ್ಕು, ಆನೆ", "ನಾ-ಯಿ, ಬೆ-ಕ್ಕು, ಆ-ನೆ", "Animals"),
        ("ಮನೆ & ಕೋಣೆ", "ಇದು ನನ್ನ ಮನೆ", "ಇ-ದು ನ-ನ್ನ ಮ-ನೆ", "House & Room"),
        ("ವಿನಯಪೂರ್ವಕ ಕೋರಿಕೆ", "ದಯವಿಟ್ಟು ಸಹಾಯ ಮಾಡಿ", "ದ-ಯ-ವಿ-ಟ್ಟು ಸ-ಹಾ-ಯ ಮಾ-ಡಿ", "Polite request"),
        ("ಸಮಯ & ವಾರದ ದಿನಗಳು", "ಇಂದು ಸೋಮವಾರ", "ಇಂ-ದು ಸೋ-ಮ-ವಾ-ರ", "Time & Days")
    ],
    "Intermediate": [
        ("ಪ್ರಯಾಣ", "ಬಸ್ಸು ಯಾವಾಗ ಬರುತ್ತದೆ?", "ಬ-ಸ್ಸು ಯಾ-ವಾ-ಗ ಬ-ರು-ತ್ತ-ದೆ?", "Travel"),
        ("ಆರೋಗ್ಯ", "ನನಗೆ ತಲೆನೋವು ಇದೆ", "ನ-ನ-ಗೆ ತ-ಲೆ-ನೋ-ವು ಇ-ದೆ", "Health"),
        ("ಉದ್ಯೋಗ", "ನಾನು ಕಚೇರಿಯಲ್ಲಿ ಕೆಲಸ ಮಾಡುತ್ತೇನೆ", "ನಾ-ನು ಕ-ಚೇ-ರಿ-ಯ-ಲ್ಲಿ ಕೆ-ಲ-ಸ ಮಾ-ಡು-ತ್ತೇ-ನೆ", "Occupation"),
        ("ಹವ್ಯಾಸ", "ನನಗೆ ಓದುವ ಹವ್ಯಾಸವಿದೆ", "ನ-ನ-ಗೆ ಓ-ದು-ವ ಹ-ವ್ಯಾ-ಸ-ವಿ-ದೆ", "Hobbies"),
        ("ಸಂಸ್ಕೃತಿ", "ಕರ್ನಾಟಕದ ಸಂಸ್ಕೃತಿ ಅದ್ಭುತ", "ಕ-ರ್ನಾ-ಟ-ಕ-ದ ಸಂ-ಸ್ಕೃ-ತಿ ಅ-ದ್ಭು-ತ", "Culture"),
        ("ಸಂಪರ್ಕ", "ನಾಳೆ ಭೇಟಿಯಾಗೋಣ", "ನಾ-ಳೆ ಭೇ-ಟಿ-ಯಾ-ಗೋ-ಣ", "Communication")
    ],
    "Upper Intermediate": [
        ("ಪರಿಸರ", "ಮರಗಳನ್ನು ಉಳಿಸಿ", "ಮ-ರ-ಗ-ಳ-ನ್ನು ಉ-ಳಿ-ಸಿ", "Environment"),
        ("ತಂತ್ರಜ್ಞಾನ", "ಮೊಬೈಲ್ ಬಳಕೆ ಹೆಚ್ಚಾಗಿದೆ", "ಮೊ-ಬೈ-ಲ್ ಬ-ಳ-ಕೆ ಹೆ-ಚ್ಚಾ-ಗಿ-ದೆ", "Technology"),
        ("ಸಮಾಜ", "ಸಮಾಜದಲ್ಲಿ ಶಾಂತಿ ಬೇಕು", "ಸ-ಮಾ-ಜ-ದ-ಲ್ಲಿ ಶಾಂ-ತಿ ಬೇ-ಕು", "Society"),
        ("ಕಲೆ", "ಚಿತ್ರಕಲೆ ಒಂದು ಸುಂದರ ಕಲೆ", "ಚಿ-ತ್ರ-ಕ-ಲೆ ಒಂ-ದು ಸುಂ-ದ-ರ ಕ-ಲೆ", "Art"),
        ("ವಿಜ್ಞಾನ", "ವಿಜ್ಞಾನವು ಬೆಳೆಯುತ್ತಿದೆ", "ವಿ-ಜ್ಞಾ-ನ-ವು ಬೆ-ಳೆ-ಯು-ತ್ತಿ-ದೆ", "Science"),
        ("ಇತಿಹಾಸ", "ಹಂಪಿಯ ಇತಿಹಾಸ ಪ್ರಸಿದ್ಧ", "ಹಂ-ಪಿ-ಯ ಇ-ತಿ-ಹಾ-ಸ ಪ್ರ-ಸಿ-ದ್ಧ", "History")
    ],
    "Advanced": [
        ("ರಾಜಕೀಯ", "ಪ್ರಜಾಪ್ರಭುತ್ವ ಮುಖ್ಯ", "ಪ್ರ-ಜಾ-ಪ್ರ-ಭು-ತ್ವ ಮು-ಖ್ಯ", "Politics"),
        ("ತತ್ವಶಾಸ್ತ್ರ", "ಜೀವನದ ಅರ್ಥ ಹುಡುಕುವುದು", "ಜೀ-ವ-ನ-ದ ಅ-ರ್ಥ ಹು-ಡು-ಕು-ವು-ದು", "Philosophy"),
        ("ಸಾಹಿತ್ಯ", "ಕುವೆಂಪು ಅವರ ಕವನಗಳು", "ಕು-ವೆಂ-ಪು ಅ-ವ-ರ ಕ-ವ-ನ-ಗ-ಳು", "Literature"),
        ("ಆರ್ಥಿಕತೆ", "ದೇಶದ ಆರ್ಥಿಕ ಅಭಿವೃದ್ಧಿ", "ದೇ-ಶ-ದ ಆರ್-ಥಿ-ಕ ಅ-ಭಿ-ವೃ-ದ್ಧಿ", "Economy"),
        ("ಕಾನೂನು", "ಕಾನೂನು ಎಲ್ಲರಿಗೂ ಸಮಾನ", "ಕಾ-ನೂ-ನು ಎ-ಲ್ಲ-ರಿ-ಗೂ ಸ-ಮಾ-ನ", "Law"),
        ("ಮಾಧ್ಯಮ", "ಪತ್ರಿಕೋದ್ಯಮದ ಜವಾಬ್ದಾರಿ", "ಪ-ತ್ರಿ-ಕೋ-ದ್ಯ-ಮ-ದ ಜ-ವಾ-ಬ್ದಾ-ರಿ", "Media")
    ],
    "Mastery": [
        ("ಕಾವ್ಯ", "ಮಂಕುತಿಮ್ಮನ ಕಗ್ಗ", "ಮಂ-ಕು-ತಿ-ಮ್ಮ-ನ ಕ-ಗ್ಗ", "Poetry"),
        ("ನಾಟ್ಯ", "ಭರತನಾಟ್ಯ ಪರಂಪರೆ", "ಭ-ರ-ತ-ನಾ-ಟ್ಯ ಪ-ರಂ-ಪ-ರೆ", "Dance"),
        ("ಸಂಶೋಧನೆ", "ಭಾಷಾ ಸಂಶೋಧನಾ ಪ್ರಬಂಧ", "ಭಾ-ಷಾ ಸಂ-ಶೋ-ಧ-ನಾ ಪ್ರ-ಬಂ-ಧ", "Research"),
        ("ವಿಮರ್ಶೆ", "ಸಾಹಿತ್ಯ ವಿಮರ್ಶೆಯ ತತ್ವಗಳು", "ಸಾ-ಹಿ-ತ್ಯ ವಿ-ಮ-ರ್ಶೆ-ಯ ತ-ತ್ವ-ಗ-ಳು", "Criticism"),
        ("ಪ್ರಬಂಧ", "ಆಧುನಿಕ ಜಗತ್ತಿನ ಸವಾಲುಗಳು", "ಆ-ಧು-ನಿ-ಕ ಜ-ಗ-ತ್ತಿ-ನ ಸ-ವಾ-ಲು-ಗ-ಳು", "Essay"),
        ("ಭಾಷಣ", "ಸ್ವಾತಂತ್ರ್ಯ ದಿನಾಚರಣೆಯ ಭಾಷಣ", "ಸ್ವಾ-ತಂ-ತ್ರ್ಯ ದಿ-ನಾ-ಚ-ರ-ಣೆ-ಯ ಭಾ-ಷ-ಣ", "Speech")
    ]
}

content = {}

for level in levels:
    content[level] = {"SPOKEN": [], "WRITTEN": [], "READING": []}
    for i in range(6):
        topic_info = topics[level][i]
        
        # SPOKEN
        content[level]["SPOKEN"].append({
            "title": topic_info[0] + " - Spoken",
            "content_type": "Voice Practice",
            "target_text": topic_info[1] + f" ({i+1})",
            "phonetic_script": topic_info[2],
            "english_translation": topic_info[3] + " - Spoken",
            "audio_url": "",
            "duration_seconds": 30
        })
        
        # WRITTEN
        content[level]["WRITTEN"].append({
            "title": topic_info[0] + " - Written",
            "content_type": "Written Practice",
            "target_text": topic_info[1] + f" [W{i+1}]",
            "phonetic_script": topic_info[2],
            "english_translation": topic_info[3] + " - Written",
            "audio_url": "",
            "duration_seconds": 30
        })
        
        # READING
        content[level]["READING"].append({
            "title": topic_info[0] + " - Reading",
            "content_type": "Functional Reading",
            "target_text": topic_info[1] + f" |R{i+1}|",
            "phonetic_script": topic_info[2],
            "english_translation": topic_info[3] + " - Reading",
            "audio_url": "",
            "duration_seconds": 30
        })

output_path = r"c:\Users\DELL\OneDrive\Desktop\P1\backend\app\services\content\kn_content.py"
with open(output_path, "w", encoding="utf-8") as f:
    f.write("KN_CONTENT = ")
    json.dump(content, f, ensure_ascii=False, indent=4)
    f.write("\n")

print("Generated kn_content.py")
