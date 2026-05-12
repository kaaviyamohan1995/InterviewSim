import gradio as gr

from Interviewer_agent import (
    interview_agent,
    begin_interview,
    stop_interview
)

from Resume_Parser import parse_resume


# ---------------------------
# START UI LOGIC
# ---------------------------
def start_interview(api_key, resume_profile):

    if not api_key:
        return (
            "⚠️ Enter API key",
            gr.update(visible=True),   # keep start page
            gr.update(visible=False)   # hide interview page
        )

    if not resume_profile:
        return (
            "⚠️ Upload resume first",
            gr.update(visible=True),
            gr.update(visible=False)
        )

    return (
        "✅ Ready",
        gr.update(visible=False),   # hide start page
        gr.update(visible=True)     # show interview page
    )


# ---------------------------
# UI
# ---------------------------
with gr.Blocks() as demo:

    gr.Markdown("# 🧠 AI Interview Simulator")

    # ---------------------------
    # START PAGE
    # ---------------------------
    with gr.Column(visible=True) as start_page:

        api_key = gr.Textbox(
            type="password",
            label="OpenAI API Key"
        )

        resume = gr.File(
            type="filepath",
            label="Upload Resume"
        )

        jd = gr.Textbox(
            label="Job Description (Optional)"
        )

        start_btn = gr.Button("Start Interview")

        resume_profile_state = gr.State()

        status = gr.Textbox(label="Status")


    # ---------------------------
    # INTERVIEW PAGE
    # ---------------------------
    with gr.Column(visible=False) as interview_page:

        chatbot = gr.Chatbot()

        msg = gr.Textbox(label="Your Answer")

        state = gr.State({
            "round": 1,
            "step": 0,
            "history": [],
            "topics_asked": [],
            "concepts_covered": [],
            "question_types": []
        })

        submit = gr.Button("Send")
        stop_btn = gr.Button("Stop Interview")


    # ---------------------------
    # RESUME PARSE
    # ---------------------------
    resume.change(
        parse_resume,
        [resume, api_key],
        [status, resume_profile_state]
    )


    # ---------------------------
    # START INTERVIEW
    # ---------------------------
    start_btn.click(
        start_interview,
        [api_key, resume_profile_state],
        [status, start_page, interview_page]
    )


    # ---------------------------
    # CHAT FLOW
    # ---------------------------
    submit.click(
        interview_agent,
        [msg, state, api_key, resume_profile_state, jd],
        [chatbot, state, msg]
    )


    # ---------------------------
    # STOP INTERVIEW
    # ---------------------------
    def stop_ui():
        state_reset, chat_reset, status = stop_interview()

        return (
            state_reset,
            chat_reset,
            status,
            gr.update(visible=True),   # show start page
            gr.update(visible=False)   # hide interview page
        )


    stop_btn.click(
        stop_ui,
        [],
        [state, chatbot, status, start_page, interview_page]
    ).then(
        lambda: "",
        None,
        msg
    )


demo.launch()