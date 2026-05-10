"""
Central profile manager for Interview Simulator
Handles resume profile normalization and formatting for interview engine
"""


def normalize_profile(raw_profile):
    """
    Ensures safe structure for interview usage
    """

    if not isinstance(raw_profile, dict):
        raw_profile = {}

    return {
        "skills": raw_profile.get("skills", []) or [],
        "tools": raw_profile.get("tools", []) or [],
        "domain": raw_profile.get("domain", "") or "",
        "experience_years": raw_profile.get("experience_years", "") or "",
        "strengths": raw_profile.get("strengths", []) or []
    }


def format_profile_for_prompt(profile):
    """
    Converts structured profile → clean LLM prompt format
    """

    if not profile:
        profile = {}

    return f"""
Skills: {', '.join(profile.get('skills', []))}
Tools: {', '.join(profile.get('tools', []))}
Domain: {profile.get('domain', '')}
Experience: {profile.get('experience_years', '')}
Strengths: {', '.join(profile.get('strengths', []))}
"""