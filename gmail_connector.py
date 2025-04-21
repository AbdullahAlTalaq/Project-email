from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
import base64
import os


class GmailConnector:
    def __int__(self, credentials_path='credentials.json',token_path='token.json',scopes=None):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.scopes = scopes or ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
        self.service =None
    def authenticate(self):
        creds = None

        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, self.scopes)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.scopes)
                creds = flow.run_local_server(port=0)
            with open(self.token_path,'w') as token_file:
                token_file.write(creds.to_json())
        self.service = build('gmail','v1',credentials=creds)
    def is_authenticated(self):
        return self.service is not None

    def send_email(self, to: str, subject: str, body: str) -> dict:
        if not self.service:
            raise RuntimeError("Service not initialized. Call authenticate() first.")
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': raw_message}
        sent_msg = self.service.users().messages().send(userId="me", body=create_message).execute()
        return sent_msg


'''
from gmail_connector import GmailConnector

def main():
    # Initialize the connector
    gmail = GmailConnector()

    # Authenticate and connect
    gmail.authenticate()

    # Fetch and print latest emails
    if gmail.is_authenticated():



from llama_index.tools import FunctionTool

def send_email_tool(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail API using GmailConnector."""
    try:
        gmail = GmailConnector()
        gmail.authenticate()
        result = gmail.send_email(to=to, subject=subject, body=body)
        return f"✅ Email sent to {to}. Message ID: {result['id']}"
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"

send_email_llama_tool = FunctionTool.from_defaults(
    fn=send_email_tool,
    name="send_email_tool",
    description="Send an email. Inputs: to, subject, body."
)

'''





















'''
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


def list_unread_emails(service):
    """List unread emails."""
    result = service.users().messages().list(userId='me', labelIds=['INBOX', 'UNREAD']).execute()
    messages = result.get('messages', [])

    if not messages:
        print('No unread messages.')
    else:
        print('Unread messages:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')
            body = get_email_body(msg['payload'])

            print(f'Subject: {subject}\nFrom: {sender}\nDate: {date}\n')
            print('-' * 50)


def list_starred_emails(service):
    """List starred emails."""
    result = service.users().messages().list(userId='me', labelIds=['STARRED']).execute()
    messages = result.get('messages', [])

    if not messages:
        print('No starred messages.')
    else:
        print('Starred messages:')
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')
            body = get_email_body(msg['payload'])

            print(f'Subject: {subject}\nFrom: {sender}\nDate: {date}\n')
            print('-' * 50)


def send_email(service):
    """Send an email."""
    to = input('Enter recipient email: ')
    subject = input('Enter subject: ')
    body = input('Enter body: ')

    message = service.users().messages().send(userId='me', body={
        'raw': base64.urlsafe_b64encode(f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}".encode('utf-8')).decode('utf-8')
    }).execute()

    print(f'Email sent to {to}')


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
        print("1. List unread emails and starred emails")
        print("2. Send an email")
        print("3. Exit")

        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            print("\nListing unread emails:")
            list_unread_emails(service)
            print("\nListing starred emails:")
            list_starred_emails(service)
        elif choice == '2':
            send_email(service)
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice, please try again.")


if __name__ == '__main__':
    main()

'''