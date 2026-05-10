from openai import OpenAI

def interview_agent(user_input, history, api_key, resume_text, job_description, round_number=1, user_name=None):
    client = OpenAI(api_key=api_key)

    # Stop interview if user types "stop"
    if user_input and user_input.lower().strip() in ["stop", "quit", "end interview"]:
        history.append({"role": "assistant", "content": "🛑 Interview stopped. Thank you!"})
        return history, history

    # Build system prompt with resume + JD context
    system_prompt = f"""
You are a professional interviewer.
- Conduct a structured interview in 3 rounds.
- Round 1: Behavioral (intro).
- Round 2: Technical (based on resume + job description).
- Round 3: HR/soft skills.
- Ask exactly ONE question at a time.
- After each answer, give short constructive feedback.
- After Round 3, provide a final summary (strengths, gaps, verdict).

Resume:
{resume_text}

Job Description:
{job_description}
"""

    messages = [{"role": "system", "content": system_prompt}] + history

    if user_input:
        messages.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages
    )

    answer = response.choices[0].message.content

    # Update history
    if user_input:
        history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": answer})

    return history, history


def begin_interview(api_key, resume_text, job_description):
    if not api_key:
        return [], "⚠️ Please enter your OpenAI API key."

    client = OpenAI(api_key=api_key)

    system_prompt = f"""
You are a professional interviewer.
Start the interview with a greeting and ONE behavioral question:
- Ask the candidate to introduce themselves.
- Capture their name for later rounds.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "system", "content": system_prompt}]
    )

    first_question = response.choices[0].message.content
    history = [{"role": "assistant", "content": first_question}]
    return history, "✅ Interview started. Please answer the first question below."


def stop_interview():
    """Helper to stop interview via button in Gradio UI"""
    return [], [], "🛑 Interview stopped. Restart to begin again."
