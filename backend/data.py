"""
In-memory demo data store.

This is intentionally the same dataset that used to be hardcoded in
script.js, just moved server-side. Swap this module out for real
database queries / ML pipeline output when you move past the demo.
"""

INDUSTRY_SKILLS = [
    {"skill": "Python", "industry": 91, "curriculum": 88, "icon": "🐍"},
    {"skill": "SQL", "industry": 83, "curriculum": 82, "icon": "🗄"},
    {"skill": "Cloud Computing", "industry": 72, "curriculum": 24, "icon": "☁"},
    {"skill": "Machine Learning", "industry": 72, "curriculum": 48, "icon": "🧠"},
    {"skill": "Docker", "industry": 61, "curriculum": 18, "icon": "📦"},
    {"skill": "AWS", "industry": 54, "curriculum": 12, "icon": "🖥"},
    {"skill": "REST APIs", "industry": 58, "curriculum": 51, "icon": "🔗"},
    {"skill": "Data Engineering", "industry": 49, "curriculum": 21, "icon": "🗃"},
    {"skill": "Cybersecurity", "industry": 45, "curriculum": 27, "icon": "🛡"},
]

KPIS = [
    {"label": "Industry Skills Analyzed", "value": "4,850", "delta": "+6.2%", "up": True, "icon": "📈", "note": "vs last semester", "good": False},
    {"label": "Curriculum Skills", "value": "327", "delta": "+1.4%", "up": True, "icon": "📘", "note": "vs last semester", "good": False},
    {"label": "Critical Gaps", "value": "18", "delta": "-12%", "up": False, "icon": "⚠", "note": "from last semester", "good": True},
    {"label": "Curriculum Alignment", "value": "72%", "delta": "+3 pts", "up": True, "icon": "✔", "note": "vs last semester", "good": False},
    {"label": "Emerging Skills", "value": "34", "delta": "+9", "up": True, "icon": "💡", "note": "newly tracked", "good": False},
]

CRITICAL_GAPS = [
    {"skill": "AWS / Cloud Computing", "industry": 54, "curriculum": 12, "gapScore": 0.82, "icon": "☁",
     "recommendation": "Introduce foundational cloud computing concepts and AWS laboratory exposure."},
    {"skill": "Docker & Containerization", "industry": 61, "curriculum": 18, "gapScore": 0.71, "icon": "📦",
     "recommendation": "Add a containerization module with hands-on Docker and image-build labs."},
    {"skill": "Data Engineering", "industry": 49, "curriculum": 21, "gapScore": 0.57, "icon": "🗃",
     "recommendation": "Introduce pipeline design and ETL fundamentals within the DBMS elective track."},
    {"skill": "Cybersecurity Fundamentals", "industry": 45, "curriculum": 27, "gapScore": 0.40, "icon": "🛡",
     "recommendation": "Expand network security coverage with applied threat-modelling exercises."},
]

TREND_YEARS = ["2024", "2025", "2026"]
TREND_SERIES = {
    "Cloud Computing": [42, 55, 72],
    "Docker": [31, 46, 61],
    "Machine Learning": [54, 63, 72],
    "Cybersecurity": [33, 39, 45],
    "Generative AI": [12, 38, 66],
}
TREND_COLORS = {
    "Cloud Computing": "#4338CA",
    "Docker": "#2563AC",
    "Machine Learning": "#12866F",
    "Cybersecurity": "#B45309",
    "Generative AI": "#C0342A",
}

EMERGING_SKILLS = [
    {"skill": "Generative AI", "demand": 66, "growth": "+450%", "roles": "ML Engineer, AI Product Engineer", "priority": "Very High"},
    {"skill": "Cloud Computing", "demand": 72, "growth": "+71%", "roles": "Cloud Engineer, DevOps Engineer", "priority": "Very High"},
    {"skill": "Data Engineering", "demand": 49, "growth": "+58%", "roles": "Data Engineer, Analytics Engineer", "priority": "High"},
    {"skill": "Cybersecurity", "demand": 45, "growth": "+36%", "roles": "Security Analyst, SOC Engineer", "priority": "High"},
    {"skill": "Edge Computing", "demand": 28, "growth": "+94%", "roles": "IoT Engineer, Embedded Systems", "priority": "Medium"},
]

COURSES = [
    {"name": "Database Management Systems", "dept": "CSE", "sem": "4", "credits": 4,
     "skills": ["SQL", "Database Design", "Normalization", "Transactions", "Indexing"], "coverage": 78},
    {"name": "Programming Fundamentals", "dept": "CSE", "sem": "1", "credits": 4,
     "skills": ["Python", "Problem Solving", "Control Structures"], "coverage": 85},
    {"name": "Data Structures", "dept": "CSE", "sem": "2", "credits": 4,
     "skills": ["Algorithms", "Trees", "Graphs", "Complexity Analysis"], "coverage": 81},
    {"name": "Computer Networks", "dept": "CSE", "sem": "5", "credits": 3,
     "skills": ["TCP/IP", "Routing", "Network Security"], "coverage": 58},
    {"name": "Operating Systems", "dept": "CSE", "sem": "4", "credits": 4,
     "skills": ["Process Scheduling", "Memory Management", "Concurrency"], "coverage": 64},
    {"name": "Cloud Computing (Elective)", "dept": "CSE", "sem": "7", "credits": 3,
     "skills": ["Cloud Fundamentals"], "coverage": 24},
]

DBMS_MAPPING = [
    {"skill": "SQL", "confidence": 97},
    {"skill": "Database Design", "confidence": 91},
    {"skill": "Normalization", "confidence": 88},
    {"skill": "Transactions", "confidence": 84},
    {"skill": "PostgreSQL", "confidence": 74},
]
MAPPING_COURSE_LIST = ["Programming Fundamentals", "Data Structures", "DBMS", "Computer Networks", "Operating Systems", "Cloud Computing"]

RECOMMENDATIONS = [
    {"priority": 1, "title": "Introduce Cloud Computing", "growth": "31%", "coverage": 12,
     "action": "Introduce cloud fundamentals, deployment concepts and hands-on AWS/Azure laboratory work.", "status": "pending"},
    {"priority": 2, "title": "Expand Docker & Container Orchestration", "growth": "24%", "coverage": 18,
     "action": "Add a dedicated lab module on containerization, image builds and basic Kubernetes deployment.", "status": "pending"},
    {"priority": 3, "title": "Strengthen Data Engineering Coverage", "growth": "19%", "coverage": 21,
     "action": "Introduce ETL pipeline design and data pipeline orchestration in the analytics elective.", "status": "pending"},
]

DEPT_COMPARISON = [
    {"dept": "CSE", "alignment": 78, "gaps": 12, "emerging": 18},
    {"dept": "ECE", "alignment": 71, "gaps": 16, "emerging": 14},
    {"dept": "IIoT", "alignment": 64, "gaps": 21, "emerging": 23},
    {"dept": "IT", "alignment": 81, "gaps": 9, "emerging": 15},
]

REPORT_OPTIONS = [
    "Department-wise gap report",
    "Industry demand report",
    "Curriculum alignment report",
    "Emerging skills report",
    "Semester comparison",
]

EVIDENCE_BY_SKILL_DEFAULT = {
    "industry": [
        "54% of analyzed cloud-related job postings mention AWS",
        "Demand increased 18% over the last year",
        "Most common roles: Cloud Engineer, Backend Developer, DevOps Engineer",
    ],
    "curriculum": [
        "AWS not explicitly present in any course",
        "Cloud fundamentals partially covered in one elective",
        "No practical cloud laboratory identified",
    ],
    "conclusion": "High-priority curriculum gap",
}
