# hey check out john doe dob:1985-2-14 email: john.doe@example.com
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

    for msg_chunk, _ in agent.stream(state_input, stream_mode="messages"):
        content = getattr(msg_chunk, "content", None)
        if not content:
            continue

        # Case 1: doctor scheduling info (tool return)
        if isinstance(content, dict) and "doctors" in content:
            doctors = content["doctors"]
            accordion_blocks = []
            for doc in doctors:
                # Instead of `with`, build an Accordion component and append
                accordion_blocks.append(
                    gr.Accordion(
                        f"{doc['name']} — {doc['specialty']}",
                        open=False,
                        children=[
                            gr.Markdown(
                                f"[30 min]({doc['calendly_30_url']})  |  [60 min]({doc['calendly_60_url']})"
                            )
                        ],
                    )
                )
            yield gr.ChatMessage(
                role="assistant", content="Here are available doctors:"
            )
            for block in accordion_blocks:
                yield gr.ChatMessage(role="assistant", content=block)
            continue

        # Case 2: normal agent text response
        if isinstance(content, str):
            yield gr.ChatMessage(role="assistant", content=content)


demo = gr.ChatInterface(
    fn=stream_response,
    textbox=gr.Textbox(
        placeholder="Enter your message here...", container=False, scale=7
    ),
    chatbot=gr.Chatbot(),
    submit_btn="Send",
)

demo.launch(share=True, debug=True)
