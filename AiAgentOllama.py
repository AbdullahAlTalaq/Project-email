import ollama
from msgraph import GraphServiceClient
from msgraph.generated.users.item.send_mail.send_mail_post_request_body import SendMailPostRequestBody
from msgraph.generated.models.message import Message
from msgraph.generated.models.item_body import ItemBody
from msgraph.generated.models.body_type import BodyType
from msgraph.generated.models.recipient import Recipient
from msgraph.generated.models.email_address import EmailAddress
from azure.identity import DeviceCodeCredential
import asyncio
import re

scope = ["User.Read", "Mail.Send", "Mail.Read"]
tenant_id ="2c86bbfc-8d04-41ff-a83a-942f075e0f60"
client_id = "8f6af9ce-445a-47b3-9134-e21738881000"
credential = DeviceCodeCredential(tenant_id=tenant_id,client_id=client_id)

graph_client = GraphServiceClient(credential, scope)

def generate_email_prompt(message):
  
  output = ollama.generate(
  model="deepseek-coder-v2",
  prompt=f"""Call Ollama with the Llama 3.2 model"""
         """You are an email assistant that helps users interact with their Microsoft Outlook.
please write en email using this message {message}
Only return the message.""",
  stream=False,
)
  
  return output['response']

def extract_email(prompt):
   email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
   emails = re.findall(email_pattern, prompt)



async def send_email():
    x =input("Enter your prompt: ")
    emails = extract_email(x)
    message_email = generate_email_prompt(x)
    request_body = SendMailPostRequestBody(
	message = Message(
		subject = "Test",
		body = ItemBody(
			content_type = BodyType.Text,
			content = message_email,
		),
		to_recipients = [
			Recipient(
				email_address = EmailAddress(
					address = emails,
				),
			),
		],
	),
	save_to_sent_items = False,
)    
    await graph_client.me.send_mail.post(request_body)
 

if __name__ == '__main__':
    asyncio.run(send_email()) 