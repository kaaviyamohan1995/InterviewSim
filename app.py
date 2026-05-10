import gradio as gr
from Interviewer_agent import interview_agent, begin_interview
from Resume_Parser import parse_resume


def start_interview(api_key):
    if not api_key:
        return "⚠️ Enter API key", gr.update(), gr.update()

    return "✅ Ready", gr.update(visible=False), gr.update(visible=True)


def stop_interview():
    return [], {"round": 1, "step": 0, "history": []}, "🛑 Stopped", gr.update(visible=True), gr.update(visible=False)


with gr.Blocks() as demo:

    gr.Markdown("# Interview Simulator")

    with gr.Column(visible=True) as start_page:
        api_key = gr.Textbox(type="password")
        resume = gr.File(type="filepath")
        jd = gr.Textbox()
        start_btn = gr.Button("Start")

        resume_profile_state = gr.State()

    with gr.Column(visible=False) as interview_page:
        chatbot = gr.Chatbot()
        msg = gr.Textbox()
        state = gr.State({"round": 1, "step": 0, "history": []})

        submit = gr.Button("Send")
        stop_btn = gr.Button("Stop")

    status = gr.Textbox()

    # switch
    start_btn.click(start_interview, [api_key], [status, start_page, interview_page])

    # resume parse
    resume.change(parse_resume, [resume, api_key], [status, resume_profile_state])

    # begin interview
    start_btn.click(begin_interview, [api_key, resume_profile_state, jd],
                    [chatbot, state, status])

    # submit answer
    submit.click(
        interview_agent,
        [msg, state, api_key, resume_profile_state, jd],
        [chatbot, state, msg]
    )

    # stop
    stop_btn.click(
        stop_interview,
        [],
        [chatbot, state, status, start_page, interview_page]
    )

demo.launch()