from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from langgraph.graph import END, START, MessagesState, StateGraph

from .tools import fetch_patient_record, insert_patient_record
from .prompts import DB_PROMPT

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

db_agent = create_react_agent(
    model=llm,
    tools=[fetch_patient_record, insert_patient_record],
    prompt=DB_PROMPT,
    name="EMR Database Agent",
)

supervisor_agent = create_supervisor(
    model=llm,
    agents=[db_agent],
    name="Supervisor Agent",
    prompt="You are a supervisor agent overseeing the EMR Database Agent. Your role is to ensure that the database agent performs its tasks correctly and efficiently. You will receive the results of the database agent's actions and must provide feedback or further instructions as necessary. Always ensure that the database agent adheres to the guidelines provided in its prompt and uses the tools appropriately.",
)


def build_agent_system():
    graph = StateGraph(MessagesState)
    graph.add_node(START, supervisor_agent)
    graph.add_node(db_agent)
    graph.add_edge(supervisor_agent, db_agent)
    graph.add_edge(supervisor_agent, END)

    return graph.compile()
