import requests
import sys

BASE_URL = "http://127.0.0.1:8000/api/assessment/benchmarks"
LANGS = ['en', 'te', 'hi', 'ta', 'bn', 'mr', 'kn', 'es']

def verify_all_benchmarks():
    print("=" * 100)
    print("      VERIFYING LEARNER PROFICIENCY BENCHMARKS ACROSS ALL 8 LANGUAGES")
    print("=" * 100)
    
    all_ok = True
    for l in LANGS:
        res = requests.get(f"{BASE_URL}?lang={l}")
        if res.status_code != 200:
            print(f"[FAILED] [{l.upper()}] Status Code: {res.status_code}")
            all_ok = False
            continue
        
        data = res.json()
        lang_name = data.get("language_name", "")
        tiers = data.get("tiers", [])
        
        if len(tiers) == 3:
            tier_names = [t.get("tier") for t in tiers]
            print(f"  [PASSED] [{l.upper()}] Tiers Count: {len(tiers)} | Tiers: {tier_names}")
        else:
            print(f"  [FAILED] [{l.upper()}] Expected 3 tiers, got {len(tiers)}")
            all_ok = False

    print("=" * 100)
    if all_ok:
        print("      SUCCESS: PROFICIENCY BENCHMARKS ESTABLISHED FOR ALL 8 LANGUAGES (100%)")
    print("=" * 100)
    return all_ok

if __name__ == "__main__":
    ok = verify_all_benchmarks()
    if not ok:
        sys.exit(1)
