from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI ,set_tracing_disabled , ModelSettings, function_tool
from GmailEmailSender import GmailEmailSender
import asyncio
# Configure the model
model = OpenAIChatCompletionsModel( 
    model="yasserrmd/Qwen2.5-7B-Instruct-1M",
    openai_client=AsyncOpenAI(base_url="http://localhost:11434/v1",api_key="ollama")
    
)
#############

##################
# Create the agent


@function_tool  
def Sent_Email(receiver:str,email_subject:str,message_body:str ) -> str:
    
    """This tool is for sending email. 
    Args:
    receiver: This argument contains the recipient's email address. 
    message_body: This argument contains the body of the message. 
    email_subject: This argument contains the subject line of the message. 
    """
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

Sent_Email_agent = Agent(
    name="Sent Email agent",
    instructions="Always respond in haiku form",
    model=model,
    tools=[Sent_Email],
)

history_tutor_agent = Agent(
    name="History Tutor",
    handoff_description="Specialist agent for historical questions",
    instructions="You provide assistance with historical queries. Explain important events and context clearly.",
        model=model,

)

math_tutor_agent = Agent(
    name="Math Tutor",
    handoff_description="Specialist agent for math questions",
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples",
    model=model,

)
triage_agent = Agent(
    name="Triage Agent",
    instructions="You determine which agent to use based on the user's question",
    model=model,
    handoffs=[history_tutor_agent, math_tutor_agent, Sent_Email_agent]
)



set_tracing_disabled(disabled=True)

async def main():
# Run the agent synchronously
    result = await Runner.run(triage_agent, "What is the capital of France?")
    print(result.final_output)

asyncio.run(main())
