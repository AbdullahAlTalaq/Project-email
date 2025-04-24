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



