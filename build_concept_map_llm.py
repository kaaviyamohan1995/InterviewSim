from openai import OpenAI
import json
import re

def build_concept_map_llm(profile, api_key):

    client = OpenAI(api_key=api_key)

    prompt = f"""
You are an expert technical interviewer designer.

Your task:
Extract interview-relevant technical concepts from the candidate profile.

Return ONLY valid JSON.

RULES:
- Do NOT assume domain like RF or software.
- Derive concepts strictly from skills, tools, strengths.
- Expand each area into deep interview concepts.
- Focus on what interviewers actually test.

FORMAT:
{{
  "Area Name": [
    "concept1",
    "concept2"
  ]
}}

PROFILE:
Skills: {profile.get("skills", [])}
Tools: {profile.get("tools", [])}
Strengths: {profile.get("strengths", [])}
Domain: {profile.get("domain", "")}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content

    match = re.search(r"\{.*\}", content, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    return {}