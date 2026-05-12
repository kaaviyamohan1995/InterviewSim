from openai import OpenAI

from Interviewer_Brain import interview_brain
from Prompt_Builder import build_dynamic_prompt


# ---------------------------
# INTERVIEW AGENT (MAIN LOOP)
# ---------------------------
def interview_agent(
    user_input,
    state,
    api_key,
    resume_profile,
    job_description
):

    client = OpenAI(api_key=api_key)

    # ---------------------------
    # SAFE STATE INIT
    # ---------------------------
    if not isinstance(state, dict):
        state = {}

    state.setdefault("round", 1)
    state.setdefault("step", 0)
    state.setdefault("history", [])
    state.setdefault("topics_asked", [])
    state.setdefault("concepts_covered", [])
    state.setdefault("question_types", [])
    state.setdefault("started", False)

    job_description = job_description or ""
    resume_profile = resume_profile or {"interview_concepts": {}}

    # ---------------------------
    # STOP SAFETY GUARD
    # ---------------------------
    if not state.get("started"):
        return begin_interview(api_key, resume_profile, job_description)

    # ---------------------------
    # INTERVIEW BRAIN
    # ---------------------------
    brain_output = interview_brain(
        resume_profile,
        job_description,
        state
    )

    # ---------------------------
    # DYNAMIC PROMPT
    # ---------------------------
    system_prompt = build_dynamic_prompt(
        resume_profile,
        job_description,
        brain_output,
        state
    )

    # ---------------------------
    # BUILD MESSAGES
    # ---------------------------
    messages = [{"role": "system", "content": system_prompt}]
    messages += state["history"]

    if user_input:
        messages.append({"role": "user", "content": user_input})

    # ---------------------------
    # GPT CALL
    # ---------------------------
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    output = response.choices[0].message.content

    # ---------------------------
    # UPDATE STATE
    # ---------------------------
    if user_input:
        state["history"].append({
            "role": "user",
            "content": user_input
        })
        state["step"] += 1

    state["history"].append({
        "role": "assistant",
        "content": output
    })

    # ---------------------------
    # ROUND TRANSITION
    # ---------------------------
    if state["step"] >= 3:
        state["round"] = min(state["round"] + 1, 3)
        state["step"] = 0

    return state["history"], state, ""


# ---------------------------
# BEGIN INTERVIEW (ONLY ONCE)
# ---------------------------
def begin_interview(api_key, resume_profile, job_description):

    client = OpenAI(api_key=api_key)

    state = {
        "round": 1,
        "step": 0,
        "history": [],
        "topics_asked": [],
        "concepts_covered": [],
        "question_types": [],
        "started": True
    }

    job_description = job_description or ""
    resume_profile = resume_profile or {"interview_concepts": {}}

    # ---------------------------
    # OPENING PROMPT (FIXED)
    # ---------------------------
    system_prompt = system_prompt = """
You are a senior technical interviewer.

TASK:
Start the interview with a short greeting and ask ONLY ONE question.

QUESTION RULE:
- The ONLY question should be: ask the candidate to introduce themselves
- Do NOT ask any additional technical or follow-up questions

OUTPUT FORMAT:
- Greeting + single introduction question in one response
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt}]
    )

    first_question = response.choices[0].message.content

    state["history"].append({
        "role": "assistant",
        "content": first_question
    })

    return state["history"], state, "✅ Interview started"


# ---------------------------
# STOP INTERVIEW (FULL RESET SAFE)
# ---------------------------
def stop_interview():

    state = {
        "round": 1,
        "step": 0,
        "history": [],
        "topics_asked": [],
        "concepts_covered": [],
        "question_types": [],
        "started": False
    }

    return state, [], "🛑 Stopped"