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
    step = state.get("step", 0)

    topic = brain_output["topic"]
    subtopic = brain_output["subtopic"]
    question_type = brain_output["question_type"]
    difficulty = brain_output["difficulty"]

    asked_topics = state.get("topics_asked", [])

    # ---------------------------
    # FIRST QUESTION FIX
    # ---------------------------
    if current_round == 1 and step == 0:

        return f"""
You are a senior technical interviewer.

IMPORTANT:
This is the START of the interview.

TASK:
1. Greet the candidate briefly
2. Ask them to introduce themselves

STRICT RULES:
- Only ONE message
- No technical questions yet
- No multiple questions

Candidate Profile:
Skills: {', '.join(profile.get('skills', []))}
Tools: {', '.join(profile.get('tools', []))}

Job Description:
{job_description}

Generate the opening interview message.
"""

    # ---------------------------
    # NORMAL FLOW
    # ---------------------------
    return f"""
You are an expert technical interviewer.

You adapt dynamically based on:
- Candidate resume
- Job description
- Interview progress

INTERVIEW CONTEXT
-----------------
Round:
{round_map.get(current_round)}

Step:
{step}

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
Selected Topic:
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
2. No tutoring or explanations.
3. No multiple questions in one response.
4. Never repeat earlier topics unless necessary for depth.
5. Keep tone professional like a real FAANG interviewer.
6. Adjust depth:
   - easy → fundamentals
   - medium → applied scenarios
   - hard → deep system reasoning
7. Avoid generic HR questions.
8. Use resume context naturally.
9. Prefer scenario-based technical questions.

Generate ONE interview question only.
"""