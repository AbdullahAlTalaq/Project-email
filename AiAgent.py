import chromadb
from llama_index.core import PromptTemplate, Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

def setup_resume_qa_system(files):
    llm = Ollama(model="llama3.2")
    embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    Settings.llm = llm
    Settings.embed_model = embed_model

    documents = SimpleDirectoryReader(input_files=files).load_data()
    chroma_client = chromadb.EphemeralClient()
    chroma_collection = chroma_client.create_collection("ollama")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
        transformations=[SentenceSplitter(chunk_size=256, chunk_overlap=10)]
    )

    template = (
        "Imagine you are a data scientist's assistant and "
        "you answer a recruiter's questions about the data scientist's experience.\n"
        "Here is some context from the data scientist's resume:\n"
        "-----------------------------------------\n"
        "{context_str}\n"
        "-----------------------------------------\n"
        "Considering the above information, please respond to the following inquiry:\n\n"
        "Question: {query_str}\n\n"
        "Answer clearly and concisely. The data scientist's name is Bhavik Jikadara."
    )

    qa_template = PromptTemplate(template)

    return index.as_query_engine(
        text_qa_template=qa_template,
        similarity_top_k=3
    )





















import asyncio, random
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from GmailEmailSender import GmailEmailSender
from resume_qa import setup_resume_qa_system

# Setup resume query engine once
resume_qa_engine = setup_resume_qa_system(["./resume.pdf"])

# Email sender tool
def Send_Email(receiver: str, email_subject: str, message_body: str) -> str:
    try:
        gmail_sender = GmailEmailSender(user_id='user1')
        gmail_sender.send_email(to=receiver, subject=email_subject, body=message_body)
        return "Sent successfully"
    except Exception as e:
        return f"Send failed: {str(e)}"

# Resume QA tool
def Query_Resume(query: str) -> str:
    try:
        response = resume_qa_engine.query(query)
        return response.response
    except Exception as e:
        return f"Error querying resume: {str(e)}"

# Tool that queries the resume and sends an email
def Email_Resume_Info(receiver: str, topic: str, question: str) -> str:
    try:
        info = resume_qa_engine.query(question).response
        subject = f"{topic} Experience"
        body = f"Hello,\n\nHere is Bhavik's experience with {topic}:\n\n{info}\n\nBest regards,\nYour Assistant"
        result = Send_Email(receiver, subject, body)
        return f"Email status: {result}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# Email reader
def Get_Recent_Emails() -> str:
    try:
        gmail = GmailEmailSender(user_id='user1')
        emails = gmail.get_recent_emails()
        if not emails:
            return "No recent emails found."
        return "\n---\n".join(
            [f"Email {i}:\nFrom: {e['from']}\nSubject: {e['subject']}\nBody: {e['body'][:300]}..." for i, e in enumerate(emails, 1)]
        )
    except Exception as e:
        return f"Error retrieving emails: {str(e)}"

# Fun tools
def Best_singer(song: str) -> str:
    return f"The best singer is {random.choice(['ammar', 'yara', 'momo', 'song jin woo', 'mecseney'])} in {song}."

def multiply(a: float, b: float) -> float:
    return a * b

# Wrap tools
tools = [
    FunctionTool.from_defaults(fn=Send_Email, name="send_email_tool"),
    FunctionTool.from_defaults(fn=Get_Recent_Emails, name="Get_Recent_Emails"),
    FunctionTool.from_defaults(fn=Best_singer, name="Best_singer_tool"),
    FunctionTool.from_defaults(fn=multiply, name="multiply_tool"),
    FunctionTool.from_defaults(fn=Query_Resume, name="query_resume_tool"),
    FunctionTool.from_defaults(fn=Email_Resume_Info, name="email_resume_info_tool"),
]

# Create the agent
agent = FunctionAgent(
    llm=Ollama(model="yasserrmd/Qwen2.5-7B-Instruct-1M"),
    tools=tools,
    system_prompt=(
        "You are a helpful assistant agent. You can:\n"
        "- Send and read emails.\n"
        "- Retrieve Bhavik Jikadara’s resume info using a resume query tool.\n"
        "- Send emails with resume summaries using the info.\n"
        "- Do basic math and have fun with music prompts.\n"
        "Use tools smartly. If a user asks you to email something based on the resume, query it first, then email the result."
    )
)

# Run the agent
async def main():
    # Try one of these to test:
    # response = await agent.run("Send an email to recruiter@example.com about Bhavik's Python experience")
    response = await agent.run("What does Bhavik know about Python?")
    print(str(response))

if __name__ == "__main__":
    asyncio.run(main())





