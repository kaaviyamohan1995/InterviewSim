from openai import OpenAI

from Interviewer_Brain import interview_brain
from Prompt_Builder import build_dynamic_prompt


# ---------------------------
# INTERVIEW AGENT
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
    # STATE INIT
    # ---------------------------
    if not isinstance(state, dict):
        state = {}

    state.setdefault("round", 1)
    state.setdefault("step", 0)
    state.setdefault("history", [])

    state.setdefault("topics_asked", [])
    state.setdefault("concepts_covered", [])
    state.setdefault("question_types", [])

    # ---------------------------
    # SAFETY RESUME PROFILE
    # ---------------------------
    if not resume_profile:
        resume_profile = {
            "interview_concepts": {}
        }

    # ---------------------------
    # INTERVIEW BRAIN
    # ---------------------------
    brain_output = interview_brain(
        resume_profile,
        job_description or "",
        state
    )

    # ---------------------------
    # PROMPT BUILDING
    # ---------------------------
    system_prompt = build_dynamic_prompt(
        resume_profile,
        job_description or "",
        brain_output,
        state
    )

    # ---------------------------
    # MESSAGE HISTORY
    # ---------------------------
    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages += state["history"]

    if user_input:
        messages.append({
            "role": "user",
            "content": user_input
        })

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
    if state["step"] >= 3 and state["round"] < 3:
        state["round"] += 1
        state["step"] = 0

    return state["history"], state, ""


# ---------------------------
# BEGIN INTERVIEW
# ---------------------------
def begin_interview(
    api_key,
    resume_profile,
    job_description
):

    client = OpenAI(api_key=api_key)

    # ---------------------------
    # INITIAL STATE
    # ---------------------------
    state = {
        "round": 1,
        "step": 0,
        "history": [],

        "topics_asked": [],
        "concepts_covered": [],
        "question_types": []
    }

    # ---------------------------
    # SAFETY PROFILE
    # ---------------------------
    if not resume_profile:
        resume_profile = {
            "interview_concepts": {}
        }

    # ---------------------------
    # BRAIN INIT
    # ---------------------------
    brain_output = interview_brain(
        resume_profile,
        job_description or "",
        state
    )

    # ---------------------------
    # PROMPT
    # ---------------------------
    system_prompt = build_dynamic_prompt(
        resume_profile,
        job_description or "",
        brain_output,
        state
    )

    # ---------------------------
    # FIRST QUESTION
    # ---------------------------
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            }
        ]
    )

    first_question = response.choices[0].message.content

    state["history"].append({
        "role": "assistant",
        "content": first_question
    })

    return state["history"], state, "✅ Interview started"


# ---------------------------
# STOP
# ---------------------------
def stop_interview():

    return (
        [],
        {
            "round": 1,
            "step": 0,
            "history": [],
            "topics_asked": [],
            "concepts_covered": [],
            "question_types": []
        },
        "🛑 Stopped"
    )