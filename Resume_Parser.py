import fitz
from docx import Document
import os
import json
import re
from openai import OpenAI


# -----------------------------
# MAIN FUNCTION (USED BY APP)
# -----------------------------
def parse_resume(file_path, api_key):

    if not file_path:
        return "Please upload a resume.", {}

    text = extract_text(file_path)

    profile = extract_profile_with_ai(
        text,
        api_key
    )

    summary = format_summary(
        text,
        profile
    )

    return summary, profile


# -----------------------------
# TEXT EXTRACTION
# -----------------------------
def extract_text(file_path):

    ext = os.path.splitext(
        file_path
    )[1].lower()

    if ext == ".pdf":
        return extract_pdf(file_path)

    elif ext == ".docx":
        return extract_docx(file_path)

    return ""


def extract_pdf(file_path):

    text = ""

    doc = fitz.open(file_path)

    for page in doc:
        text += page.get_text()

    return text


def extract_docx(file_path):

    doc = Document(file_path)

    return "\n".join(
        p.text for p in doc.paragraphs
    )


# -----------------------------
# AI EXTRACTION
# -----------------------------
def extract_profile_with_ai(
    text,
    api_key
):

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an expert resume analyzer
and technical interviewer designer.

Your task:
Extract structured resume data
for an interview simulator.

IMPORTANT RULES:
- Do NOT assume any domain.
- Infer dynamically from resume.
- Extract interview-relevant concepts.
- Concepts must represent
what interviewers usually assess.

Return ONLY valid JSON.

FORMAT:

{{
    "name": "",

    "skills": [],

    "tools": [],

    "domain": "",

    "experience_years": "",

    "education": "",

    "strengths": [],

    "interview_concepts": {{
        "topic_name": [
            "concept_1",
            "concept_2"
        ]
    }}
}}

GOOD EXAMPLE:

{{
    "name": "John",

    "skills": [
        "Python",
        "Machine Learning"
    ],

    "tools": [
        "TensorFlow"
    ],

    "domain": "AI Engineering",

    "experience_years": "5",

    "strengths": [
        "Model Development"
    ],

    "interview_concepts": {{
        "Machine Learning": [
            "overfitting",
            "model evaluation",
            "feature engineering",
            "hyperparameter tuning"
        ],

        "Python Engineering": [
            "debugging",
            "optimization",
            "API design"
        ]
    }}
}}

Resume:

{text}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    clean = extract_json(content)

    try:
        return json.loads(clean)

    except Exception as e:

        print(
            "Resume parse failed:",
            e
        )

        return {
            "name": "",

            "skills": [],

            "tools": [],

            "domain": "",

            "experience_years": "",

            "education": "",

            "strengths": [],

            "interview_concepts": {},

            "error": "parse failed"
        }


# -----------------------------
# JSON CLEANER
# -----------------------------
def extract_json(text):

    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )

    return (
        match.group(0)
        if match
        else text
    )


# -----------------------------
# SUMMARY VIEW
# -----------------------------
def format_summary(
    text,
    profile
):

    concepts = profile.get(
        "interview_concepts",
        {}
    )

    concept_text = ""

    for topic, subtopics in concepts.items():

        concept_text += (
            f"\n• {topic}: "
            f"{', '.join(subtopics)}"
        )

    return f"""
## 📄 AI Resume Profile

### 👤 Name
{profile.get('name', '')}

### 🛠 Skills
{', '.join(profile.get('skills', []))}

### 🔧 Tools
{', '.join(profile.get('tools', []))}

### 🎯 Domain
{profile.get('domain', '')}

### 💼 Experience
{profile.get('experience_years', '')}

### 💪 Strengths
{', '.join(profile.get('strengths', []))}

### 🧠 Interview Concepts
{concept_text}

---

### 👀 Resume Preview
{text[:800]}
"""