import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models
import schemas
from auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, require_current_user
)
from extractor import extract_skills_from_text, process_pdf_file, SKILL_TAXONOMY
from seed_data import seed_database, ROLE_PROFILES

# Initialize Database tables
Base.metadata.create_all(bind=engine)

# Seed database on startup
with next(get_db()) as db_session:
    seed_database(db_session)

app = FastAPI(
    title="SkillParity Intelligence API",
    description="Industry–Curriculum Intelligence & Skill Gap Analysis Platform REST API",
    version="2.0.0"
)

# Wide CORS middleware for local MVP execution
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------------------
# 1. AUTHENTICATION & USER MANAGEMENT
# ----------------------------------------------------------------------------

@app.post("/api/auth/register", response_model=schemas.TokenResponse, tags=["Authentication"])
def register(user_data: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    new_user = models.User(
        email=user_data.email.lower().strip(),
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name.strip(),
        role=user_data.role.lower().strip(),
        organization=user_data.organization.strip() if user_data.organization else ""
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize default student profile if role is student
    if new_user.role == "student":
        student_prof = models.StudentProfile(
            user_id=new_user.id,
            target_role="Backend Developer",
            extracted_skills=[],
            confirmed_skills=["Python", "SQL", "Git"]
        )
        db.add(student_prof)
        db.commit()

    token = create_access_token({"sub": new_user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": new_user
    }

@app.post("/api/auth/login", response_model=schemas.TokenResponse, tags=["Authentication"])
def login(login_data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == login_data.email.lower().strip()).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": user.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@app.get("/api/auth/me", response_model=schemas.UserResponse, tags=["Authentication"])
def get_me(current_user: models.User = Depends(require_current_user)):
    return current_user


# ----------------------------------------------------------------------------
# 2. CURRICULUM MANAGEMENT & PDF PROCESSING (UNIVERSITY)
# ----------------------------------------------------------------------------

@app.post("/api/curriculum/upload", response_model=schemas.CurriculumResponse, tags=["Curriculum"])
async def upload_curriculum(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF documents are supported.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        pdf_res = process_pdf_file(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process PDF text: {str(e)}")

    user_id = current_user.id if current_user else 1

    new_curriculum = models.Curriculum(
        user_id=user_id,
        title=f"Curriculum Analysis ({file.filename})",
        institution=current_user.organization if (current_user and current_user.organization) else "Global Institute of Technology",
        department="Computer Science & Engineering",
        academic_year="2026-2027",
        filename=file.filename,
        pages_processed=pdf_res["pages_processed"],
        courses_count=len(pdf_res["courses_detected"]),
        skills_detected_count=len(pdf_res["skills_detected"]),
        raw_extracted_skills=pdf_res["skills_detected"],
        confirmed_skills=pdf_res["skills_detected"],
        courses_detail=pdf_res["courses_detected"]
    )

    db.add(new_curriculum)
    db.commit()
    db.refresh(new_curriculum)

    return new_curriculum

@app.get("/api/curriculum/latest", response_model=schemas.CurriculumResponse, tags=["Curriculum"])
def get_latest_curriculum(db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user)):
    user_id = current_user.id if current_user else None
    if user_id:
        curriculum = db.query(models.Curriculum).filter(models.Curriculum.user_id == user_id).order_by(models.Curriculum.id.desc()).first()
        if curriculum:
            return curriculum

    # Fallback to the latest global curriculum in DB
    curriculum = db.query(models.Curriculum).order_by(models.Curriculum.id.desc()).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="No curriculum uploaded yet.")
    return curriculum

@app.put("/api/curriculum/{id}/skills", response_model=schemas.CurriculumResponse, tags=["Curriculum"])
def update_curriculum_skills(
    id: int,
    payload: schemas.CurriculumUpdateSkills,
    db: Session = Depends(get_db)
):
    curriculum = db.query(models.Curriculum).filter(models.Curriculum.id == id).first()
    if not curriculum:
        raise HTTPException(status_code=404, detail="Curriculum record not found")

    curriculum.confirmed_skills = sorted(list(set(payload.confirmed_skills)))
    db.commit()
    db.refresh(curriculum)
    return curriculum


# ----------------------------------------------------------------------------
# 3. RESUME UPLOAD & STUDENT PROFILE (STUDENT)
# ----------------------------------------------------------------------------

@app.post("/api/resume/upload", response_model=schemas.StudentProfileResponse, tags=["Student"])
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. Only PDF resumes are supported.")

    contents = await file.read()
    if len(contents) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        pdf_res = process_pdf_file(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process resume text: {str(e)}")

    user_id = current_user.id if current_user else 2

    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user_id).first()
    if not profile:
        profile = models.StudentProfile(
            user_id=user_id,
            target_role="Backend Developer",
            completed_projects=[]
        )
        db.add(profile)

    profile.resume_filename = file.filename
    profile.extracted_skills = pdf_res["skills_detected"]
    # Merge existing confirmed skills with newly detected skills
    merged = set(profile.confirmed_skills or []) | set(pdf_res["skills_detected"])
    profile.confirmed_skills = sorted(list(merged))

    db.commit()
    db.refresh(profile)
    return profile

@app.get("/api/student/profile", response_model=schemas.StudentProfileResponse, tags=["Student"])
def get_student_profile(db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user)):
    user_id = current_user.id if current_user else 2
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user_id).first()
    if not profile:
        profile = db.query(models.StudentProfile).order_by(models.StudentProfile.id.asc()).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Student profile not found")
    return profile

@app.put("/api/student/profile", response_model=schemas.StudentProfileResponse, tags=["Student"])
def update_student_profile(
    payload: schemas.StudentProfileUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 2
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user_id).first()
    if not profile:
        profile = db.query(models.StudentProfile).order_by(models.StudentProfile.id.asc()).first()

    if payload.target_role is not None:
        profile.target_role = payload.target_role
    if payload.confirmed_skills is not None:
        profile.confirmed_skills = sorted(list(set(payload.confirmed_skills)))
    if payload.completed_projects is not None:
        profile.completed_projects = payload.completed_projects

    db.commit()
    db.refresh(profile)
    return profile


# ----------------------------------------------------------------------------
# 4. SKILL EXTRACTION ENGINE
# ----------------------------------------------------------------------------

@app.post("/api/skills/extract", response_model=schemas.SkillExtractionResponse, tags=["Skill Extraction Engine"])
def extract_skills_endpoint(req: schemas.TextExtractionRequest):
    skills, details = extract_skills_from_text(req.text)
    return {
        "skills": skills,
        "details": details
    }


# ----------------------------------------------------------------------------
# 5. INDUSTRY DATA & SKILL INTELLIGENCE
# ----------------------------------------------------------------------------

@app.get("/api/industry/jobs", response_model=List[schemas.JobPostingResponse], tags=["Industry Intelligence"])
def get_industry_jobs(
    sector: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.JobPosting)
    if sector and sector.lower() != "all":
        query = query.filter(models.JobPosting.sector.ilike(f"%{sector}%"))
    if q:
        search_fmt = f"%{q}%"
        query = query.filter(
            (models.JobPosting.title.ilike(search_fmt)) |
            (models.JobPosting.company.ilike(search_fmt)) |
            (models.JobPosting.description.ilike(search_fmt))
        )
    return query.all()

@app.post("/api/industry/jobs", response_model=schemas.JobPostingResponse, tags=["Industry Intelligence"])
def create_job_posting(payload: schemas.JobPostingCreate, db: Session = Depends(get_db)):
    new_job = models.JobPosting(
        title=payload.title,
        company=payload.company,
        location=payload.location,
        sector=payload.sector,
        description=payload.description,
        skills=payload.skills,
        date="2026-09-27",
        is_demo=False
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

@app.get("/api/industry/skills", tags=["Industry Intelligence"])
def get_industry_skill_analytics(db: Session = Depends(get_db)):
    """Calculates skill frequency, demand percentage, growth trend, and categories."""
    jobs = db.query(models.JobPosting).all()
    total_jobs = len(jobs) if jobs else 1

    skill_counts = {}
    for job in jobs:
        for skill in (job.skills or []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

    # Skill taxonomy map for categories
    category_map = {item["canonical_name"]: item["category"] for item in SKILL_TAXONOMY}

    analytics = []
    for skill, count in skill_counts.items():
        demand_pct = round((count / total_jobs) * 100)
        category = category_map.get(skill, "Other")
        
        # Calculate simulated trend comparison
        growth_pct = 15 if skill in ["Docker", "AWS", "FastAPI", "LLMs", "PyTorch", "Kubernetes"] else (5 if skill in ["Python", "SQL", "Git"] else -2)

        analytics.append({
            "skill": skill,
            "category": category,
            "jobCount": count,
            "demandPct": demand_pct,
            "growthPct": growth_pct,
            "status": "Emerging" if growth_pct >= 15 else ("Declining" if growth_pct < 0 else "Stable")
        })

    analytics.sort(key=lambda x: x["demandPct"], reverse=True)
    return analytics

@app.get("/api/industry/roles", tags=["Industry Intelligence"])
def get_role_mappings():
    """Returns standardized target role profiles and required/recommended skills."""
    return ROLE_PROFILES


# ----------------------------------------------------------------------------
# 6. GAP ENGINES (UNIVERSITY & STUDENT)
# ----------------------------------------------------------------------------

@app.get("/api/gap/university", tags=["Gap Analysis"])
def get_university_gap_analysis(db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user)):
    """
    Compares Curriculum Skills vs Industry Demand across analyzed job postings.
    Generates a matrix with Status: Match, Critical Gap, Partial Gap, Emerging, Obsolete.
    """
    # Get latest curriculum
    user_id = current_user.id if current_user else None
    curriculum = None
    if user_id:
        curriculum = db.query(models.Curriculum).filter(models.Curriculum.user_id == user_id).order_by(models.Curriculum.id.desc()).first()
    if not curriculum:
        curriculum = db.query(models.Curriculum).order_by(models.Curriculum.id.desc()).first()

    curr_skills = set(curriculum.confirmed_skills if curriculum else ["Python", "Java", "C++", "SQL", "JavaScript", "HTML5 & CSS3", "Problem Solving"])

    # Calculate industry demand
    jobs = db.query(models.JobPosting).all()
    total_jobs = len(jobs) if jobs else 1

    skill_counts = {}
    for job in jobs:
        for skill in (job.skills or []):
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

    matrix = []
    for item in SKILL_TAXONOMY:
        skill = item["canonical_name"]
        category = item["category"]
        count = skill_counts.get(skill, 0)
        demand_pct = round((count / total_jobs) * 100)

        in_curriculum = skill in curr_skills

        # Determine status
        if in_curriculum and demand_pct >= 30:
            status = "Match"
        elif in_curriculum and demand_pct < 10:
            status = "Obsolete / Declining"
        elif not in_curriculum and demand_pct >= 40:
            status = "Critical Gap"
        elif not in_curriculum and demand_pct >= 20:
            status = "Partial Gap"
        elif skill in ["LLMs", "FastAPI", "PyTorch", "Kubernetes"] and demand_pct >= 15:
            status = "Emerging Skill"
        elif in_curriculum:
            status = "Match"
        else:
            status = "Partial Gap"

        matrix.append({
            "skill": skill,
            "category": category,
            "demandPct": demand_pct,
            "inCurriculum": in_curriculum,
            "status": status,
            "jobCount": count
        })

    matrix.sort(key=lambda x: x["demandPct"], reverse=True)
    return matrix

@app.get("/api/gap/student", tags=["Gap Analysis"])
def get_student_gap_analysis(db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user)):
    """
    Compares Student Skills vs Target Role required and recommended skills.
    Categorizes skills into MATCH, PARTIAL, GAP, CRITICAL GAP, EMERGING.
    Calculates exact readiness percentage.
    """
    user_id = current_user.id if current_user else 2
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user_id).first()
    if not profile:
        profile = db.query(models.StudentProfile).order_by(models.StudentProfile.id.asc()).first()

    target_role = profile.target_role if profile else "Backend Developer"
    student_skills = set(profile.confirmed_skills if profile else ["Python", "SQL", "Git"])

    role_profile = ROLE_PROFILES.get(target_role, ROLE_PROFILES["Backend Developer"])
    required_skills = role_profile["required"]
    recommended_skills = role_profile["recommended"]

    all_target_skills = required_skills + recommended_skills

    skill_gaps = []
    matched_count = 0

    for skill in required_skills:
        if skill in student_skills:
            status = "MATCH"
            matched_count += 1
        elif any(s in student_skills for s in ["Python", "JavaScript", "C++"]) and skill in ["FastAPI", "React", "Node.js"]:
            status = "PARTIAL"
            matched_count += 0.5
        else:
            status = "CRITICAL GAP"

        skill_gaps.append({
            "skill": skill,
            "type": "Required",
            "status": status
        })

    for skill in recommended_skills:
        if skill in student_skills:
            status = "MATCH"
            matched_count += 1
        elif skill in ["LLMs", "PyTorch", "Kubernetes"]:
            status = "EMERGING"
        else:
            status = "GAP"

        skill_gaps.append({
            "skill": skill,
            "type": "Recommended",
            "status": status
        })

    alignment_pct = round((matched_count / len(all_target_skills)) * 100) if all_target_skills else 0

    return {
        "target_role": target_role,
        "alignment_pct": min(alignment_pct, 100),
        "student_skills": sorted(list(student_skills)),
        "skill_gaps": skill_gaps
    }


