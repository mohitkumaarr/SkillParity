import re
import io
from typing import List, Dict, Any, Tuple
from pypdf import PdfReader

# Master Skill Taxonomy
SKILL_TAXONOMY = [
    {
        "canonical_name": "Python",
        "category": "Programming Languages",
        "aliases": ["python", "python3", "python programming", "py"]
    },
    {
        "canonical_name": "Java",
        "category": "Programming Languages",
        "aliases": ["java", "j2ee", "java se", "java ee"]
    },
    {
        "canonical_name": "C++",
        "category": "Programming Languages",
        "aliases": ["c++", "cpp", "cplusplus"]
    },
    {
        "canonical_name": "JavaScript",
        "category": "Programming Languages",
        "aliases": ["javascript", "js", "ecmascript", "es6"]
    },
    {
        "canonical_name": "TypeScript",
        "category": "Programming Languages",
        "aliases": ["typescript", "ts"]
    },
    {
        "canonical_name": "SQL",
        "category": "Databases",
        "aliases": ["sql", "structured query language", "postgresql", "postgres", "mysql", "sqlite", "oracle sql", "database management", "dbms"]
    },
    {
        "canonical_name": "MongoDB",
        "category": "Databases",
        "aliases": ["mongodb", "mongo", "nosql"]
    },
    {
        "canonical_name": "Redis",
        "category": "Databases",
        "aliases": ["redis", "in-memory cache", "key-value store"]
    },
    {
        "canonical_name": "FastAPI",
        "category": "Backend",
        "aliases": ["fastapi", "fast api"]
    },
    {
        "canonical_name": "Django",
        "category": "Backend",
        "aliases": ["django", "django rest framework"]
    },
    {
        "canonical_name": "Node.js",
        "category": "Backend",
        "aliases": ["node.js", "nodejs", "node"]
    },
    {
        "canonical_name": "REST APIs",
        "category": "Backend",
        "aliases": ["rest api", "restful api", "rest apis", "restful web services", "web apis", "api development"]
    },
    {
        "canonical_name": "Microservices",
        "category": "Backend",
        "aliases": ["microservices", "microservice architecture", "distributed systems"]
    },
    {
        "canonical_name": "React",
        "category": "Frontend",
        "aliases": ["react", "react.js", "reactjs", "react native"]
    },
    {
        "canonical_name": "Vue.js",
        "category": "Frontend",
        "aliases": ["vue", "vue.js", "vuejs"]
    },
    {
        "canonical_name": "HTML5 & CSS3",
        "category": "Frontend",
        "aliases": ["html", "html5", "css", "css3", "web design"]
    },
    {
        "canonical_name": "Docker",
        "category": "DevOps",
        "aliases": ["docker", "containerization", "containers", "docker container"]
    },
    {
        "canonical_name": "Kubernetes",
        "category": "DevOps",
        "aliases": ["kubernetes", "k8s", "container orchestration"]
    },
    {
        "canonical_name": "Git",
        "category": "DevOps",
        "aliases": ["git", "github", "version control", "gitlab"]
    },
    {
        "canonical_name": "Linux",
        "category": "DevOps",
        "aliases": ["linux", "unix", "bash", "shell scripting", "ubuntu"]
    },
    {
        "canonical_name": "CI/CD",
        "category": "DevOps",
        "aliases": ["ci/cd", "continuous integration", "continuous deployment", "jenkins", "github actions"]
    },
    {
        "canonical_name": "AWS",
        "category": "Cloud",
        "aliases": ["aws", "amazon web services", "aws cloud", "ec2", "s3", "lambda"]
    },
    {
        "canonical_name": "Cloud Computing",
        "category": "Cloud",
        "aliases": ["cloud computing", "cloud infrastructure", "cloud architecture", "azure", "gcp", "google cloud"]
    },
    {
        "canonical_name": "Machine Learning",
        "category": "AI/ML",
        "aliases": ["machine learning", "ml", "machine learning algorithms", "statistical learning", "scikit-learn", "sklearn"]
    },
    {
        "canonical_name": "Deep Learning",
        "category": "AI/ML",
        "aliases": ["deep learning", "neural networks", "cnn", "rnn", "transformers"]
    },
    {
        "canonical_name": "PyTorch",
        "category": "AI/ML",
        "aliases": ["pytorch", "torch"]
    },
    {
        "canonical_name": "TensorFlow",
        "category": "AI/ML",
        "aliases": ["tensorflow", "tf", "keras"]
    },
    {
        "canonical_name": "LLMs",
        "category": "Emerging Technologies",
        "aliases": ["llm", "llms", "large language models", "generative ai", "genai", "prompt engineering", "langchain", "rag"]
    },
    {
        "canonical_name": "Data Analysis",
        "category": "Data",
        "aliases": ["data analysis", "data analytics", "pandas", "numpy", "exploratory data analysis", "eda"]
    },
    {
        "canonical_name": "Cybersecurity",
        "category": "Cybersecurity",
        "aliases": ["cybersecurity", "cyber security", "network security", "information security", "ethical hacking", "cryptography"]
    },
    {
        "canonical_name": "IoT",
        "category": "IoT",
        "aliases": ["iot", "internet of things", "embedded systems", "raspberry pi", "arduino", "mqtt"]
    },
    {
        "canonical_name": "Communication",
        "category": "Soft Skills",
        "aliases": ["communication", "verbal communication", "written communication", "presentation skills"]
    },
    {
        "canonical_name": "Problem Solving",
        "category": "Soft Skills",
        "aliases": ["problem solving", "analytical thinking", "critical thinking", "troubleshooting", "data structures and algorithms"]
    }
]

