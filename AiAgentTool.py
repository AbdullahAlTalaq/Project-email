from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import base64
import ollama
from smolagents import CodeAgent,HfApiModel,load_tool,tool
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

@tool
def email_generator(email_body:str,title_value:str,emails:str) -> str:
    """ Tool that sends an email with the given email_body. 
    Args:
        email_body:use This agrment to generate email_body
    """
     try:
        message = service.users().messages().send(userId='me', body={
        'raw': base64.urlsafe_b64encode(f"To: {emails}\r\nSubject: {title_value}\r\n\r\n{email_body}".encode('utf-8')).decode('utf-8')}).execute()
    except:
        print("Error")

def get_token():
    creds = none 
    #you have to include token file inside project directory 
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json",SCOPES)
    else: 
        # if you don't have token file than get client json from google cloud 
        flow = InstalledAppFlow.from_client_secrets_file('Client.json', SCOPES)

        with open("token.json","w") as token:
            token.write(creds.to_json())

    service = build('gmail',"v1",credentials=creds)
    return service


def extractor(prompt):
# here we take the email and we remove it from prompt 
   email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
   emails = re.findall(email_pattern, prompt)
   prompt=prompt.removeprefix(email_pattern)
   #here extract title
   title_index = text.find("title:")

   result = text[:title_index].strip()
   title_value = text[title_index + len("title:"):].strip()

   prompt = result 


   return prompt,title_value,emails
   #we will call the function tool     we will pass emails, title_value, prompt

def prompt_function():

    return prompt



def main():
    model = HfApiModel(max_tokens=5096,temperature=0.5,model_id='model to use tommorw',custom_role_conversions=None,)
    agent = CodeAgent(model=model,tools=[email_generator])
    print("This is a script for sending emails usign Ai Agent (example for sending email: send email about the dinner tonight :example@test.Sabic title:DinnerToNight)")
    prompt = input("Enter your prompt here: ")

    email = prompt_function()
    service = get_token()
    prompt, title_value, emails= extractor(email)
    agent.run(prompt,title_value, emails)









"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def create_message(sender, to, subject, message_text):
    message = MIMEMultipart()
    message['to'] = to
    message['subject'] = subject
    msg = MIMEText(message_text)
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw_message}

"""