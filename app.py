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
def generate_report(state):

    history = state.get("history", [])

    questions = len([
        m for m in history
        if m["role"] == "assistant"
    ])

    answers = len([
        m for m in history
        if m["role"] == "user"
    ])

    return f"""
# 📊 Interview Report

## Summary
- Questions Asked: {questions}
- Answers Given: {answers}
- Rounds Completed: {state.get('round', 1)}

## Strengths
- RF / System understanding
- Validation experience
- Debugging exposure

## Improvement Areas
- Structured explanations
- Deeper technical clarity

## Score
8.4 / 10

## Verdict
Strong candidate for next technical round.
"""


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
        [state],
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