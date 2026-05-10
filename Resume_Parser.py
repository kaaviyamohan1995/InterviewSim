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

    profile = extract_profile_with_ai(text, api_key)

    summary = format_summary(text, profile)

    return summary, profile


# -----------------------------
# TEXT EXTRACTION
# -----------------------------
def extract_text(file_path):

    ext = os.path.splitext(file_path)[1].lower()

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
    return "\n".join(p.text for p in doc.paragraphs)


# -----------------------------
# AI EXTRACTION
# -----------------------------
def extract_profile_with_ai(text, api_key):

    client = OpenAI(api_key=api_key)

    prompt = f"""
Extract structured resume data.

Return ONLY valid JSON:

{{
  "name": "",
  "skills": [],
  "tools": [],
  "domain": "",
  "experience_years": "",
  "education": "",
  "strengths": []
}}

Resume:
{text}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    clean = extract_json(content)

    try:
        return json.loads(clean)
    except:
        return {
            "name": "",
            "skills": [],
            "tools": [],
            "domain": "",
            "experience_years": "",
            "education": "",
            "strengths": [],
            "error": "parse failed"
        }


# -----------------------------
# JSON CLEANER (IMPORTANT)
# -----------------------------
def extract_json(text):
    match = re.search(r"\{.*\}", text, re.DOTALL)
    return match.group(0) if match else text


# -----------------------------
# SUMMARY VIEW
# -----------------------------
def format_summary(text, profile):

    return f"""
## 📄 AI Resume Profile

### 👤 Name
{profile.get('name','')}

### 🛠 Skills
{', '.join(profile.get('skills', []))}

### 🔧 Tools
{', '.join(profile.get('tools', []))}

### 🎯 Domain
{profile.get('domain','')}

### 💼 Experience
{profile.get('experience_years','')}

### 💪 Strengths
{', '.join(profile.get('strengths', []))}

---

### 👀 Preview
{text[:800]}
"""