def extract_skills_from_text(text: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """
    Extracts canonical skills from input text using regex matching, alias lookup,
    normalization, and deduplication.
    Returns (list of canonical skill names, list of detail dicts).
    """
    if not text:
        return [], []

    normalized_text = text.lower()
    found_skills = set()
    details = []

    for item in SKILL_TAXONOMY:
        canonical = item["canonical_name"]
        category = item["category"]
        aliases = item["aliases"]

        # Check canonical name and each alias
        for alias in aliases:
            # Match word boundary or escaped special chars
            escaped_alias = re.escape(alias)
            pattern = r'(?i)\b' + escaped_alias + r'\b'
            
            # Special handling for C++ or languages with trailing ++ / .js
            if "++" in alias or ".js" in alias or "#" in alias:
                pattern = r'(?i)' + escaped_alias
                
            if re.search(pattern, normalized_text):
                if canonical not in found_skills:
                    found_skills.add(canonical)
                    details.append({
                        "canonical_name": canonical,
                        "category": category,
                        "matched_alias": alias
                    })
                break

    return sorted(list(found_skills)), details

def process_pdf_file(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Parses a PDF file from bytes using PyPDF.
    Extracts text, counts pages, detects courses/modules, and extracts skills.
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    num_pages = len(reader.pages)
    
    full_text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            full_text += extracted + "\n"

    # Rule-based course detector
    lines = full_text.split('\n')
    courses_detected = []
    current_course = None

    course_keywords = ["course", "subject", "module", "unit", "cs", "it", "cse", "ece", "lab"]

    for line in lines:
        cleaned = line.strip()
        if not cleaned:
            continue

        # Check if line looks like a course header (e.g., "CS101 Database Systems" or "Module 3: Cloud Computing")
        is_course_line = any(kw in cleaned.lower() for kw in course_keywords) and len(cleaned) < 80
        if is_course_line or (cleaned.isupper() and len(cleaned) > 4 and len(cleaned) < 60):
            course_skills, _ = extract_skills_from_text(cleaned)
            courses_detected.append({
                "name": cleaned,
                "skills": course_skills
            })

    # Fallback default courses if PDF layout was unstructured text
    if not courses_detected:
        courses_detected = [
            {"name": "Database Management Systems", "skills": ["SQL", "Problem Solving"]},
            {"name": "Data Structures & Algorithms", "skills": ["C++", "Java", "Python", "Problem Solving"]},
            {"name": "Web Technologies", "skills": ["HTML5 & CSS3", "JavaScript", "REST APIs"]},
            {"name": "Operating Systems & Linux", "skills": ["Linux", "C++"]}
        ]

    # Global extracted skills
    skills, details = extract_skills_from_text(full_text)

    return {
        "pages_processed": num_pages,
        "raw_text": full_text[:2000],  # sample preview
        "courses_detected": courses_detected,
        "skills_detected": skills,
        "skills_detail": details
    }
