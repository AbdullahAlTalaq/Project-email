import streamlit as st
import asyncio
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from GmailEmailSender import GmailEmailSender

# Streamlit config
st.set_page_config(
    page_title="📨 AI Email Assistant",
    page_icon="📧",
    layout="centered"
)

st.title("📨 Email Assistant (LlamaIndex + Ollama)")
st.markdown("This AI agent can query PDFs and send emails using your instructions.")

# --- Define the email sending tool ---
def Send_Email(receiver: str, email_subject: str, message_body: str) -> str:
    try:
        gmail_sender = GmailEmailSender(user_id='user1')
        gmail_sender.send_email(to=receiver, subject=email_subject, body=message_body)
        return "✅ Email sent successfully."
    except Exception as e:
        return f"❌ Send failed: {str(e)}"


def multiply(a: float, b: float) -> float:
    return a * b

# --- Register tools ---
tools = [
    FunctionTool.from_defaults(fn=Send_Email, name="send_email_tool"),
    FunctionTool.from_defaults(fn=multiply,name="multiply two numbers")
]

# --- Create the agent ---
@st.cache_resource
def create_agent():
    return FunctionAgent(
        llm=Ollama(model="yasserrmd/Qwen2.5-7B-Instruct-1M"),
        tools=tools,
        system_prompt=(
            "You are a helpful assistant agent. You can:\n"
            "- Query content from a PDF using `query_pdf_tool`.\n"
            "user will ask you to send the email. You have to generate simple email to the target email that user will mention in the prompt."
        )
    )

agent = create_agent()

# --- User input area ---
user_prompt = st.text_area("Enter your instruction for the agent:", height=150)

# --- Run the agent ---
if st.button("Run Agent"):
    if not user_prompt:
        st.warning("Please enter a prompt first.")
    else:
        try:
            async def run():
                with st.spinner("Agent is thinking..."):
                    response = await agent.run(user_prompt)
                    st.success("Agent Response:")
                    st.write(str(response))
            asyncio.run(run())
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# --- Footer ---
st.markdown("---")
st.markdown("Powered by 🦙 LlamaIndex + Ollama + Gmail API + Streamlit")
