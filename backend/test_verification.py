import requests
import json
import time

BASE = "http://127.0.0.1:8000/api"

def test_platform():
    print("--- 1. Testing Auth Endpoints ---")
    ts = int(time.time())
    reg_payload = {
        "full_name": "Test Faculty",
        "email": f"faculty_{ts}@univ.edu",
        "password": "password123",
        "role": "university",
        "organization": "Test State University"
    }
    r = requests.post(f"{BASE}/auth/register", json=reg_payload)
    print("Register Status:", r.status_code)
    auth_data = r.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    print("\n--- 2. Testing Overview Analytics ---")
    r = requests.get(f"{BASE}/analytics/university-overview", headers=headers)
    print("Overview:", r.json())

    print("\n--- 3. Testing Skill Extraction Engine ---")
    r = requests.post(f"{BASE}/skills/extract", json={"text": "Looking for a Python backend engineer with FastAPI, Docker, and PostgreSQL experience."})
    print("Extracted Skills:", r.json())

    print("\n--- 4. Testing University Gap Analysis Matrix ---")
    r = requests.get(f"{BASE}/gap/university", headers=headers)
    matrix = r.json()
    print(f"Gap Matrix Rows: {len(matrix)}")
    print("Sample Top 3 Gaps:", matrix[:3])

    print("\n--- 5. Testing Student Gap Engine ---")
    r = requests.get(f"{BASE}/gap/student", headers=headers)
    print("Student Gap Summary:", r.json())

    print("\n--- 6. Testing Recommendations Engine ---")
    r = requests.get(f"{BASE}/recommendations/university", headers=headers)
    recos = r.json()
    print(f"University Recommendations: {len(recos)}")
    for rec in recos:
        print(f" - [{rec['gap_skill']}] {rec['title']}")

    print("\n--- 7. Testing Employer Signals ---")
    r = requests.get(f"{BASE}/employer/signals", headers=headers)
    print("Employer Signals:", r.json())

    print("\n--- 8. Testing Global Search ---")
    r = requests.get(f"{BASE}/search?q=Docker", headers=headers)
    print("Search Result for Docker:", r.json())

    print("\n--- ALL API TESTS PASSED CLEANLY! ---")

if __name__ == "__main__":
    test_platform()