# ----------------------------------------------------------------------------
# 7. RECOMMENDATIONS & CAREER ROADMAP
# ----------------------------------------------------------------------------

@app.get("/api/recommendations/university", response_model=List[schemas.RecommendationResponse], tags=["Recommendations"])
def get_university_recommendations(db: Session = Depends(get_db)):
    recos = db.query(models.Recommendation).filter(models.Recommendation.target_type == "university").all()
    return sorted(recos, key=lambda r: r.priority)

@app.get("/api/recommendations/student", tags=["Recommendations"])
def get_student_recommendations(db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user)):
    user_id = current_user.id if current_user else 2
    profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user_id).first()
    if not profile:
        profile = db.query(models.StudentProfile).order_by(models.StudentProfile.id.asc()).first()

    student_skills = set(profile.confirmed_skills if profile else ["Python", "SQL"])

    recommendations = []
    if "Docker" not in student_skills:
        recommendations.append({
            "title": "Master Containerization with Docker",
            "missing_skill": "Docker",
            "action": "Complete a 4-hour hands-on lab on Dockerfile design, multi-container compose, and local microservice deployment.",
            "recommended_project": "Containerized Task Manager REST API",
            "priority": "High"
        })
    if "REST APIs" not in student_skills and "FastAPI" not in student_skills:
        recommendations.append({
            "title": "Build Production REST APIs using FastAPI",
            "missing_skill": "REST APIs / FastAPI",
            "action": "Learn FastAPI routing, Pydantic data validation, JWT authentication, and Swagger documentation.",
            "recommended_project": "E-Commerce REST API Engine",
            "priority": "High"
        })
    if "AWS" not in student_skills and "Cloud Computing" not in student_skills:
        recommendations.append({
            "title": "Learn AWS Cloud Fundamentals",
            "missing_skill": "AWS / Cloud",
            "action": "Set up AWS Free Tier, deploy an EC2 instance, and configure S3 bucket object storage.",
            "recommended_project": "Cloud File Storage & CDN Service",
            "priority": "Medium"
        })
    if "LLMs" not in student_skills:
        recommendations.append({
            "title": "Explore GenAI & Prompt Engineering",
            "missing_skill": "LLMs",
            "action": "Integrate an OpenAI/HuggingFace API with Python to build a smart search engine.",
            "recommended_project": "AI Resume & Syllabus Summarizer",
            "priority": "Medium"
        })

    return recommendations

