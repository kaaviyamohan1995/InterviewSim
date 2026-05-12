from openai import OpenAI

from Interviewer_Brain import interview_brain
from Prompt_Builder import build_dynamic_prompt


# ---------------------------
# BEGIN INTERVIEW
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
        "started": True,
        "ended": False
    }

    system_prompt = """
You are a senior technical interviewer.

Start with a short greeting and ask ONLY:
"Please introduce yourself."
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

    return state["history"], state, ""


# ---------------------------
# MAIN INTERVIEW LOOP
# ---------------------------
def interview_agent(
    user_input,
    state,
    api_key,
    resume_profile,
    job_description
):

    client = OpenAI(api_key=api_key)

    if not isinstance(state, dict):
        state = {}

    state.setdefault("round", 1)
    state.setdefault("step", 0)
    state.setdefault("history", [])
    state.setdefault("started", False)
    state.setdefault("ended", False)

    job_description = job_description or ""
    resume_profile = resume_profile or {"interview_concepts": {}}

    # ---------------------------
    # START IF NOT STARTED
    # ---------------------------
    if not state["started"]:
        return begin_interview(api_key, resume_profile, job_description)

    # ---------------------------
    # AUTO END CONDITION
    # ---------------------------
    MAX_ROUNDS = 3
    MAX_STEPS = 3

    if state["round"] > MAX_ROUNDS or state["step"] >= MAX_STEPS:
        state["ended"] = True

    if state["ended"]:
        return state["history"], state, "🏁 Interview Completed"

    # ---------------------------
    # BRAIN
    # ---------------------------
    brain_output = interview_brain(resume_profile, job_description, state)

    system_prompt = build_dynamic_prompt(
        resume_profile,
        job_description,
        brain_output,
        state
    )

    messages = [{"role": "system", "content": system_prompt}]
    messages += state["history"]

    if user_input:
        messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    output = response.choices[0].message.content

    if user_input:
        state["history"].append({"role": "user", "content": user_input})
        state["step"] += 1

    state["history"].append({"role": "assistant", "content": output})

    if state["step"] >= MAX_STEPS:
        state["round"] = min(state["round"] + 1, MAX_ROUNDS)
        state["step"] = 0

    return state["history"], state, ""


# ---------------------------
# STOP (MANUAL RESET)
# ---------------------------
def stop_interview(state):

    if not isinstance(state, dict):
        state = {}

    state["ended"] = True
    state["started"] = False

    return state, "🏁 Interview Ended"

def reset_interview():

    state = {
        "round": 1,
        "step": 0,
        "history": [],
        "topics_asked": [],
        "concepts_covered": [],
        "question_types": [],
        "started": False,
        "ended": False
    }

    return state, [], "🔄 Reset Complete"