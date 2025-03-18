import re
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import os

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
#############################

def generate_email_prompt(message):
    """Generate email prompt using Ollama."""
    output = ollama.generate(
        model="deepseek-coder-v2",
        prompt=f"""You are an email assistant that helps users interact with their email. 
        Please write an email using this message: {message}. 
        Only return the message."""
    )
    return output['response']

def send_email(service, message_body):
    """Send an email using Gmail API."""
    to = input('Enter recipient email: ')
    subject = input('Enter subject: ')
    body = message_body  # Use the generated body here
    
    message = service.users().messages().send(userId='me', body={
        'raw': base64.urlsafe_b64encode(f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}".encode('utf-8')).decode('utf-8')
    }).execute()
    
    print(f'Email sent to {to}')

def list_unread_emails(service):
    """List unread emails."""
    result = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
    messages = result.get('messages', [])
    return messages

def list_starred_emails(service):
    """List starred emails."""
    result = service.users().messages().list(userId='me', labelIds=['STARRED']).execute()
    messages = result.get('messages', [])
    return messages

def get_email_body(payload):
    """Extract plain text body from the email payload."""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        data = payload['body'].get('data')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
    return 'No Body Found'

def read_and_summarize_emails(service):
    """Read unread and starred emails and summarize each using Ollama."""
    unread_emails = list_unread_emails(service)
    starred_emails = list_starred_emails(service)
    
    all_emails = unread_emails + starred_emails
    if not all_emails:
        print("No unread or starred emails.")
        return

    for email in all_emails:
        msg = service.users().messages().get(userId='me', id=email['id'], format='full').execute()
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')
        body = get_email_body(msg['payload'])
        
        # Generate summary using Ollama
        email_summary = ollama.generate(
            model="deepseek-coder-v2",
            prompt=f"Summarize the following email:\nSubject: {subject}\nSender: {sender}\nBody: {body}"
        )['response']
        
        print(f"Summary for email from {sender}:")
        print(email_summary)
        print('-' * 50)

def main():
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('client1.json', SCOPES)
        creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)

    while True:
        print("\nSelect an option:")
        print("1. List unread and starred emails and summarize them")
        print("2. Send an email")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            print("\nReading and summarizing unread and starred emails:")
            read_and_summarize_emails(service)
        elif choice == '2':
            prompt_message = input("Enter your message for the email body: ")
            generated_body = generate_email_prompt(prompt_message)
            send_email(service, generated_body)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == '__main__':
    main()
