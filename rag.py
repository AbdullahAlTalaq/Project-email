from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.ollama import Ollama
from agno.tools import tool
from agno.team.team import Team
from agno.embedder.ollama import OllamaEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from agno.memory.v2 import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb
from agno.storage.mongodb import MongoDbStorage
import json
from Yahya_files.Tools import Send_Email, Read_Email

Email_Dictionary= json.load(open("Yahya_files/Email_Dictionary.json", "r"))

knowledge_base = PDFKnowledgeBase(
        path="Files\Career Co.pdf",
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="payslip",
            search_type=SearchType.hybrid,
            embedder=OllamaEmbedder(id="openhermes"),
          ),
    reader=PDFReader(chunk=True),
)


agent_storage: str = "tmp_yahya/agents.db"

team_storage: str = "tmp_yahya/teams.db"

memory = Memory(
    # Use any model for creating memories
    model=Ollama(id="mistral-small3.1"),
    db=SqliteMemoryDb(table_name="user_memories", db_file=agent_storage),
)


Writing_Email_agent = Agent(
    name="Writing Email agent",
    role="Writing an email about a topic",
    knowledge=knowledge_base,
    tools=[DuckDuckGoTools()],
    context={"Email_Dictionary": Email_Dictionary},
    add_context=True,
    model=Ollama(id="yasserrmd/Qwen2.5-7B-Instruct-1M"),
    instructions= open("Yahya_files/Writing_Email_agent.txt", encoding="utf-8").read().strip(),
    markdown=True,
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=5,
    # Adds markdown formatting to the messages
    monitoring=True,
    add_state_in_messages=True,
    memory=memory,
)

Read_Email_agent = Agent(
    name="Read Email agent",
    role="Reading emails for the past few days",
    model=Ollama(id="yasserrmd/Qwen2.5-7B-Instruct-1M"),
    tools=[Read_Email],
    instructions=open("Yahya_files/Read_Email_agent.txt", encoding="utf-8").read().strip(),
    markdown=True,
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=5,
    # Adds markdown formatting to the messages
    monitoring=True,
)

Send_Email_agent = Agent(
    name="Send Email agent",
    role="Send an Email to a specific person only",
    model=Ollama(id="yasserrmd/Qwen2.5-7B-Instruct-1M"),
    tools=[Send_Email],
    instructions=open("Yahya_files/Send_Email_agent.txt", encoding="utf-8").read().strip(),
    markdown=True,
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=5,
    # Adds markdown formatting to the messages
    monitoring=True,
)

Handoffs_Team=Team(
    name="Handoffs_Team",
    #role="You determine the appropriate agent for each task.",
    model=Ollama(id="yasserrmd/Qwen2.5-7B-Instruct-1M"),
    members=[Writing_Email_agent,Send_Email_agent,Read_Email_agent],
    instructions=open("Yahya_files/Handoffs_Team.txt", encoding="utf-8").read().strip(),
    markdown=True,
    storage=MongoDbStorage(collection_name="Handoffs_Teams", db_name="agno"),
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    read_team_history= True,
    enable_team_history=True,
    # Number of history responses to add to the messages
    num_history_runs=10,
    # Adds markdown formatting to the messages)
    memory=memory,
    enable_agentic_memory=True,
    enable_user_memories=True,
    monitoring=True,
)

if Writing_Email_agent.knowledge is not None:
    Writing_Email_agent.knowledge.load()

app = Playground(teams=[Handoffs_Team]).get_app()

if __name__ == "__main__":
    serve_playground_app("RAG_Agent:app", reload=True)

