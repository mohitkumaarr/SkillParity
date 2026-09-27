# SkillParity — Industry–Curriculum Intelligence Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141%2B-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0%2B-D76A03?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![SQLite](https://img.shields.io/badge/SQLite-MVP%20Persistence-003B57?style=flat&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

> **Bringing Higher Education into Parity with Live Industry Demand.**
> SkillParity is an enterprise-grade intelligence platform that bridges the gap between what regional labor markets demand and what academic institutions teach.

---

## 🏛️ Executive Summary

Traditional higher education curricula often lag behind rapidly evolving technology standards. **SkillParity** establishes a closed-loop intelligence engine:

```text
  ┌───────────────────────┐
  │  LIVE INDUSTRY DATA   │ (Job postings, employer requirements)
  └───────────┬───────────┘
              ▼
  ┌───────────────────────┐
  │   SKILL EXTRACTION    │ (PyPDF text parsing, regex boundary matching)
  └───────────┬───────────┘
              ▼
  ┌───────────────────────┐
  │ TAXONOMY NORMALIZATION│ (13-category canonical normalization)
  └───────────┬───────────┘
              ▼
  ┌───────────────────────┐
  │   SKILL GAP ENGINE    │ (Curriculum vs. Industry Demand Matrix)
  └───────────┬───────────┘
              ▼
  ┌───────────────────────┐
  │ ACTIONABLE OUTCOMES   │ (Curriculum updates, student roadmaps, employer signals)
  └───────────────────────┘
```

---

## ✨ Key Features

### 🏫 1. University Portal (Institutional Workspace)
- **Curriculum Alignment Score**: Dominant institutional metric (e.g. `72%` alignment) calculated against regional market demand.
- **Syllabus PDF Upload & Parser**: Upload course PDF documents; processed page-by-page via `PyPDF`.
- **Skill Extraction & Review**: Automated identification of taught skills with a full review, edit, remove, and add interface.
- **Curriculum vs. Industry Gap Matrix**: Evaluates skills as `MATCH`, `PARTIAL GAP`, `CRITICAL GAP`, `EMERGING SKILL`, or `OBSOLETE/DECLINING`.
- **Actionable Academic Recommendations**: Priority-ranked curriculum module updates, lab projects, and course revisions generated directly from detected gaps.

### 🎓 2. Student Portal (Career Readiness Workspace)
- **Resume PDF Parser**: Extract skills directly from student resumes using PyPDF taxonomy lookup.
- **Target Role Profiler**: Select target career tracks (*Backend Developer, AI Engineer, Cloud & DevOps Engineer, Data Analyst, Full Stack Developer, Cybersecurity Specialist*).
- **Personal Gap Score**: Calculates target role readiness percentage (e.g. `68%` readiness).
- **Horizontal 4-Stage Roadmap**: Dynamic pipeline (*01 Foundation → 02 Core Skills → 03 Production → 04 Career Ready*) mapped to missing skills.
- **Tailored Portfolio Projects**: Project recommendations customized to bridge specific missing student gaps.

### 💼 3. Employer Portal (Industry Signals Workspace)
- **Create Role Requirements**: Define mandatory and recommended skills for open positions to feed the regional demand dataset.
- **Capability Validation**: Evaluate skill levels (*Beginner, Intermediate, Advanced*) and importance.
- **Graduate Skill Gap Feedback**: Submit structured feedback on difficult-to-find skills, emerging technologies, and missing graduate capabilities.

### 🔍 4. Global Search & Analytics
- Cross-entity global search across skills, target roles, job postings, and academic recommendations.
- Interactive Chart.js visualizations styled with warm neutral editorial palettes.

---

## 🎨 Visual Identity & Aesthetic

Designed with a warm neutral editorial palette:
- **Warm Ivory / Soft Cream** (`#F5F0E6` / `#FAF7F2`) main surfaces.
- **Charcoal** (`#1C1C1A`) primary typography.
- **Muted Terracotta** (`#B85C3A`) primary brand accent.
- **Deep Sage Green** (`#355C52`) secondary accent.
- **IBM Plex Sans**, **Manrope**, and **JetBrains Mono** typography.

---

## 🛠️ Technology Stack

* **Backend**: Python 3.10+, FastAPI, SQLAlchemy, SQLite, PyPDF, PyJWT, Passlib (PBKDF2 HMAC SHA256)
* **Frontend**: Vanilla JavaScript (Single Page Application Router & Fetch API), HTML5, Custom CSS Design System, Chart.js 4.4
* **Testing**: Automated Python verification suite (`test_verification.py`)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mohitkumaarr/SkillParity.git
   cd SkillParity
   ```

2. **Set Up Virtual Environment**:
   ```bash
   # On Windows
   python -m venv venv
   .\venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```

4. **Run the FastAPI Web Application Server**:
   ```bash
   python -m uvicorn --app-dir backend main:app --reload --port 8000
   ```

5. **Open in Browser**:
   - Web Platform: [http://localhost:8000/](http://localhost:8000/)
   - OpenAPI Swagger Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Running Verification Tests

To run the automated verification suite covering all REST API endpoints, JWT auth, gap engines, recommendations, and search:

```bash
python backend/test_verification.py
```

---

## 📂 Project Structure

```text
SkillParity/
├── backend/
│   ├── main.py              # FastAPI application entrypoint & API routes
│   ├── database.py          # SQLAlchemy engine & session setup
│   ├── models.py            # SQLite database models
│   ├── schemas.py           # Pydantic request & response schemas
│   ├── auth.py              # JWT authentication & PBKDF2 hashing
│   ├── extractor.py         # Skill extraction & PyPDF text parser engine
│   ├── seed_data.py         # Demo dataset & initial seed data
│   ├── requirements.txt     # Python backend dependencies
│   └── test_verification.py # Automated test suite
├── frontend/
│   ├── index.html           # SPA HTML shell & top navigation
│   ├── styles.css           # Warm neutral editorial design system
│   └── app.js               # Client SPA router, view renderers & API client
├── .gitignore
└── README.md
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for details.
