import os
import sqlite3

def delete_all_accounts():
    print("Deleting all registered accounts and learner profile data...")
    
    # 1. Clear SQLite local DB if present
    db_paths = [
        r"c:\Users\DELL\OneDrive\Desktop\P1\backend\aksharai.db",
        r"c:\Users\DELL\OneDrive\Desktop\P1\backend\app.db",
        r"c:\Users\DELL\OneDrive\Desktop\P1\aksharai.db"
    ]

    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Delete from learner and dependent tables
                tables = [
                    "learner_profile",
                    "learner_registration_progress",
                    "assessment_result",
                    "path_lesson",
                    "learning_path",
                    "recommendation",
                    "pronunciation_score",
                    "voice_session",
                    "progress_tracking",
                    "learning_report",
                    "learner_achievement",
                    "learner"
                ]
                
                for table in tables:
                    try:
                        cursor.execute(f"DELETE FROM {table};")
                    except Exception as te:
                        pass
                
                conn.commit()
                conn.close()
                print(f"Successfully deleted all account records from {db_path}")
            except Exception as e:
                print(f"Error clearing {db_path}: {e}")

if __name__ == "__main__":
    delete_all_accounts()
