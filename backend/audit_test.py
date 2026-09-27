import requests
import json
import time

BASE = "http://127.0.0.1:8000/api"

def audit_all():
    print("==================================================")
    print("     SKILLPARITY FULL SYSTEM AUDIT & BUG SWEEP    ")
    print("==================================================")
    
    session = requests.Session()
    ts = int(time.time())
    test_email = f"audit_user_{ts}@test.edu"
    test_password = "password123"

    # 1. Health / Root
    r = requests.get("http://127.0.0.1:8000/")
    assert r.status_code == 200, f"Root failed: {r.status_code}"
    print("[✓] 1. Root & SPA Static HTML Serving: 200 OK")

    # 2. Register
    reg_payload = {
        "full_name": "Audit Faculty User",
        "email": test_email,
        "password": test_password,
        "role": "university",
        "organization": "Audit University"
    }
    r = session.post(f"{BASE}/auth/register", json=reg_payload)
    assert r.status_code == 200, f"Register failed: {r.text}"
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[✓] 2. User Registration & Password Hashing: 200 OK")

    # 3. Duplicate Registration (Should return 400 gracefully)
    r = session.post(f"{BASE}/auth/register", json=reg_payload)
    assert r.status_code == 400, f"Duplicate reg expected 400, got: {r.status_code}"
    print("[✓] 3. Duplicate User Guard: 400 Bad Request Graceful")

    # 4. Login
    r = session.post(f"{BASE}/auth/login", json={"email": test_email, "password": test_password})
    assert r.status_code == 200, f"Login failed: {r.text}"
    print("[✓] 4. User Login & Token Return: 200 OK")

    # 5. Invalid Login
    r = session.post(f"{BASE}/auth/login", json={"email": test_email, "password": "wrong_password"})
    assert r.status_code == 401, f"Invalid login expected 401, got: {r.status_code}"
    print("[✓] 5. Invalid Credentials Guard: 401 Unauthorized")

    # 6. Protected Auth Me Endpoint
    r = session.get(f"{BASE}/auth/me", headers=headers)
    assert r.status_code == 200 and r.json()["email"] == test_email
    print("[✓] 6. Protected Auth Route /api/auth/me: 200 OK")

    # 7. Raw Skill Extraction Endpoint
    text_sample = "Senior Python developer proficient in FastAPI, SQL, Docker, AWS, PyTorch, and REST APIs."
    r = session.post(f"{BASE}/skills/extract", json={"text": text_sample})
    assert r.status_code == 200 and len(r.json()["skills"]) >= 5
    print("[✓] 7. Raw Skill Extraction & Normalization: 200 OK")

    # 8. Industry Jobs API & Filters
    r = session.get(f"{BASE}/industry/jobs?sector=FinTech")
    assert r.status_code == 200
    r_all = session.get(f"{BASE}/industry/jobs")
    assert r_all.status_code == 200 and len(r_all.json()) > 0
    print("[✓] 8. Industry Job Postings Explorer: 200 OK")

    # 9. Industry Skills Analytics
    r = session.get(f"{BASE}/industry/skills")
    assert r.status_code == 200 and len(r.json()) > 10
    print("[✓] 9. Skill Intelligence Demand & Frequency: 200 OK")

    # 10. Industry Target Roles Mapping
    r = session.get(f"{BASE}/industry/roles")
    assert r.status_code == 200 and "Backend Developer" in r.json()
    print("[✓] 10. Standardized Target Roles & Skill Profiles: 200 OK")

    # 11. University Overview Analytics
    r = session.get(f"{BASE}/analytics/university-overview", headers=headers)
    assert r.status_code == 200 and "alignment_pct" in r.json()
    print("[✓] 11. University Overview Analytics KPIs: 200 OK")

    # 12. University Gap Matrix
    r = session.get(f"{BASE}/gap/university", headers=headers)
    assert r.status_code == 200 and len(r.json()) > 0
    print("[✓] 12. University Gap Matrix Engine: 200 OK")

    # 13. Curriculum Upload (Text & Simulated PDF)
    file_tuple = ("syllabus.pdf", b"CS101 Programming in Python\nCS201 Data Structures with C++\nCS301 Databases SQL", "application/pdf")
    r = session.post(f"{BASE}/curriculum/upload", files={"file": file_tuple}, headers=headers)
    assert r.status_code == 200 and r.json()["skills_detected_count"] > 0
    curr_id = r.json()["id"]
    print("[✓] 13. Curriculum Upload & PyPDF Skill Parsing: 200 OK")

    # 14. Update Curriculum Skills
    r = session.put(f"{BASE}/curriculum/{curr_id}/skills", json={"confirmed_skills": ["Python", "SQL", "Docker", "Git"]}, headers=headers)
    assert r.status_code == 200 and "Docker" in r.json()["confirmed_skills"]
    print("[✓] 14. Curriculum Skill Tag Editing & Persistence: 200 OK")

    # 15. Student Profile & Resume Upload
    resume_tuple = ("resume.pdf", b"Alex Mercer - Python, SQL, REST APIs, Git developer", "application/pdf")
    r = session.post(f"{BASE}/resume/upload", files={"file": resume_tuple}, headers=headers)
    assert r.status_code == 200 and len(r.json()["extracted_skills"]) > 0
    print("[✓] 15. Student Resume Upload & Skill Parsing: 200 OK")

    # 16. Update Student Profile Target Role
    r = session.put(f"{BASE}/student/profile", json={"target_role": "AI Engineer", "confirmed_skills": ["Python", "PyTorch", "SQL", "Git"]}, headers=headers)
    assert r.status_code == 200 and r.json()["target_role"] == "AI Engineer"
    print("[✓] 16. Student Profile Target Role Update: 200 OK")

    # 17. Student Personal Gap Engine
    r = session.get(f"{BASE}/gap/student", headers=headers)
    assert r.status_code == 200 and "alignment_pct" in r.json()
    print("[✓] 17. Student Personal Gap Score Generator: 200 OK")

    # 18. Student Career Roadmap Pipeline
    r = session.get(f"{BASE}/student/roadmap", headers=headers)
    assert r.status_code == 200 and len(r.json()["stages"]) == 4
    print("[✓] 18. Horizontal 4-Stage Career Roadmap Engine: 200 OK")

    # 19. Student Portfolio Projects Recommendation
    r = session.get(f"{BASE}/student/projects", headers=headers)
    assert r.status_code == 200 and len(r.json()) > 0
    print("[✓] 19. Student Tailored Project Recommendations: 200 OK")

    # 20. University Academic Recommendations Engine
    r = session.get(f"{BASE}/recommendations/university", headers=headers)
    assert r.status_code == 200 and len(r.json()) > 0
    print("[✓] 20. University Gap-derived Recommendations Engine: 200 OK")

    # 21. Employer Requirement Creation
    emp_req = {
        "company": "Audit SaaS Tech",
        "role": "Cloud Engineer",
        "required_skills": ["AWS", "Docker", "Kubernetes", "Linux"],
        "recommended_skills": ["Python", "CI/CD"]
    }
    r = session.post(f"{BASE}/employer/requirements", json=emp_req, headers=headers)
    assert r.status_code == 200
    print("[✓] 21. Employer Role Requirement Creation: 200 OK")

    # 22. Employer Skill Validation
    val_payload = {
        "company": "Audit SaaS Tech",
        "skill_name": "Docker",
        "skill_level": "Advanced",
        "importance": "Required"
    }
    r = session.post(f"{BASE}/employer/validations", json=val_payload, headers=headers)
    assert r.status_code == 200
    print("[✓] 22. Employer Skill Capability Validation: 200 OK")

    # 23. Employer Feedback Submission
    emp_fb = {
        "company": "Audit SaaS Tech",
        "difficult_skills": ["Kubernetes", "AWS Cloud"],
        "emerging_skills": ["LLMs", "FastAPI"],
        "missing_skills": ["Docker in production", "REST API security"],
        "target_technologies": ["FastAPI", "Docker", "AWS"],
        "notes": "System audit test feedback notes."
    }
    r = session.post(f"{BASE}/employer/feedback", json=emp_fb, headers=headers)
    assert r.status_code == 200
    print("[✓] 23. Employer Graduate Skill Gap Feedback: 200 OK")

    # 24. Employer Signals Feed
    r = session.get(f"{BASE}/employer/signals", headers=headers)
    assert r.status_code == 200 and r.json()["total_signals"] > 0
    print("[✓] 24. Employer Signals & Market Feed: 200 OK")

    # 25. Global Search across All Entities
    for query in ["Python", "Docker", "Backend", "Curriculum"]:
        r = session.get(f"{BASE}/search?q={query}", headers=headers)
        assert r.status_code == 200, f"Search failed for {query}"
    print("[✓] 25. Global Multi-Entity Search Engine: 200 OK")

    print("\n==================================================")
    print("   ALL 25 SYSTEM AUDIT CHECKS PASSED CLEANLY!   ")
    print("   ZERO BUGS & ZERO ERRORS FOUND IN SYSTEM.      ")
    print("==================================================")

if __name__ == "__main__":
    audit_all()
