import gradio as gr
from Interviewer_agent import interview_agent, begin_interview

# Helper to stop interview
def stop_interview():
    return [], [], "🛑 Interview stopped. Restart to begin again."

def start_interview(api_key):
    if not api_key:
        return gr.update(visible=False), [], "⚠️ Please enter your OpenAI API key."
    return gr.update(visible=True), [], "✅ Key accepted. Paste resume & JD, then click Start Interview."

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎉 Interview Simulator Agent")

    api_key = gr.Textbox(label="🔑 API Key", type="password")
    resume_box = gr.Textbox(label="📄 Resume", lines=6)
    jd_box = gr.Textbox(label="📝 Job Description", lines=6)
    status = gr.Label()
    start_btn = gr.Button("🚀 Start Interview")

    with gr.Group(visible=False) as interview_ui:
        chatbot = gr.Chatbot(label="💬 Interview Chat", value=[])
        msg = gr.Textbox(label="✍️ Your Answer")
        state = gr.State([])
        submit = gr.Button("Submit Answer")
        stop_btn = gr.Button("🛑 Stop Interview", variant="secondary")

        # Submit answer → continue interview
        submit.click(
            interview_agent,
            [msg, state, api_key, resume_box, jd_box],
            [chatbot, state]
        )

        # Stop interview → clear chat and reset
        stop_btn.click(
            stop_interview,
            [],
            [chatbot, state, status]
        )

    # First click: reveal UI
    start_btn.click(
        start_interview,
        [api_key],
        [interview_ui, chatbot, status]
    )

    # Second click: actually start interview with first question
    start_btn.click(
        begin_interview,
        [api_key, resume_box, jd_box],
        [chatbot, status]
    )

demo.launch()
