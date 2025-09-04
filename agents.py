from dotenv import load_dotenv
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from .tools import fetch_patient_record, insert_patient_record, fetch_doctors_by_specialty
from .prompts import DB_PROMPT, SCHEDULING_PROMPT, SUPERVISOR_PROMPT

load_dotenv()

llm = ChatOllama(model="qwen3:1.7b")

db_agent = create_react_agent(
    model=llm,
    tools=[
        fetch_patient_record,
        insert_patient_record,
    ],
    prompt=DB_PROMPT,
    name="EMR Database Agent",
)

scheduling_agent = create_react_agent(
    model=llm,
    tools=[fetch_doctors_by_specialty],
    prompt=SCHEDULING_PROMPT,
    name="Scheduling Agent",
)

supervisor_agent = create_supervisor(
    model=llm,
    agents=[db_agent, scheduling_agent],
    name="Supervisor Agent",
    prompt=SUPERVISOR_PROMPT,
)


def build_agent_system():
    return supervisor_agent.compile()
