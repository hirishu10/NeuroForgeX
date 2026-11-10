# Part One Taking the Job Description Details from the Company Description
# Part Two Make the Schema to validate the JSON data from the Resume
# Part Three Make the Readable System to retrieve te data as per the Schema defined.
# Part Four Make the Score system to find out that the resume is oerfect for apply.

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel

load_dotenv()

# Api Keys
groq_api_key = os.getenv("GROQ_API_KEY")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_uri = os.getenv("QDRANT_API_KEY_URI")

# Model & Schema
model = "openai/gpt-oss-120b"
response_format = {"type": "json_object"}

# This is example of job description which will LLM receive to do the operation further.
job_description = f"""
We are looking for an experienced Full Stack Software Engineer with 3+ years of hands-on experience in developing scalable and high-performance web applications using the React.js and Node.js ecosystems.

The ideal candidate should have strong expertise in frontend development using React.js and Next.js, along with backend development experience using Node.js, Express.js, and NestJS. The candidate should be proficient in building reusable components, developing RESTful APIs, managing application state, implementing form validations, and integrating frontend applications with backend services.

Key Responsibilities
 - Develop, maintain, and enhance scalable web applications using React.js, Next.js, and Node.js.
 - Build reusable, responsive, and optimized frontend components.
 - Develop backend services and RESTful APIs using Node.js, Express.js, and NestJS.
 - Implement state management using Redux and Redux Toolkit.
 - Handle complex forms and validations using React Hook Form and Yup.
 - Integrate REST APIs using Axios and Fetch API.
 - Work with databases such as MongoDB, PostgreSQL, or MySQL.
 - Implement authentication and authorization using JWT and role-based access control.
 - Write clean, reusable, maintainable, and well-structured code.
 - Identify and resolve application bugs, performance issues, and production-related problems.
 - Collaborate with UI/UX designers, QA engineers, and backend developers.
 - Participate in code reviews, sprint planning, and Agile development processes.
 - Understand business requirements and translate them into technical solutions.

Required Technical Skills
 - Strong proficiency in JavaScript (ES6+) and TypeScript.
 - Hands-on experience with React.js and Next.js.
 - Strong backend development experience with Node.js.
 - Experience with Express.js and/or NestJS.
 - Good understanding of Redux, Redux Toolkit, and Context API.
 - Experience with React Hook Form and Yup for form management and validation.
 - Strong knowledge of RESTful API development and integration.
 - Experience with Axios, Fetch API, and asynchronous programming.
 - Understanding of HTML5, CSS3, responsive design, and modern UI frameworks.
 - Knowledge of MongoDB, PostgreSQL, or MySQL.
 - Experience with Git, GitHub, GitLab, or Bitbucket.
 - Familiarity with Postman, Swagger, and API testing.

Good to Have
 - Experience with Docker and containerization.
 - Basic knowledge of AWS or other cloud platforms.
 - Familiarity with Jest and React Testing Library.
 - Understanding of CI/CD pipelines.
 - Knowledge of Microservices architecture.
 - Experience with Agile/Scrum methodologies.

Experience & Qualifications
 - 3+ years of professional experience in software development.
 - Proven experience in developing frontend and backend applications.
 - Strong understanding of software development life cycle (SDLC).
 - Good problem-solving and debugging skills.
 - Ability to work independently as well as collaboratively within a team.
 - Strong communication and analytical skills.

Preferred Candidate: Developers with practical experience in service-based or product-based software development companies and exposure to real-world client projects.
"""


# Creating the Job Description Class to retreieve the exact data from the LLM.
class JobDescriptionSystem(BaseModel):
    role: str
    required_skill: list[str]
    prefered_skill: list[str]
    minimum_experience: float | None
    educational_requirements: list[str]
    responsibilities: list[str]


# Extracting the schema from the
job_description_schema = JobDescriptionSystem.model_json_schema()


# This is a system prompt will be worked to extract the required information from the description provided.
system_prompt = f"""
You are an expert HR assistant.

Your job is to analyze job description and extract
structured information from them.

Return ONLY valid JSON matching this schema:

{job_description_schema}
IMPORTANT:
Do NOT return the schema itself.
Do NOT return fields like "properties", "title" or "type".
Fill the schema with actual information extracted from the job description.

If minimum experience is not mentioned, return null.
If information for a list is missing, return an empty list.
Do not invent information.
"""

user_prompt = f"""
Analyze the following job description:
{job_description}
"""

system_message = {"role": "system", "content": system_prompt}

user_message = {"role": "user", "content": user_prompt}

messages = [system_message, user_message]
#
#
if not groq_api_key:
    raise ValueError("Groq API Key is missing")

client = Groq(api_key=groq_api_key)

response = client.chat.completions.create(
    model=model, messages=messages, response_format=response_format
)

answer = response.choices[0].message.content

print(f"Anwer: {answer}")
#########################

