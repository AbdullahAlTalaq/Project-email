from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import base64
import os
import openai


openai.api_key = "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"

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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

def summarize_with_gpt(subject, sender, date, body):
    prompt = f"""
You are an assistant. Read the following email and provide:
1. A short summary of what the email is about.
2. A suggested reply in a professional tone.

Email Details:
Subject: {subject}
From: {sender}
Date: {date}
Body:
{body}
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  
            messages=[
                {"role": "system", "content": "You are an expert email assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        gpt_reply = response.choices[0].message['content'].strip()
        print("\n GPT Summary & Suggested Reply:")
        print(gpt_reply)

    except Exception as e:
        print("Error calling OpenAI GPT:", str(e))

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
    result = service.users().messages().list(userId='me', labelIds=['STARRED']).execute()
    messages = result.get('messages', [])

    print(f"\n Number of starred emails: {len(messages)}\n")

    for idx, message in enumerate(messages):
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        headers = msg['payload']['headers']

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'No Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')
        body = get_email_body(msg['payload'])

        print(f"\n Email #{idx+1}")
        print(f"Subject: {subject}")
        print(f"From: {sender}")
        print(f"Date: {date}")
       

        summarize_with_gpt(subject, sender, date, body)
        print("=" * 80)

if __name__ == '__main__':
    main()
