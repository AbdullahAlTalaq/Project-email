import os
import logging
from typing import List, Optional
from pathlib import Path
import json

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
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


agent_storage: str = "tmp/agents.db"

#Models
# "yasserrmd/Qwen2.5-7B-Instruct-1M"
# "qwq"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='agent_system.log'
)
logger = logging.getLogger(__name__)
console = Console()

# Configuration
class Config:
    # Base paths and configurations
    BASE_DIR = Path(__file__).parent
    FILES_DIR = BASE_DIR / "Files"
    VECTOR_DB_PATH = BASE_DIR / "tmp" / "lancedb"
    
    # Knowledge base configuration
    PDF_PATH = FILES_DIR / "Career Co.pdf"
    VECTOR_TABLE_NAME = "payslip"
    EMBEDDER_MODEL = "openhermes"
    
    # Agent models
    TEAM_LEADER_MODEL = "qwq"
    EMAIL_AGENT_MODEL = "qwq"

        # Instructions
    with open('instructions.json', 'r') as file:
        INSTRUCTIONS_PATH = json.load(file)



@tool(show_result=True, stop_after_tool_call=True)
def send_email(receiver: str, email_subject: str, message_body: str) -> str:
    """
    Tool: send_email

    Description:
    Use this tool to send an email to a specified recipient. Provide the recipient's email address,
    the email subject line, and the full message body. You should only call this tool once per request.

    Args:
        receiver (str): Email address of the recipient.
        email_subject (str): The subject of the email.
        message_body (str): The main content/message to send.

    Returns:
        A success or failure message indicating whether the email was sent.
    """
    try:
        logger.info(f"Sending email to {receiver}")
        gmail_sender = GmailEmailSender(user_id='user3')  # Unique ID per user
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


def create_knowledge_base() -> PDFKnowledgeBase:
    """
    Create and configure the knowledge base.
    
    Returns:
        Configured PDFKnowledgeBase instance
    """
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
    """
    Create and configure individual agents.
    
    Returns:
        email_agent
    """
    try:
        
        # Email agent
        email_agent = Agent(
            name="Email Agent",
            role="Send emails to specific recipients",
            model=Ollama(id=Config.EMAIL_AGENT_MODEL),
            knowledge= knowledge_base,
            tools=[send_email, DuckDuckGoTools()],
            add_history_to_messages= True,
            instructions=[ "You are an expert assistant with access to a tool that can send emails.",
                            "Use the send_email tool when a task requires emailing someone.",
                            "Only send the email once per request.",
                            "Verify that the email has a valid subject, recipient, and message body.",
                            "Use the PDF knowledge base to write detailed, relevant content.",
                            "If information is missing, search the web to complete the task.",
                            "Always write a well-structured email before sending.",
                            "Remain clear and professional in tone unless told otherwise.",
                            "Do not include disclaimers or say that you're an AI assistant.",
                            "End your process by calling the send_email tool when ready."],
            markdown=True,
            storage=SqliteStorage(
                table_name="web_agent",
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
    """
    Create and configure the agent team.
    
    Args:
        web_agent: The web search agent
        email_agent: The email sending agent
        knowledge_base: The knowledge base to use
        
    Returns:
        Configured Team instance
    """
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

try:
    console.print("[bold green]Starting Agent System...[/bold green]")
    
    # Create knowledge base
    knowledge_base = create_knowledge_base()
    
    # Create agents
    email_agent = create_agents(knowledge_base)
    
    # Create team
    agent_team = create_team(email_agent)
    
    # Load knowledge base
    if agent_team.knowledge is not None:
        console.print("[bold blue]Loading knowledge base...[/bold blue]")
        agent_team.knowledge.load()
        console.print("[bold green]Knowledge base loaded successfully[/bold green]")

    # create UI app
    app = Playground(agents=[email_agent]).get_app(use_async=False)
    
    # Process a task
    console.print("[bold blue]Processing task...[/bold blue]")
    # agent_team.print_response(
    #     "Write about Co-Ownership from pdf that you have and if there any information search the internet based on the pdf. "
    #     "When you done, send the information to Yahya(y75910@gmail.com) via email.",
    #     stream=True
    # )
    
    # Print all messages in this session
    # messages_in_session = agent_team.get_messages_for_session()
    # pprint(messages_in_session)

except Exception as e:
    logger.critical(f"System failed: {str(e)}")
    console.print(f"[bold red]Error: {str(e)}[/bold red]")

if __name__ == "__main__":
    serve_playground_app("Gmail_Agent_copy:app", reload=True)