raw_json = answer
job_data = json.loads(raw_json)

# Getting the Job Description JSON data as per the module.
job = JobDescriptionSystem(**job_data)


class MatchResult(BaseModel):
    score: float
    details: dict


class Experience(BaseModel):
    company: str | None = None
    role: str | None = None
    duration: str | None = None
    description: str | None = None
    skill_used: list[str] = []


class Resume(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None

    total_experience_years: float | None = None

    skills: list[str] = []
    experiences: list[Experience] = []
    educations: list[str] = []
    projects: list[str] = []
    certifications: list[str] = []


resume_schema = Resume.model_json_schema()


# Some helpful functions
def final_score(job, resume):
    match_schema = MatchResult.model_json_schema()
    prompt = f"""
    You are and HR recruiter.
    
    Compare the candidate's resume with the job description.
    
    JOB Description:
    {job.model_dump_json(indent=2)}
    
    CANDIDATE RESUME:
    {resume.model_dump_json(indent=2)}
    Return JSON matching this schema:
    
    {match_schema}
    
    Give Me:
    
    1. Candidate name
    2. Matching skills
    3. Missing important skills
    4. Whether experience requirement  is met
    5. Overall match percentage from 0 to 100
    6. A short final verdict
    
    Keep the response concise and easy to read.
    """
    messages = [{"role": "user", "content": prompt}]

    response_type = {"type": "json_object"}
    response = client.chat.completions.create(
        model=model, messages=messages, response_format=response_type
    )
    data = json.loads(response.choices[0].message.content)
    print(f"Score Data: {data}")
    return MatchResult(**data)


def parse_resume(resume_text):
    system_prompt = f"""
    You are and expert resume parser.
    
    Extract information from the resume based on its meaning.
    not only based on exact section headings.
    
    Different resumes may use different headings.
    
    For example:
    - Experience
    - Professional Experience
    - Work History
    - Employment
    - Internships
    
    These may all contain relevant experience.
    
    Skills may also appear in the skills section, work experience,
    internships or projects.
    
    Return ONLY valid JSON matching this schema:
    
    {resume_schema}
    
    Important rules:
    
    1. Do not invent information.
    2. If a value is not available, return null.
    3. If a list has no information, return an empty list.
    4. include internships inside experiences.
    5. Extract skills mentioned across entire resume.
    """
    user_prompt = f"""
    Parse the following resume:
    
    {resume_text}
    """

    message_system = {"role": "system", "content": system_prompt}
    message_user = {"role": "user", "content": user_prompt}

    messages = [message_system, message_user]
    response_format = {"type": "json_object"}
    response = client.chat.completions.create(
        model=model, messages=messages, response_format=response_format
    )
    raw_json = response.choices[0].message.content
    data = json.loads(raw_json)
    resume = Resume(**data)
    print(f"Resume: {resume}")
    return resume


################################>

from pypdf import PdfReader
from docx import Document
import time


def read_pdf(file_path):
    reader = PdfReader(file_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    print(f"Read PDF: {text}")
    return text


def read_docx(file_path):
    document = Document(file_path)
    text = ""
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"

    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text += cell.text + "\n"

    print(f"Read DOCX: {text}")
    return text


def read_resume(file_path):
    print(f"Reading file: {file_path}")
    if file_path.suffix.lower() == ".pdf":
        return read_pdf(file_path)
    elif file_path.suffix.lower() == ".docx":
        return read_docx(file_path)
    else:
        return None


#######################>
resume_folder = Path("resumes")
all_results = []
for file_path in resume_folder.iterdir():
    if file_path.suffix.lower() not in [".pdf", ".docx"]:
        continue

    print("\nProcessing:", file_path.name)

    # Reading the resume and stroing as string
    resume_text = read_resume(file_path)

    if not resume_text or not resume_text.strip():
        print(f"Skipping empty resume: {file_path.name}")
        continue

    # Retrieving Resume from the resume text
    parsed_resume = parse_resume(resume_text)

    time.sleep(5)  # wait for sometime

    # Finalising the Score with resume and job.
    result = final_score(job, parsed_resume)

    time.sleep(5)  # wait for sometime

    print("Score:", result.score)

    all_results.append(
        {"name": parsed_resume.name, "score": result.score, "details": result.details}
    )

all_results.sort(key=lambda candidate: candidate["score"], reverse=True)

top_2 = all_results[:2]
worst_2 = all_results[-2:]

print("TOP CANDIDATES:")
for candidate in top_2:
    print(f"""
          Candidate Name:{candidate["name"]},
          Candidate Score: {candidate["score"]} %
          """)
    print(f"""Candidate Details: {candidate["details"]}""")

print("#########################################")

print("TOP CANDIDATES:")
for candidate in worst_2:
    print(f"""
          Candidate Name:{candidate["name"]},
          Candidate Score: {candidate["score"]} %
          """)
    print(f"""Candidate Details: {candidate["details"]}""")
