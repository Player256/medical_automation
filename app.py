# hey check out john doe dob:1985-2-14 email: john.doe@example.com
import gradio as gr
import dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .agents import build_agent_system

dotenv.load_dotenv()

agent = build_agent_system()
system_prompt = "You are a helpful medical assistant."


def interact_with_agent(message, history):
    msgs = [SystemMessage(system_prompt)]
    for m in history or []:
        if m["role"] == "user":
            msgs.append(HumanMessage(content=m["content"]))
        if m["role"] == "assistant":
            msgs.append(AIMessage(content=m["content"]))
    if message:
        msgs.append(HumanMessage(content=message))
        history.append({"role": "user", "content": message})

    state_input = {"messages": msgs}

    for msg_chunk, _ in agent.stream(state_input, stream_mode="messages"):
        content = getattr(msg_chunk, "content", None)
        if not content:
            continue

        if isinstance(content, dict) and "doctors" in content:
            history.append(
                {"role": "assistant", "content": "Here are available doctors:"}
            )
            for doc in content["doctors"]:
                doc_text = f"{doc['name']} — {doc['specialty']}\n"
                doc_text += f"[30 min]({doc['calendly_30_url']}) | [60 min]({doc['calendly_60_url']})"
                history.append({"role": "assistant", "content": doc_text})
            yield history
            continue

        if isinstance(content, str):
            history.append({"role": "assistant", "content": content})
            yield history


with gr.Blocks() as demo:
    gr.Markdown("# 🏥 Medical Assistant (LangGraph + Gradio)")
    chatbot = gr.Chatbot(
        type="messages",
        label="Assistant",
        avatar_images=(
            None,
            "https://em-content.zobj.net/source/twitter/141/parrot_1f99c.png",
        ),
    )
    input_box = gr.Textbox(
        placeholder="Enter your message here...",
        container=False,
        scale=7,
    )

    input_box.submit(interact_with_agent, [input_box, chatbot], [chatbot])

demo.launch(share=True, debug=True)
