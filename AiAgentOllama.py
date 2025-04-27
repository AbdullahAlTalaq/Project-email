from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.models.ollama import Ollama
from agno.tools import tool
from agno.team.team import Team
import random
from rich.pretty import pprint
from utils.GmailEmailSender import GmailEmailSender 
from agno.embedder.ollama import OllamaEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader

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

@tool(show_result=True, stop_after_tool_call=True)
def Send_Email(receiver:str,email_subject:str,message_body:str ) -> str:
    """This tool is for sending email. receiver: This argument contains the recipient's email address, message_body: This argument contains the body of the message, email_subject: This argument contains the subject line of the message. """
    
    try:

        gmail_sender = GmailEmailSender(user_id='user3')  # Unique ID per user
        gmail_sender.send_email(
        to=receiver,
        subject= email_subject,
        body=message_body
        )
        return "Sent successfully"
    except Exception as e:
        
        return "Send failed"




Send_Email_agent = Agent(
    name="Send Email agent",
    role="write and Send an Email to a specific person",
    knowledge=knowledge_base,
    model=Ollama(id="qwq"),
    tools=[Send_Email,DuckDuckGoTools()],
    instructions=["You are an Agent who writes the email using the knowledge base. If you need information that is not there, use the DuckDuckGoTools tool.",
                  "Use the knowledge base and if that's not enough for you, use DuckDuckGoTools too.",
                  "Write a professional email, and prepare the receiver (email address), email_subject (subject line), and message_body (body of the message).",
                  "After writing the email, use the Send_Email tool to send the email.",
                  "Implement things, use tools, and do not overthink and explain"],
    markdown=True,
)
if Send_Email_agent.knowledge is not None:
    Send_Email_agent.knowledge.load()
agent_team = Team(
    name="Team leader",
    mode="coordinate",
    model=Ollama(id="qwq"),  # You can use a different model for the team leader agent
    members=[Send_Email_agent],
    instructions=["""Always use the info that is available in the tools only.
    If you receive 'Sent successfully' or 'Send failed' from the tool, stop sending another email.
    To send an email, follow these steps:
       1. Call the Send_Email_agent function.
    If you receive 'Sent successfully':
       1. Print that the sending was successful.
       2. Print the entire message (receiver, subject, body).
    If you receive 'Send failed':
       1. Print that the sending failed.
       2. Print the message 'Not sent'.""",
       "Implement things, use tools, and do not overthink and explain"],
    show_tool_calls=True,  # Uncomment to see tool calls in the response
    markdown=True,
)

# Give the team a task
agent_team.print_response("Write about Co-Ownership based on knowledge base, And write to me about the new iPhone 16e from Apple.When you done, send the information to Yahya(y75910@gmail.com) via email. ", stream=True)

# if __name__ == "__main__":

#     agent_team.print_response("Who is the best singer in my country KSA song ?")
#     agent_team.print_response("What is the weather like in my country?")


    # Print all messages in this session
    #messages_in_session = agent_team.get_messages_for_session()
    #pprint(messages_in_session)


