from sqlalchemy.orm import Session
import models
from auth import hash_password

ROLE_PROFILES = {
    "Backend Developer": {
        "required": ["Python", "SQL", "REST APIs", "FastAPI", "Git"],
        "recommended": ["Docker", "Redis", "Microservices", "CI/CD", "AWS"]
    },
    "AI Engineer": {
        "required": ["Python", "Machine Learning", "PyTorch", "TensorFlow", "SQL"],
        "recommended": ["LLMs", "Deep Learning", "Data Analysis", "Docker", "FastAPI"]
    },
    "Cloud & DevOps Engineer": {
        "required": ["AWS", "Docker", "Kubernetes", "Linux", "Git"],
        "recommended": ["Cloud Computing", "CI/CD", "Python", "REST APIs", "Cybersecurity"]
    },
    "Data Analyst": {
        "required": ["SQL", "Python", "Data Analysis", "Communication"],
        "recommended": ["Machine Learning", "FastAPI", "Git", "Cloud Computing"]
    },
    "Full Stack Developer": {
        "required": ["JavaScript", "React", "Python", "REST APIs", "SQL", "HTML5 & CSS3"],
        "recommended": ["TypeScript", "FastAPI", "Docker", "Git", "AWS"]
    },
    "Cybersecurity Specialist": {
        "required": ["Cybersecurity", "Linux", "Python", "SQL"],
        "recommended": ["AWS", "Docker", "REST APIs", "Problem Solving"]
    }
}

DEMO_JOBS = [
    {
        "title": "Senior Backend Developer",
        "company": "Nexus Financial SaaS",
        "location": "San Francisco, CA (Hybrid)",
        "sector": "FinTech & Enterprise SaaS",
        "description": "Building high-throughput microservices using Python, FastAPI, SQL, and Docker. Experience with REST APIs, Redis, and AWS required.",
        "skills": ["Python", "FastAPI", "SQL", "REST APIs", "Docker", "Redis", "AWS", "Git"],
        "date": "2026-09-20",
        "is_demo": True
    },
    {
        "title": "Cloud Operations & DevOps Engineer",
        "company": "Apex Cloud Systems",
        "location": "Austin, TX (Remote)",
        "sector": "Cloud Infrastructure",
        "description": "Manage Kubernetes clusters, AWS cloud infrastructure, Docker containers, and CI/CD pipelines. Strong Linux and Git skills mandatory.",
        "skills": ["AWS", "Docker", "Kubernetes", "Linux", "Git", "CI/CD", "Cloud Computing"],
        "date": "2026-09-22",
        "is_demo": True
    },
    {
        "title": "AI & GenAI Solutions Engineer",
        "company": "Cognitive Scale AI",
        "location": "Boston, MA",
        "sector": "Artificial Intelligence & ML",
        "description": "Deploy LLM workflows, PyTorch models, and RAG pipelines in production using FastAPI and Docker. PyTorch and ML experience needed.",
        "skills": ["Python", "Machine Learning", "PyTorch", "LLMs", "FastAPI", "Docker", "Data Analysis"],
        "date": "2026-09-24",
        "is_demo": True
    },
    {
        "title": "Data Platform Engineer",
        "company": "Quantum Insights",
        "location": "New York, NY",
        "sector": "Data Analytics",
        "description": "Design data analysis pipelines, SQL query optimizers, and automated ETL jobs using Python, PostgreSQL, and AWS.",
        "skills": ["Python", "SQL", "Data Analysis", "AWS", "Git", "REST APIs"],
        "date": "2026-09-21",
        "is_demo": True
    },
    {
        "title": "Full Stack Engineer",
        "company": "Vanguard Tech Solutions",
        "location": "Seattle, WA",
        "sector": "Enterprise Software",
        "description": "Develop client-facing React web apps and Python REST API backends with PostgreSQL database backends.",
        "skills": ["JavaScript", "React", "Python", "REST APIs", "SQL", "HTML5 & CSS3", "Git"],
        "date": "2026-09-25",
        "is_demo": True
    },
    {
        "title": "Cybersecurity Infrastructure Analyst",
        "company": "Securitas Enterprise",
        "location": "Chicago, IL",
        "sector": "Cybersecurity & Defense",
        "description": "Audit network security, manage Linux security protocols, write automation scripts in Python, and enforce cloud access controls.",
        "skills": ["Cybersecurity", "Linux", "Python", "SQL", "AWS", "Problem Solving"],
        "date": "2026-09-18",
        "is_demo": True
    },
    {
        "title": "IoT Systems Developer",
        "company": "SmartGrid Automation",
        "location": "San Jose, CA",
        "sector": "IoT & Embedded Hardware",
        "description": "Build embedded systems protocols, C++ microcontrollers, Python edge processing algorithms, and MQTT communication bridges.",
        "skills": ["C++", "IoT", "Python", "Linux", "Problem Solving"],
        "date": "2026-09-15",
        "is_demo": True
    },
    {
        "title": "Backend Systems Architect",
        "company": "Hyperion Software",
        "location": "Denver, CO",
        "sector": "IT & Software",
        "description": "Design distributed microservices in Go and Python, utilizing SQL databases, Docker containerization, and AWS serverless components.",
        "skills": ["Python", "SQL", "REST APIs", "Microservices", "Docker", "AWS", "Git"],
        "date": "2026-09-26",
        "is_demo": True
    },
    {
        "title": "Machine Learning Engineer",
        "company": "DeepVision Systems",
        "location": "Palo Alto, CA",
        "sector": "Artificial Intelligence & ML",
        "description": "Train and deploy deep learning neural networks with PyTorch and TensorFlow. Serve predictions via FastAPI REST endpoints.",
        "skills": ["Python", "Machine Learning", "Deep Learning", "PyTorch", "TensorFlow", "FastAPI"],
        "date": "2026-09-23",
        "is_demo": True
    },
    {
        "title": "Junior Backend Developer",
        "company": "CloudStart Technologies",
        "location": "Atlanta, GA",
        "sector": "Enterprise SaaS",
        "description": "Assist in building RESTful web services in Python and FastAPI, managing Git repositories, and writing SQL migrations.",
        "skills": ["Python", "SQL", "REST APIs", "Git", "Communication"],
        "date": "2026-09-25",
        "is_demo": True
    }
]