@app.get("/api/student/roadmap", tags=["Student"])
def get_student_roadmap(db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user)):
    gap_data = get_student_gap_analysis(db, current_user)
    student_skills = set(gap_data["student_skills"])
    target_role = gap_data["target_role"]

    roadmap = [
        {
            "stage": "1. FOUNDATION",
            "title": "Programming & Data Fundamentals",
            "skills": [
                {"name": "Python", "acquired": "Python" in student_skills},
                {"name": "SQL", "acquired": "SQL" in student_skills},
                {"name": "Git", "acquired": "Git" in student_skills}
            ],
            "description": "Master core syntax, algorithm complexity, database queries, and git version control."
        },
        {
            "stage": "2. CORE",
            "title": "Backend Architecture & Web APIs",
            "skills": [
                {"name": "REST APIs", "acquired": "REST APIs" in student_skills},
                {"name": "FastAPI", "acquired": "FastAPI" in student_skills},
                {"name": "JWT Auth", "acquired": "Communication" in student_skills}
            ],
            "description": "Construct high-performance RESTful APIs, data validation schemas, and secure token auth."
        },
        {
            "stage": "3. PRODUCTION",
            "title": "DevOps, Containerization & Cloud",
            "skills": [
                {"name": "Docker", "acquired": "Docker" in student_skills},
                {"name": "AWS", "acquired": "AWS" in student_skills},
                {"name": "CI/CD Pipelines", "acquired": "CI/CD" in student_skills}
            ],
            "description": "Containerize microservices, write automated unit tests, and configure cloud CI/CD deployment."
        },
        {
            "stage": "4. CAREER READY",
            "title": "Capstone Projects & Industry Placement",
            "skills": [
                {"name": "System Architecture", "acquired": len(student_skills) >= 6},
                {"name": "Portfolio Projects", "acquired": len(student_skills) >= 5},
                {"name": "Interview Preparation", "acquired": True}
            ],
            "description": "Complete production capstone applications, showcase GitHub repository, and clear technical interviews."
        }
    ]

    return {
        "target_role": target_role,
        "alignment_pct": gap_data["alignment_pct"],
        "stages": roadmap
    }

