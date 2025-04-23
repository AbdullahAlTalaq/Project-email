import chromadb
from llama_index.core import PromptTemplate, Settings, SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.vector_stores.chroma import ChromaVectorStore

class RagSystem:
    def __init__(self, files):
        llm = Ollama(model="llama3")
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
            "Imagine you are reading a PDF and answering questions about it.\n"
            "Here is context from the document:\n"
            "-----------------------------------------\n"
            "{context_str}\n"
            "-----------------------------------------\n"
            "Now respond to the question below:\n\n"
            "Question: {query_str}\n\n"
            "Answer clearly and concisely."
        )
        qa_template = PromptTemplate(template)

        self.query_engine = index.as_query_engine(
            text_qa_template=qa_template,
            similarity_top_k=3
        )

    def query(self, query: str) -> str:
        response = self.query_engine.query(query)
        return response.response



import asyncio
import random
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.ollama import Ollama
from llama_index.core.tools import FunctionTool
from GmailEmailSender import GmailEmailSender
from RagSystem import RagSystem

# Initialize RAG system for document reading
rag = RagSystem(["./resume.pdf"])

# Email sending tool
def Send_Email(receiver: str, email_subject: str, message_body: str) -> str:
    try:
        gmail_sender = GmailEmailSender(user_id='user1')
        gmail_sender.send_email(to=receiver, subject=email_subject, body=message_body)
        return "Sent successfully"
    except Exception as e:
        return f"Send failed: {str(e)}"

# PDF querying tool
def Query_PDF(query: str) -> str:
    try:
        return rag.query(query)
    except Exception as e:
        return f"Query failed: {str(e)}"

# Fun tools (optional)
def Best_singer(song: str) -> str:
    return f"The best singer is {random.choice(['ammar', 'yara', 'momo', 'song jin woo', 'mecseney'])} in {song}."

def multiply(a: float, b: float) -> float:
    return a * b

# Tool registration
tools = [
    FunctionTool.from_defaults(fn=Send_Email, name="send_email_tool"),
    FunctionTool.from_defaults(fn=Query_PDF, name="query_pdf_tool"),
    FunctionTool.from_defaults(fn=Best_singer, name="Best_singer_tool"),
    FunctionTool.from_defaults(fn=multiply, name="multiply_tool"),
]

# Agent definition
agent = FunctionAgent(
    llm=Ollama(model="yasserrmd/Qwen2.5-7B-Instruct-1M"),
    tools=tools,
    system_prompt=(
        "You are a helpful assistant agent. You can:\n"
        "- Query content from a PDF using `query_pdf_tool`.\n"
        "- Send emails using `send_email_tool`.\n"
        "If a user asks you to send something from a document, use the query tool first to retrieve the content, then compose and send the email."
    )
)

# Run the agent
async def main():
    response = await agent.run("Email the Python experience from the PDF to testaiagent6@gmail.com")
    print(str(response))

if __name__ == "__main__":
    asyncio.run(main())
