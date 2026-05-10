from openai import OpenAI
from Profile_Manager import format_profile_for_prompt


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

    # safety state
    if not isinstance(state, dict):
        state = {"round": 1, "step": 0}

    round_map = {
        1: "Behavioral (Introduction & background)",
        2: "Technical (based on resume + job description)",
        3: "HR / Soft skills"
    }

    current_round = state.get("round", 1)
    step = state.get("step", 0)

    profile_text = format_profile_for_prompt(resume_profile)

    system_prompt = f"""
You are a senior RFIC interviewer.

STRICT RULES:
- Ask ONLY ONE question
- No multiple questions
- No tutoring style

Round: {current_round} - {round_map[current_round]}
Step: {step}

PROFILE:
{profile_text}

JOB:
{job_description}
"""

    messages = [{"role": "system", "content": system_prompt}]

    if isinstance(state.get("history", []), list):
        messages += state["history"]

    if user_input:
        messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    answer = response.choices[0].message.content

    # init history if missing
    if "history" not in state:
        state["history"] = []

    if user_input:
        state["history"].append({"role": "user", "content": user_input})
        state["step"] = step + 1

    state["history"].append({"role": "assistant", "content": answer})

    # round transition
    if state["step"] >= 3 and state["round"] < 3:
        state["round"] += 1
        state["step"] = 0

    return state["history"], state, ""
    

# ---------------------------
# BEGIN INTERVIEW
# ---------------------------
def begin_interview(api_key, resume_profile, job_description):
    client = OpenAI(api_key=api_key)

    profile_text = format_profile_for_prompt(resume_profile)

    system_prompt = f"""
Start interview.

Ask ONLY ONE behavioral question.

PROFILE:
{profile_text}

JOB:
{job_description}
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt}]
    )

    first_question = response.choices[0].message.content

    state = {
        "round": 1,
        "step": 0,
        "history": [
            {"role": "assistant", "content": first_question}
        ]
    }

    return state["history"], state, "✅ Interview started"


# ---------------------------
# STOP
# ---------------------------
def stop_interview():
    return [], {"round": 1, "step": 0, "history": []}, "🛑 Stopped"