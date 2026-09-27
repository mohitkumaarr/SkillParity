from pydantic import BaseModel, EmailStr
from typing import List, Optional, Any, Dict

# Auth Schemas
class UserRegister(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # 'university', 'student', 'employer'
    organization: Optional[str] = ""

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    organization: Optional[str] = ""

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Skill Extraction Schemas
class TextExtractionRequest(BaseModel):
    text: str

class ExtractedSkillItem(BaseModel):
    canonical_name: str
    category: str
    matched_alias: str

class SkillExtractionResponse(BaseModel):
    skills: List[str]
    details: List[ExtractedSkillItem]

# Curriculum Schemas
class CurriculumUpdateSkills(BaseModel):
    confirmed_skills: List[str]

class CurriculumResponse(BaseModel):
    id: int
    title: str
    institution: str
    department: str
    academic_year: str
    filename: Optional[str]
    pages_processed: int
    courses_count: int
    skills_detected_count: int
    raw_extracted_skills: List[str]
    confirmed_skills: List[str]
    courses_detail: List[Dict[str, Any]]

    class Config:
        from_attributes = True

# Student Profile Schemas
class StudentProfileUpdate(BaseModel):
    target_role: Optional[str] = None
    confirmed_skills: Optional[List[str]] = None
    completed_projects: Optional[List[str]] = None

class StudentProfileResponse(BaseModel):
    id: int
    user_id: int
    resume_filename: Optional[str]
    extracted_skills: List[str]
    confirmed_skills: List[str]
    target_role: str
    completed_projects: List[str]

    class Config:
        from_attributes = True

# Job & Industry Schemas
class JobPostingResponse(BaseModel):
    id: int
    title: str
    company: str
    location: str
    sector: str
    description: str
    skills: List[str]
    date: str
    is_demo: bool

    class Config:
        from_attributes = True

class JobPostingCreate(BaseModel):
    title: str
    company: str
    location: str
    sector: str
    description: str
    skills: List[str]

# Employer Requirements & Feedback
class EmployerRequirementCreate(BaseModel):
    company: str
    role: str
    required_skills: List[str]
    recommended_skills: List[str]

class EmployerFeedbackCreate(BaseModel):
    company: str
    difficult_skills: List[str]
    emerging_skills: List[str]
    missing_skills: List[str]
    target_technologies: List[str]
    notes: Optional[str] = ""

class SkillValidationCreate(BaseModel):
    company: str
    skill_name: str
    skill_level: str
    importance: str

# Recommendation Schemas
class RecommendationResponse(BaseModel):
    id: int
    target_type: str
    title: str
    category: str
    description: str
    suggested_module: Optional[str]
    suggested_project: Optional[str]
    suggested_assessment: Optional[str]
    gap_skill: str
    priority: int
    status: str

    class Config:
        from_attributes = True
