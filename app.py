import gradio as gr

from Interviewer_agent import (
    interview_agent,
    begin_interview,
    stop_interview,
    reset_interview
)

from Resume_Parser import parse_resume


# ---------------------------
# ANALYSIS FUNCTION
# ---------------------------
from openai import OpenAI


def generate_report(
    state,
    api_key,
    resume_profile,
    job_description
):

    if not api_key:
        return "❌ API Key missing"

    history = state.get("history", [])

    if not history:
        return "❌ No interview history found"

    client = OpenAI(api_key=api_key)

    # ---------------------------
    # BUILD CONVERSATION
    # ---------------------------
    conversation = ""

    for msg in history:

        role = msg["role"]

        if role == "assistant":
            role = "Interviewer"

        elif role == "user":
            role = "Candidate"

        conversation += (
            f"{role}: "
            f"{msg['content']}\n\n"
        )

    # ---------------------------
    # DYNAMIC ROLE CONTEXT
    # ---------------------------
    resume_context = str(resume_profile)

    jd_context = (
        job_description
        if job_description
        else "No job description provided"
    )

    # ---------------------------
    # DYNAMIC EVALUATION PROMPT
    # ---------------------------
    prompt = f"""
You are an expert hiring manager.

Your task is to evaluate a candidate's interview performance.

IMPORTANT:
- Infer the job domain dynamically using:
    1. Resume profile
    2. Job description
    3. Interview questions

- DO NOT assume semiconductor,
  software, AI, or any specific domain.

- Adapt evaluation categories
  according to the role.

Example:
If software role:
    - coding
    - system design
    - debugging

If RF/Validation role:
    - RF knowledge
    - silicon validation
    - debugging
    - automation

If AI/ML role:
    - ML fundamentals
    - modeling
    - problem solving

Evaluate ONLY based on
candidate responses.

Resume Profile:
{resume_context}

Job Description:
{jd_context}

Interview:
{conversation}

Provide output in markdown format:

# 📊 Interview Performance Analysis

## Role Detected
(Detected role)

## Overall Score
(X.X / 10)

## Category Scores
| Category | Score |
|-----------|-------|
| Skill | X |

## Strengths
- point
- point

## Improvement Areas
- point
- point

## Interview Summary
(summary)

## Final Verdict
(Hire / Hold / Reject)
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# ---------------------------
# START FLOW
# ---------------------------
def start_interview(
    api_key,
    resume_profile
):

    if not api_key:
        return (
            "⚠️ Enter API key",
            gr.update(),
            gr.update()
        )

    if not resume_profile:
        return (
            "⚠️ Upload Resume First",
            gr.update(),
            gr.update()
        )

    return (
        "✅ Ready",
        gr.update(visible=False),
        gr.update(visible=True)
    )


# ---------------------------
# SHOW ANALYSIS BUTTON
# ---------------------------
def post_process(chatbot, state):

    if state.get("ended"):
        return (
            chatbot,
            state,
            gr.update(visible=True)
        )

    return (
        chatbot,
        state,
        gr.update(visible=False)
    )


# ---------------------------
# STOP INTERVIEW
# ---------------------------
def stop_ui(state):

    state, status = stop_interview(state)

    return (
        state,
        status,
        gr.update(visible=True)
    )


# ---------------------------
# RESET UI
# ---------------------------
def reset_ui():

    state, chat, status = reset_interview()

    return (
        state,
        chat,
        status,
        gr.update(visible=True),   # start page
        gr.update(visible=False),  # interview page
        gr.update(visible=False)   # analysis btn
    )


# ---------------------------
# UI
# ---------------------------
with gr.Blocks() as demo:

    gr.Markdown("# 🧠 AI Interview Simulator")

    # -----------------------
    # START PAGE
    # -----------------------
    with gr.Column(visible=True) as start_page:

        api_key = gr.Textbox(
            type="password",
            label="API Key"
        )

        resume = gr.File(
            type="filepath",
            label="Resume"
        )

        jd = gr.Textbox(
            label="Job Description"
        )

        start_btn = gr.Button(
            "Start Interview"
        )

        begin_btn = gr.Button(
            "Begin Interview",
            visible=False
        )

        resume_state = gr.State()

        status = gr.Textbox()

    # -----------------------
    # INTERVIEW PAGE
    # -----------------------
    with gr.Column(
        visible=False
    ) as interview_page:

        chatbot = gr.Chatbot()

        msg = gr.Textbox(
            label="Your Answer"
        )

        state = gr.State({
            "round": 1,
            "step": 0,
            "history": [],
            "started": False,
            "ended": False
        })

        submit = gr.Button("Send")

        stop_btn = gr.Button(
            "🛑 Stop Interview"
        )

        reset_btn = gr.Button(
            "🔄 Reset"
        )

        analysis_btn = gr.Button(
            "📊 Performance Analysis",
            visible=False
        )

    # -----------------------
    # ANALYSIS PAGE
    # -----------------------
    with gr.Column(
        visible=False
    ) as analysis_page:

        report = gr.Markdown()

        back_btn = gr.Button(
            "⬅ Back To Start"
        )

    # -----------------------
    # RESUME PARSE
    # -----------------------
    resume.change(
        parse_resume,
        [resume, api_key],
        [status, resume_state]
    )

    # -----------------------
    # START FLOW
    # -----------------------
    start_btn.click(
        start_interview,
        [api_key, resume_state],
        [status, start_page, interview_page]
    ).then(
        lambda: gr.update(
            visible=True
        ),
        None,
        begin_btn
    )

    # -----------------------
    # BEGIN INTERVIEW
    # -----------------------
    begin_btn.click(
        begin_interview,
        [api_key, resume_state, jd],
        [chatbot, state, status]
    )

    # -----------------------
    # CHAT FLOW
    # -----------------------
    submit.click(
        interview_agent,
        [
            msg,
            state,
            api_key,
            resume_state,
            jd
        ],
        [
            chatbot,
            state,
            msg
        ]
    ).then(
        post_process,
        [chatbot, state],
        [
            chatbot,
            state,
            analysis_btn
        ]
    )

    # -----------------------
    # STOP INTERVIEW
    # -----------------------
    stop_btn.click(
        stop_ui,
        [state],
        [
            state,
            status,
            analysis_btn
        ]
    )

    # -----------------------
    # RESET
    # -----------------------
    reset_btn.click(
        reset_ui,
        [],
        [
            state,
            chatbot,
            status,
            start_page,
            interview_page,
            analysis_btn
        ]
    )

    # -----------------------
    # PERFORMANCE ANALYSIS
    # -----------------------
    analysis_btn.click(
    generate_report,
    [state, api_key, resume_state, jd],
    report
    ).then(
    lambda: (
        gr.update(visible=False),
        gr.update(visible=True)
    ),
    None,
    [
        interview_page,
        analysis_page
    ]
    )

    # -----------------------
    # BACK BUTTON
    # -----------------------
    back_btn.click(
        lambda: (
            gr.update(visible=True),
            gr.update(visible=False)
        ),
        None,
        [
            start_page,
            analysis_page
        ]
    )


demo.launch()