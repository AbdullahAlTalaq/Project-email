import asyncio , random
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from GmailEmailSender import GmailEmailSender


def Send_Email(receiver:str,email_subject:str,message_body:str ) -> str:
    """This tool is for sending email. receiver: This argument contains the recipient's email address, message_body: This argument contains the body of the message, email_subject: This argument contains the subject line of the message. """
    try:
        gmail_sender = GmailEmailSender(user_id='user1')  # Unique ID per user
        gmail_sender.send_email(
        to=receiver,
        subject= email_subject,
        body=message_body
        )
        return "Sent successfully"
    except Exception as e:
        
        return "Send failed"


def Get_Recent_Emails() -> str:
    """This tool retrieves the last 5 received emails, including sender, subject, and message body."""
    try:
        gmail = GmailEmailSender(user_id='user1')  # Or dynamic user ID
        emails = gmail.get_recent_emails()

        if not emails:
            return "No recent emails found."

        formatted = []
        for i, email in enumerate(emails, 1):
            formatted.append(
                f"Email {i}:\nFrom: {email['from']}\nSubject: {email['subject']}\nBody: {email['body'][:300]}...\n"
            )

        return "\n---\n".join(formatted)

    except Exception as e:
        return f"Error retrieving emails: {str(e)}"

def Best_singer(song: str) -> str:
    """Get the best singer ."""
    # In a real implementation, this would call a weather API
    singer_Names= ["ammar", "yara", "momo", "song jin woo", "mecseney"]
    random_singer = random.choice(singer_Names)

    return f"The best singer is {random_singer} in {song}."


# Define a simple calculator tool
def multiply(a: float, b: float) -> float:
    """Useful for multiply two numbers."""
    return a * b


summarize_email_llama_tool = FunctionTool.from_defaults(
    fn=Get_Recent_Emails,
    name="Get_Recent_Emails",
    description="Summarize an email. Inputs: to, subject, body."
)

send_email_llama_tool = FunctionTool.from_defaults(
    fn=Send_Email,
    name="send_email_tool",
    description="Send an email. retrieves sender, subject, and a short preview of the message body."
)

Best_singer_llama_tool = FunctionTool.from_defaults(
    fn=Best_singer,
    name="Best_singer_tool",
    description="This tool for chosesing which best singer"
)
multiply_llama_tool = FunctionTool.from_defaults(
    fn=multiply,
    name="multiply_tool",
    description="This tool to multiply two numbers"
)
'''
def sum(a: float, b: float) -> float:
    """Useful for sum two numbers."""
    return a + b
'''


# Create an agent workflow with our calculator tool
agent = FunctionAgent(
    llm=Ollama(model="yasserrmd/Qwen2.5-7B-Instruct-1M"),
    tools=[send_email_llama_tool,Best_singer_llama_tool,multiply_llama_tool,summarize_email_llama_tool ],
    system_prompt="You are a helpful assistant agnet that can send emails To send an email, follow these steps: 1. Write a professional email. 2. Prepare the receiver (email address), email_subject (subject line), and message_body (body of the message).    If you receive 'Sent successfully': 1. Print that the sending was successful. 2. Print the entire message (receiver, subject, body).  If you receive 'Send failed':  1. Print that the sending failed. 2. Stop Call the Send_Email_agent'. or retrieves sender, subject, and a short preview of the message body for last five emails or select best singer beased or making mutliply calculations beased on user prompt.",
)


async def main():
    # Run the agent
    response = await agent.run("send random email to testaiagent6@gmail.com")
    print(str(response))


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())
    