@app.get("/api/student/projects", tags=["Student"])
def get_student_project_recommendations():
    return [
        {
            "title": "Production-Ready Task Management REST API",
            "difficulty": "Intermediate",
            "duration": "2 weeks",
            "skills_covered": ["FastAPI", "SQL", "Docker", "REST APIs", "Git"],
            "description": "Build a multi-user task management backend with JWT authorization, PostgreSQL database migrations, and Docker containerization."
        },
        {
            "title": "Automated Multi-Cloud Microservice Pipeline",
            "difficulty": "Advanced",
            "duration": "3 weeks",
            "skills_covered": ["AWS", "Docker", "Kubernetes", "Linux", "CI/CD"],
            "description": "Configure GitHub Actions CI/CD to build Docker containers and deploy to AWS Elastic Kubernetes Service (EKS)."
        },
        {
            "title": "GenAI Document Search & RAG Pipeline",
            "difficulty": "Advanced",
            "duration": "2 weeks",
            "skills_covered": ["Python", "LLMs", "PyTorch", "FastAPI", "Data Analysis"],
            "description": "Extract text from PDF documents, create vector embeddings, and build an interactive Q&A assistant powered by LLMs."
        }
    ]


# ----------------------------------------------------------------------------
# 8. EMPLOYER EXPERIENCE & FEEDBACK
# ----------------------------------------------------------------------------

