# app.py
import dotenv
import gradio as gr
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .agents import build_agent_system

dotenv.load_dotenv()

agent = build_agent_system()
system_prompt = "You are a helpful medical assistant."


def interact_with_agent(message, history):
    msgs = [SystemMessage(system_prompt)]
    for role, content in history:
        if role == "user":
            msgs.append(HumanMessage(content=content))
        elif role == "assistant":
            msgs.append(AIMessage(content=content))

    if message:
        msgs.append(HumanMessage(content=message))

    state_input = {"messages": msgs}

    for msg_chunk, _ in agent.stream(state_input, stream_mode="messages"):
        content = getattr(msg_chunk, "content", None)
        if not content:
            continue

        # Case 1: doctors payload
        if isinstance(content, dict) and "doctors" in content:
            reply_blocks = []

            for doc in content["doctors"]:
                name = doc.get("name", "Unknown")
                spec = doc.get("specialty", "")
                embed_html = doc.get("embed_html")

                if embed_html:
                    # Render doctor name + specialty + Schedule link
                    block = f"**{name} — {spec}**\n\n{embed_html}"
                else:
                    err = doc.get("error", "No scheduling link available.")
                    block = f"**{name} — {spec}**\n\n_{err}_"

                reply_blocks.append(block)

            reply = "\n\n".join(reply_blocks)
            yield reply
            continue

        # Case 2: plain text
        if isinstance(content, str):
            yield content


demo = gr.ChatInterface(
    fn=interact_with_agent,
    chatbot=gr.Chatbot(
        type="messages",
        label="Assistant",
        avatar_images=(
            None,
            "https://em-content.zobj.net/source/twitter/141/parrot_1f99c.png",
        ),
    ),
    textbox=gr.Textbox(
        placeholder="Enter your message here...",
        container=False,
        scale=7,
    ),
    title="🏥 Medical Assistant (LangGraph + Gradio)",
    description="Ask about doctors, appointments, or scheduling. Integrated with Calendly.",
    theme="soft",
    examples=[
        ["Book a cardiologist for John Doe dob:1985-02-14 email:john.doe@example.com"],
        ["Find me a dermatologist"],
    ],
    cache_examples=False,
)


if __name__ == "__main__":
    demo.launch(share=True, debug=True)
