import gradio as gr
import dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from .agents import build_agent_system

dotenv.load_dotenv()

agent = build_agent_system()
system_prompt = "You are a helpful medical assistant."


def stream_response(message, history):

    msgs = [SystemMessage(system_prompt)]
    for human, ai in history or []:
        if human:
            msgs.append(HumanMessage(content=human))
        if ai:
            msgs.append(AIMessage(content=ai))
    if message:
        msgs.append(HumanMessage(content=message))

    state_input = {"messages": msgs}

    partial = ""
    for msg_chunk, meta in agent.stream(
        state_input,
        stream_mode="messages",
        subgraphs=True,
    ):
        content = getattr(msg_chunk, "content", None)
        if content:
            partial += content if isinstance(content, str) else str(content)
            yield partial


demo = gr.ChatInterface(
    fn=stream_response,
    textbox=gr.Textbox(
        placeholder="Enter your message here...", container=False, scale=7
    ),
    chatbot=gr.Chatbot(),
    submit_btn="Send",
)

demo.launch(share=True, debug=True)
