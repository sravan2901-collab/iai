import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.ai_course_generator import ai_course_generator

async def test():
    print("Testing Distinct Exercise Generation for Beginners (FOUNDATIONAL tier)...")
    skills = ["VOICE", "COMPREHENSION", "READING"]
    
    for sk in skills:
        ex, provider = await ai_course_generator.generate_exercise(
            language="en",
            skill_type=sk,
            difficulty="FOUNDATIONAL"
        )
        print(f"\n--- SKILL: {sk} (Provider: {provider}) ---")
        print(f"Title: {ex.get('title')}")
        print(f"Target Text: '{ex.get('target_text')}'")
        print(f"Explanation: {ex.get('explanation')}")
        print(f"Phonetics: {ex.get('phonetic_script')}")

if __name__ == "__main__":
    asyncio.run(test())