"""
import os
import logging
from typing import List, Optional
from pathlib import Path
import json

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

from rich.console import Console
from GmailEmailSender import GmailEmailSender

# ========= MEMORY SYSTEM (NEW) =========

class UserMemoryManager:
    def __init__(self):
        self.user_profiles = {}
    
    def add_user_profile(self, user_id: str, profile: dict):
        self.user_profiles[user_id] = profile
    
    def get_user_profile(self, user_id: str) -> Optional[dict]:
        return self.user_profiles.get(user_id)

# Instantiate memory manager
memory_manager = UserMemoryManager()

# ========= CONFIG =========

agent_storage: str = "tmp/agents.db"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='agent_system.log'
)
logger = logging.getLogger(__name__)
console = Console()

class Config:
    BASE_DIR = Path(__file__).parent
    FILES_DIR = BASE_DIR / "Files"
    VECTOR_DB_PATH = BASE_DIR / "tmp" / "lancedb"
    
    PDF_PATH = FILES_DIR / "Career Co.pdf"
    VECTOR_TABLE_NAME = "payslip"
    EMBEDDER_MODEL = "openhermes"
    
    TEAM_LEADER_MODEL = "qwq"
    EMAIL_AGENT_MODEL = "qwq"

    with open('instructions.json', 'r') as file:
        INSTRUCTIONS_PATH = json.load(file)

# ========= TOOL =========

@tool(show_result=True, stop_after_tool_call=True)
def send_email(receiver: str, email_subject: str, message_body: str, sender_id: str = "user3") -> str:
    """
    Tool: send_email
    Now uses memory to personalize emails.
    """
    try:
        logger.info(f"Sending email to {receiver}")
        gmail_sender = GmailEmailSender(user_id=sender_id)

        # Get user profile from memory
        user_profile = memory_manager.get_user_profile(sender_id)

        if user_profile:
            # Personalize message
            signature = user_profile.get("signature", "")
            message_body = f"{message_body}\n\n{signature}"
        
        gmail_sender.send_email(
            to=receiver,
            subject=email_subject,
            body=message_body
        )
        logger.info("Email sent successfully")
        return "Email sent successfully"
    except Exception as e:
        logger.error(f"Failed to send email: {str(e)}")
        return f"Email sending failed: {str(e)}"

# ========= FUNCTIONS =========

def create_knowledge_base() -> PDFKnowledgeBase:
    try:
        knowledge_base = PDFKnowledgeBase(
            path=str(Config.PDF_PATH),
            vector_db=LanceDb(
                uri=str(Config.VECTOR_DB_PATH),
                table_name=Config.VECTOR_TABLE_NAME,
                search_type=SearchType.hybrid,
                embedder=OllamaEmbedder(id=Config.EMBEDDER_MODEL),
            ),
            reader=PDFReader(chunk=True),
        )
        logger.info("Knowledge base created successfully")
        return knowledge_base
    except Exception as e:
        logger.error(f"Failed to create knowledge base: {str(e)}")
        raise

def create_agents(knowledge_base: PDFKnowledgeBase):
    try:
        email_agent = Agent(
            name="Email Agent",
            role="Send personalized emails based on user memory",
            model=Ollama(id=Config.EMAIL_AGENT_MODEL),
            knowledge=knowledge_base,
            tools=[send_email, DuckDuckGoTools()],
            add_history_to_messages=True,
            instructions=[
                "Use the send_email tool to send emails.",
                "Before sending, ensure the email matches the sender's tone based on memory.",
                "Use a formal tone for bosses, and friendly for colleagues, based on memory.",
                "Attach the user's signature at the end of the message if available."
            ],
            markdown=True,
            storage=SqliteStorage(
                table_name="email_agent",
                db_file=agent_storage,
                auto_upgrade_schema=True,
            ),
            show_tool_calls=True,
            num_history_responses=5,
            add_name_to_instructions=True,
            add_datetime_to_instructions=True,
        )
        logger.info("Agents created successfully")
        return email_agent
    except Exception as e:
        logger.error(f"Failed to create agents: {str(e)}")
        raise

def create_team(email_agent: Agent) -> Team:
    try:
        agent_team = Team(
            name="Research Team",
            mode="coordinate",
            model=Ollama(id=Config.TEAM_LEADER_MODEL),
            members=[email_agent],
            instructions=[f'{Config.INSTRUCTIONS_PATH}'],
            show_tool_calls=True,
            markdown=True,
            add_datetime_to_instructions=True,
        )
        logger.info("Team created successfully")
        return agent_team
    except Exception as e:
        logger.error(f"Failed to create team: {str(e)}")
        raise

# ========= MAIN =========

try:
    console.print("[bold green]Starting Agent System...[/bold green]")
    
    knowledge_base = create_knowledge_base()
    email_agent = create_agents(knowledge_base)
    agent_team = create_team(email_agent)

    if agent_team.knowledge is not None:
        console.print("[bold blue]Loading knowledge base...[/bold blue]")
        agent_team.knowledge.load()
        console.print("[bold green]Knowledge base loaded successfully[/bold green]")

    # Add example user memory
    memory_manager.add_user_profile(
        user_id="user3",
        profile={
            "name": "Yahya Alsharif",
            "position": "Project Manager",
            "colleague_style": "Friendly and semi-formal",
            "boss_style": "Very formal and structured",
            "signature": "Best regards, Yahya"
        }
    )

    # Create UI app
    app = Playground(agents=[email_agent]).get_app(use_async=False)

except Exception as e:
    logger.critical(f"System failed: {str(e)}")
    console.print(f"[bold red]Error: {str(e)}[/bold red]")

if __name__ == "__main__":
    serve_playground_app("Gmail_Agent_with_Memory:app", reload=True)

"""


