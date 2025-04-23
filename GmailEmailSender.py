import os
import pickle
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

class GmailEmailSender:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.send']
    CREDENTIALS_FILE = 'credentials.json'
    
    def __init__(self, user_id='default'):
        self.user_id = user_id
        self.creds = None
        self.service = self.authenticate()

    def authenticate(self):
        token_path = f'token_{self.user_id}.pickle'
        if os.path.exists(token_path):
            with open(token_path, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_FILE, self.SCOPES)
                self.creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(self.creds, token)

        return build('gmail', 'v1', credentials=self.creds)

    def create_message(self, to, subject, body):
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return {'raw': raw_message}

    def send_email(self, to, subject, body):
        message = self.create_message(to, subject, body)
        try:
            sent_message = self.service.users().messages().send(userId='me', body=message).execute()
            print(f"Message sent: ID {sent_message['id']}")
            return sent_message
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def get_recent_emails(self, max_results=5):
        try:
            results = self.service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=max_results).execute()
            messages = results.get('messages', [])

            email_data = []

            for msg in messages:
                msg_detail = self.service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
                payload = msg_detail.get('payload', {})
                headers = payload.get('headers', [])

                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

                body = ''
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain':
                            body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                            break
                else:
                    body_data = payload.get('body', {}).get('data')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data).decode('utf-8')

                email_data.append({
                    'from': sender,
                    'subject': subject,
                    'body': body.strip()
                })

            return email_data

        except Exception as e:
            print(f"Failed to fetch emails: {e}")
            return []