@app.post("/api/employer/requirements", response_model=schemas.EmployerRequirementCreate, tags=["Employer"])
def create_employer_requirement(
    payload: schemas.EmployerRequirementCreate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 3
    req = models.EmployerRequirement(
        user_id=user_id,
        company=payload.company,
        role=payload.role,
        required_skills=payload.required_skills,
        recommended_skills=payload.recommended_skills
    )
    db.add(req)
    
    # Also record job posting to update industry dataset
    job = models.JobPosting(
        title=f"{payload.role} (Employer Signal)",
        company=payload.company,
        location="Remote / Regional",
        sector="Employer Input",
        description=f"Direct employer requirement created by {payload.company} for role {payload.role}.",
        skills=payload.required_skills + payload.recommended_skills,
        date="2026-09-27",
        is_demo=False
    )
    db.add(job)

    db.commit()
    return payload

@app.post("/api/employer/feedback", response_model=schemas.EmployerFeedbackCreate, tags=["Employer"])
def create_employer_feedback(
    payload: schemas.EmployerFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 3
    fb = models.EmployerFeedback(
        user_id=user_id,
        company=payload.company,
        difficult_skills=payload.difficult_skills,
        emerging_skills=payload.emerging_skills,
        missing_skills=payload.missing_skills,
        target_technologies=payload.target_technologies,
        notes=payload.notes
    )
    db.add(fb)
    db.commit()
    return payload

@app.post("/api/employer/validations", tags=["Employer"])
def create_skill_validation(
    payload: schemas.SkillValidationCreate,
    db: Session = Depends(get_db),
    current_user: Optional[models.User] = Depends(get_current_user)
):
    user_id = current_user.id if current_user else 3
    val = models.SkillValidation(
        user_id=user_id,
        company=payload.company,
        skill_name=payload.skill_name,
        skill_level=payload.skill_level,
        importance=payload.importance
    )
    db.add(val)
    db.commit()
    return {"status": "success", "message": "Skill validation recorded"}

@app.get("/api/employer/signals", tags=["Employer"])
def get_employer_signals(db: Session = Depends(get_db)):
    reqs = db.query(models.EmployerRequirement).all()
    fbs = db.query(models.EmployerFeedback).all()

    total_signals = len(reqs) + len(fbs)

    difficult_skills_counter = {}
    missing_skills_counter = {}
    for fb in fbs:
        for s in (fb.difficult_skills or []):
            difficult_skills_counter[s] = difficult_skills_counter.get(s, 0) + 1
        for s in (fb.missing_skills or []):
            missing_skills_counter[s] = missing_skills_counter.get(s, 0) + 1

    return {
        "total_signals": max(total_signals, 127),  # Includes dataset signals
        "employer_requirements_count": len(reqs),
        "employer_feedbacks_count": len(fbs),
        "top_difficult_to_find": sorted(difficult_skills_counter.items(), key=lambda x: x[1], reverse=True)[:5],
        "top_missing_in_graduates": sorted(missing_skills_counter.items(), key=lambda x: x[1], reverse=True)[:5],
        "recent_feedbacks": [
            {
                "company": fb.company,
                "notes": fb.notes,
                "target_tech": fb.target_technologies,
                "created_at": fb.created_at.strftime("%Y-%m-%d")
            }
            for fb in fbs
        ]
    }


# ----------------------------------------------------------------------------
# 9. OVERVIEW ANALYTICS & GLOBAL SEARCH
# ----------------------------------------------------------------------------

@app.get("/api/analytics/university-overview", tags=["Analytics"])
def get_university_overview_analytics(db: Session = Depends(get_db), current_user: Optional[models.User] = Depends(get_current_user)):
    gap_matrix = get_university_gap_analysis(db, current_user)

    total = len(gap_matrix)
    matches = sum(1 for item in gap_matrix if item["status"] == "Match")
    critical_gaps = sum(1 for item in gap_matrix if item["status"] == "Critical Gap")
    emerging_skills = sum(1 for item in gap_matrix if item["status"] == "Emerging Skill")

    alignment_pct = round((matches / total) * 100) if total > 0 else 72
    signals = db.query(models.EmployerFeedback).count() + db.query(models.EmployerRequirement).count() + 124

    return {
        "alignment_pct": alignment_pct,
        "critical_gaps_count": critical_gaps,
        "emerging_skills_count": emerging_skills,
        "industry_alignment_pct": alignment_pct,
        "employer_signals_count": signals,
        "total_skills_analyzed": total
    }

@app.get("/api/search", tags=["Global Search"])
def global_search(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    query_str = q.strip().lower()

    # Search skills in taxonomy
    matching_skills = [
        item["canonical_name"] for item in SKILL_TAXONOMY
        if query_str in item["canonical_name"].lower() or any(query_str in alias for alias in item["aliases"])
    ]

    # Search roles
    matching_roles = [
        role for role in ROLE_PROFILES.keys() if query_str in role.lower()
    ]

    # Search jobs
    jobs = db.query(models.JobPosting).filter(
        (models.JobPosting.title.ilike(f"%{query_str}%")) |
        (models.JobPosting.company.ilike(f"%{query_str}%")) |
        (models.JobPosting.description.ilike(f"%{query_str}%"))
    ).all()

    # Search recommendations
    recos = db.query(models.Recommendation).filter(
        (models.Recommendation.title.ilike(f"%{query_str}%")) |
        (models.Recommendation.description.ilike(f"%{query_str}%"))
    ).all()

    return {
        "query": q,
        "skills": matching_skills,
        "roles": matching_roles,
        "jobs": [
            {"id": j.id, "title": j.title, "company": j.company, "sector": j.sector}
            for j in jobs
        ],
        "recommendations": [
            {"id": r.id, "title": r.title, "gap_skill": r.gap_skill}
            for r in recos
        ]
    }


# ----------------------------------------------------------------------------
# 10. SERVE STATIC FRONTEND
# ----------------------------------------------------------------------------

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists() and not os.getenv("VERCEL"):
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
elif not os.getenv("VERCEL"):
    @app.get("/")
    def frontend_missing():
        return {
            "detail": f"Frontend folder not found at {FRONTEND_DIR}. Expected html files in frontend/ directory."
        }
