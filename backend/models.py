from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'university', 'student', 'employer'
    organization = Column(String, nullable=True)  # University or Company name
    created_at = Column(DateTime, default=datetime.utcnow)

    curricula = relationship("Curriculum", back_populates="owner")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    employer_requirements = relationship("EmployerRequirement", back_populates="owner")
    employer_feedbacks = relationship("EmployerFeedback", back_populates="owner")

class Curriculum(Base):
    __tablename__ = "curricula"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    institution = Column(String, nullable=False)
    department = Column(String, nullable=False)
    academic_year = Column(String, nullable=False)
    filename = Column(String, nullable=True)
    pages_processed = Column(Integer, default=0)
    courses_count = Column(Integer, default=0)
    skills_detected_count = Column(Integer, default=0)
    raw_extracted_skills = Column(JSON, default=list)  # List of skill names
    confirmed_skills = Column(JSON, default=list)      # List of approved skill names
    courses_detail = Column(JSON, default=list)        # List of detected course dicts
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="curricula")

class StudentProfile(Base):
    __tablename__ = "student_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    resume_filename = Column(String, nullable=True)
    extracted_skills = Column(JSON, default=list)
    confirmed_skills = Column(JSON, default=list)
    target_role = Column(String, default="Backend Developer")
    completed_projects = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="student_profile")

class JobPosting(Base):
    __tablename__ = "job_postings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    sector = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    skills = Column(JSON, default=list)  # List of canonical skill names
    date = Column(String, nullable=False)
    is_demo = Column(Boolean, default=True)

class EmployerRequirement(Base):
    __tablename__ = "employer_requirements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company = Column(String, nullable=False)
    role = Column(String, nullable=False)
    required_skills = Column(JSON, default=list)
    recommended_skills = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="employer_requirements")

class EmployerFeedback(Base):
    __tablename__ = "employer_feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company = Column(String, nullable=False)
    difficult_skills = Column(JSON, default=list)
    emerging_skills = Column(JSON, default=list)
    missing_skills = Column(JSON, default=list)
    target_technologies = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="employer_feedbacks")

class SkillValidation(Base):
    __tablename__ = "skill_validations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company = Column(String, nullable=False)
    skill_name = Column(String, nullable=False)
    skill_level = Column(String, nullable=False) # 'Beginner', 'Intermediate', 'Advanced'
    importance = Column(String, nullable=False)  # 'Required', 'Preferred'
    created_at = Column(DateTime, default=datetime.utcnow)

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    target_type = Column(String, nullable=False) # 'university' or 'student'
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)   # e.g., 'Curriculum Update', 'New Course', 'Lab Project'
    description = Column(Text, nullable=False)
    suggested_module = Column(String, nullable=True)
    suggested_project = Column(String, nullable=True)
    suggested_assessment = Column(String, nullable=True)
    gap_skill = Column(String, nullable=False)
    priority = Column(Integer, default=1)        # 1 = High, 2 = Medium, 3 = Low
    status = Column(String, default="active")    # 'active', 'accepted', 'dismissed'
    created_at = Column(DateTime, default=datetime.utcnow)
