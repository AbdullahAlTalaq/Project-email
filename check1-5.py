
from contact_utils import create_contacts_table, add_contact

create_contacts_table()
add_contact("yahya", "y75910@gmail.com")
add_contact("ali", "testaiagent6@gmail.com")

from contact_utils import get_email_by_name

@tool(show_result=True, stop_after_tool_call=True)
def Send_Email(receiver: str, email_subject: str, message_body: str) -> str:
    """Send an email. 'receiver' can be a name (looked up in DB) or full email address."""
    try:
        if "@" not in receiver:
            email = get_email_by_name(receiver)
            if not email:
                return f"Send failed: No email found for '{receiver}'"
            receiver = email

        gmail_sender = GmailEmailSender(user_id='user3')
        gmail_sender.send_email(to=receiver, subject=email_subject, body=message_body)
        return f"Sent successfully to {receiver}"
    except Exception as e:
        return f"Send failed: {e}"



from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.ollama import Ollama
from agno.tools import tool
from agno.team.team import Team
from GmailEmailSender import GmailEmailSender 
from agno.embedder.ollama import OllamaEmbedder
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.knowledge.pdf import PDFKnowledgeBase, PDFReader
from agno.playground import Playground, serve_playground_app
from agno.storage.sqlite import SqliteStorage
from agno.memory.v2 import Memory
from agno.memory.v2.db.sqlite import SqliteMemoryDb



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
    model=Ollama(id="mychen76/qwen3_cline_roo_coder_14b"),
    db=SqliteMemoryDb(table_name="user_memories", db_file=agent_storage),
)


Writing_Email_agent = Agent(
    name="Writing Email agent",
    role="Writing an email about a topic",
    knowledge=knowledge_base,
    tools=[DuckDuckGoTools()],
    model=Ollama(id="mychen76/qwen3_cline_roo_coder_14b"),
    instructions=[
    "You are responsible for composing a complete, professional email.",
    "Utilize the following resources in order:",
    "1. Knowledge Base: Retrieve information relevant to the email topic.",
    "2. Memory: Access stored user information (e.g., name, role, projects).",
    "3. DuckDuckGoTools: Search the internet for any missing information.",
    "Your output must include:",
    "- receiver: The recipient's email address.",
    "- email_subject: The subject line of the email.",
    "- message_body: The body of the email in plain text.",
    "Ensure the email is well-structured and professionally formatted.",
    "Do not send the email; your task is solely to compose it.",
    "Avoid explanations or justifications; provide only the requested fields.",
],
    markdown=True,
    #storage=SqliteStorage(table_name="Writing_Email_agent", db_file=agent_storage),
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=5,
    # Adds markdown formatting to the messages
    monitoring=True,
    memory=memory,
)

Send_Email_agent = Agent(
    name="Send Email agent",
    role="Send an Email to a specific person only",
    model=Ollama(id="mychen76/qwen3_cline_roo_coder_14b"),
    tools=[Send_Email],
    instructions=[
    "You are responsible for sending emails using the Send_Email tool.",
    "You will receive the following inputs:",
    "- receiver: The recipient's email address.",
    "- email_subject: The subject line of the email.",
    "- message_body: The body of the email.",
    "Use the Send_Email tool to send the email exactly as provided.",
    "Do not compose, modify, or evaluate the email content.",
    "Report the success or failure of the sending operation without additional commentary.",
],
    markdown=True,
    #storage=SqliteStorage(table_name="Send_Email_agent", db_file=agent_storage),
    # Adds the current date and time to the instructions
    add_datetime_to_instructions=True,
    # Adds the history of the conversation to the messages
    add_history_to_messages=True,
    # Number of history responses to add to the messages
    num_history_responses=5,
    # Adds markdown formatting to the messages
    monitoring=True,
)

# Handoffs_Agent=Agent(
#     name="Handoffs_Agent",
#     role="You determine the appropriate agent for each task.",
#     model=Ollama(id="mistral-small3.1"),
#     team=[Writing_Email_agent,Send_Email_agent],
    
#     instructions=[
#     "You manage task delegation between agents and maintain user memory.",
#     "Upon receiving a user message:",
#     "1. Analyze the message to determine the appropriate action.",
#     "   - If the task involves composing an email, delegate to Writing_Email_agent.",
#     "   - If the task involves sending an email, delegate to Send_Email_agent.",
#     "   - For other tasks, handle them directly or delegate as appropriate.",
#     "2. After Writing_Email_agent composes an email:",
#     "   - Present the email content to the user for approval.",
#     "   - Await user confirmation before proceeding.",
#     "   - If approved, delegate to Send_Email_agent to send the email.",
#     "   - If not approved, halt the process or allow for revisions.",
#     "3. Use the update_user_memory tool to store important user information (e.g., personal details, project information) for future reference.",
#     "Ensure clear communication and appropriate delegation for each task.",
# ],
#     markdown=True,
#     storage=SqliteStorage(table_name="Handoffs_Agent", db_file=agent_storage),
#     # Adds the current date and time to the instructions
#     add_datetime_to_instructions=True,
#     # Adds the history of the conversation to the messages
#     add_history_to_messages=True,
#     # Number of history responses to add to the messages
#     num_history_responses=10,
#     # Adds markdown formatting to the messages)
#     memory=memory,
#     enable_agentic_memory=True,
#     enable_user_memories=True,
#     monitoring=True
# )

Handoffs_Team=Team(
    name="Handoffs_Team",
    #role="You determine the appropriate agent for each task.",
    model=Ollama(id="mychen76/qwen3_cline_roo_coder_14b"),
    members=[Writing_Email_agent,Send_Email_agent],
    instructions=[
    "You are responsible for managing the flow of tasks between agents.",
    "When asked to send an email, follow these steps:",
    "1. First, use the Writing_Email_agent to write a complete email (receiver, subject, body).",
    "2. After Writing_Email_agent finishes, print out the generated email clearly to the user.",
    "3. Ask the user for approval: 'Do you approve sending this email? (yes/no)'",
    "4. If the user says 'yes', pass the email content to the Send_Email_agent to send it.",
    "5. If the user says 'no', do not proceed to sending. Instead, end the process or allow edits.",
    "You must not edit or modify the email yourself.",
    "Your job is to coordinate writing, approval, and sending, using the appropriate agent for each task.",
    "Stay focused on passing tasks to agents. Do not perform any writing or sending directly.",
    ],
    extra_data={"ali":"testaiagent6@gmail.com"},
    markdown=True,
    storage=SqliteStorage(table_name="Handoffs_Teams", db_file=team_storage, auto_upgrade_schema= True,),
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

#teams=[Handoffs_Team],
#agents=[Handoffs_Agent]
app = Playground(teams=[Handoffs_Team]).get_app()

if __name__ == "__main__":
    serve_playground_app("RAG_Agent:app", reload=True)



# Give the team a task
#agent_team.print_response("Write about Co-Ownership based on knowledge base, And write to me about the new iPhone 16e from Apple.When you done, send the Email to Yahya(y75910@gmail.com) via email. ", stream=True)

# if __name__ == "__main__":

#     agent_team.print_response("Who is the best singer in my country KSA song ?")
#     agent_team.print_response("What is the weather like in my country?")


    # Print all messages in this session
    #messages_in_session = agent_team.get_messages_for_session()
    #pprint(messages_in_session)