def seed_database(db: Session):
    # Check if users already exist
    user_count = db.query(models.User).count()
    if user_count == 0:
        # Create default demo accounts for quick testing
        demo_uni_user = models.User(
            email="university@demo.edu",
            hashed_password=hash_password("password123"),
            full_name="Dr. Eleanor Vance",
            role="university",
            organization="Global Institute of Technology"
        )
        demo_student_user = models.User(
            email="student@demo.edu",
            hashed_password=hash_password("password123"),
            full_name="Alex Mercer",
            role="student",
            organization="Global Institute of Technology"
        )
        demo_employer_user = models.User(
            email="employer@demo.com",
            hashed_password=hash_password("password123"),
            full_name="Marcus Vance",
            role="employer",
            organization="Nexus Financial SaaS"
        )
        db.add_all([demo_uni_user, demo_student_user, demo_employer_user])
        db.commit()

        # Seed initial curriculum for the university user
        demo_curriculum = models.Curriculum(
            user_id=demo_uni_user.id,
            title="B.Tech Computer Science & Engineering Curriculum",
            institution="Global Institute of Technology",
            department="Computer Science & Engineering",
            academic_year="2026-2027",
            filename="CSE_Curriculum_2026.pdf",
            pages_processed=14,
            courses_count=6,
            skills_detected_count=7,
            raw_extracted_skills=["Python", "Java", "C++", "SQL", "JavaScript", "HTML5 & CSS3", "Problem Solving"],
            confirmed_skills=["Python", "Java", "C++", "SQL", "JavaScript", "HTML5 & CSS3", "Problem Solving", "Git"],
            courses_detail=[
                {"name": "CS101 Programming Fundamentals (Python)", "skills": ["Python", "Problem Solving"]},
                {"name": "CS201 Data Structures & Algorithms (C++)", "skills": ["C++", "Problem Solving"]},
                {"name": "CS301 Database Management Systems", "skills": ["SQL"]},
                {"name": "CS302 Web Technologies", "skills": ["JavaScript", "HTML5 & CSS3"]},
                {"name": "CS401 Object-Oriented Software Engineering", "skills": ["Java", "Git"]}
            ]
        )
        db.add(demo_curriculum)

        # Seed initial student profile
        demo_student_profile = models.StudentProfile(
            user_id=demo_student_user.id,
            resume_filename="Alex_Mercer_Resume_2026.pdf",
            extracted_skills=["Python", "SQL", "JavaScript", "Git", "Communication"],
            confirmed_skills=["Python", "SQL", "JavaScript", "Git", "Communication", "FastAPI"],
            target_role="Backend Developer",
            completed_projects=["Task Manager REST API with FastAPI & SQL"]
        )
        db.add(demo_student_profile)

        # Seed demo job postings
        for job_data in DEMO_JOBS:
            job = models.JobPosting(**job_data)
            db.add(job)

        # Seed sample employer requirement
        demo_req = models.EmployerRequirement(
            user_id=demo_employer_user.id,
            company="Nexus Financial SaaS",
            role="Backend Developer",
            required_skills=["Python", "SQL", "REST APIs", "Docker"],
            recommended_skills=["FastAPI", "AWS", "Git"]
        )
        db.add(demo_req)

        # Seed sample employer feedback
        demo_feedback = models.EmployerFeedback(
            user_id=demo_employer_user.id,
            company="Nexus Financial SaaS",
            difficult_skills=["Docker", "AWS", "Kubernetes"],
            emerging_skills=["LLMs", "FastAPI", "CI/CD"],
            missing_skills=["Docker containerization in production", "REST API security standards"],
            target_technologies=["FastAPI", "Docker", "AWS Cloud", "PyTorch"],
            notes="Graduates have strong theory in OOP and basic SQL, but lack practical experience with Docker containerization, REST API design, and cloud deployments."
        )
        db.add(demo_feedback)

        # Seed default university recommendations based on curriculum gaps
        reco1 = models.Recommendation(
            target_type="university",
            title="Integrate Production Containerization (Docker)",
            category="Curriculum Update",
            description="High industry demand (70% of backend & DevOps roles require Docker), while current curriculum lacks containerization modules.",
            suggested_module="Containerization Fundamentals & Docker Composition",
            suggested_project="Containerized Multi-Service FastAPI Application",
            suggested_assessment="Build, test, and package a REST API using Docker containers.",
            gap_skill="Docker",
            priority=1,
            status="active"
        )
        reco2 = models.Recommendation(
            target_type="university",
            title="Add Cloud Computing Fundamentals & AWS Lab",
            category="New Course / Lab Module",
            description="Cloud deployment skills are missing from the core curriculum despite appearing in 60% of regional software engineering job posts.",
            suggested_module="Cloud Architecture & AWS Services (EC2, S3, IAM)",
            suggested_project="Deploying Scalable Web Applications to AWS",
            suggested_assessment="Deploy a secure microservice on AWS free tier.",
            gap_skill="AWS",
            priority=1,
            status="active"
        )
        reco3 = models.Recommendation(
            target_type="university",
            title="Introduce Modern REST API Design Standards",
            category="Course Revision",
            description="Expand CS302 Web Technologies to emphasize REST API design patterns, OpenAPI specs, and authentication tokens.",
            suggested_module="RESTful Architecture & JWT Authentication",
            suggested_project="Production REST API with OpenAPI Documentation",
            suggested_assessment="Design and document compliant REST endpoints.",
            gap_skill="REST APIs",
            priority=2,
            status="active"
        )
        db.add_all([reco1, reco2, reco3])
        db.commit()
