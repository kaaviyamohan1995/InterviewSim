def build_dynamic_prompt(
    profile,
    job_description,
    brain_output,
    state
):

    round_map = {
        1: "Introduction & Resume Deep Dive",
        2: "Technical Evaluation",
        3: "Advanced Problem Solving"
    }

    current_round = state.get("round", 1)

    topic = brain_output["topic"]
    subtopic = brain_output["subtopic"]
    question_type = brain_output["question_type"]
    difficulty = brain_output["difficulty"]

    asked_topics = state.get(
        "topics_asked",
        []
    )

    return f"""
You are an expert technical interviewer.

You dynamically adapt your expertise
to the candidate resume and job role.

INTERVIEW CONTEXT
-----------------
Round:
{round_map.get(current_round)}

Difficulty:
{difficulty}

Candidate Profile
-----------------
Skills:
{', '.join(profile.get('skills', []))}

Tools:
{', '.join(profile.get('tools', []))}

Strengths:
{', '.join(profile.get('strengths', []))}

Domain:
{profile.get('domain', '')}

Job Description
----------------
{job_description}

INTERVIEW STRATEGY
-------------------
Topic:
{topic}

Subtopic:
{subtopic}

Question Type:
{question_type}

Already Covered Topics:
{', '.join(asked_topics)}

STRICT RULES
-------------
1. Ask ONLY ONE question.
2. No tutoring.
3. No multiple questions.
4. Avoid repeating earlier topics.
5. Question must feel realistic and professional.
6. Adapt depth to difficulty:
   easy = fundamentals
   medium = applied thinking
   hard = deep technical reasoning
7. Avoid generic HR questions.
8. Use resume context naturally.

Generate ONE interview question.
"""