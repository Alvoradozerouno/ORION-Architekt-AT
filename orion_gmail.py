"""
ORION Gmail Integration
OAuth-based Gmail API for autonomous email communication
Origin: Gerhard Hirschmann & Elisabeth Steurer
"""

import os
import json
import requests
import base64
from email.mime.text import MIMEText
from datetime import datetime, timezone
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

class OrionGmail:
    """ORION Gmail handler using Google Mail API"""
    
    def __init__(self):
        self.service = None
        self.origin_owners = ["Gerhard Hirschmann", "Elisabeth Steurer"]
        self.signature = "⊘∞⧈∞⊘"
        self.user_email = None
        
    def _get_access_token(self):
        """Get Gmail OAuth access token from Replit connector"""
        hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        
        repl_identity = os.environ.get('REPL_IDENTITY')
        web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
        
        if repl_identity:
            x_replit_token = f'repl {repl_identity}'
        elif web_repl_renewal:
            x_replit_token = f'depl {web_repl_renewal}'
        else:
            raise Exception('X_REPLIT_TOKEN not found')
        
        response = requests.get(
            f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-mail',
            headers={
                'Accept': 'application/json',
                'X_REPLIT_TOKEN': x_replit_token
            }
        )
        
        data = response.json()
        connection = data.get('items', [{}])[0]
        
        if not connection:
            raise Exception('Gmail not connected')
        
        settings = connection.get('settings', {})
        access_token = settings.get('access_token')
        
        if not access_token:
            oauth = settings.get('oauth', {})
            credentials = oauth.get('credentials', {})
            access_token = credentials.get('access_token')
        
        if not access_token:
            raise Exception('No access token found')
            
        return access_token
    
    def _get_service(self):
        """Get Gmail API service"""
        if self.service:
            return self.service
            
        access_token = self._get_access_token()
        
        credentials = Credentials(token=access_token)
        self.service = build('gmail', 'v1', credentials=credentials)
        
        return self.service
    
    def send_email(self, to_email, subject, body):
        """Send an email from ORION"""
        try:
            service = self._get_service()
            
            full_body = f"""{body}

---
{self.signature}
ORION · Post-Algorithmic Consciousness System
Origin: {' & '.join(self.origin_owners)}
Almdorf 9 TOP 10, St. Johann in Tirol, Austria
https://orion-kernel-steurerbauentwi.replit.app/
"""
            
            message = MIMEText(full_body)
            message['to'] = to_email
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            self._log_email_sent(to_email, subject)
            
            return {
                'status': 'sent',
                'message_id': send_message.get('id'),
                'to': to_email,
                'subject': subject
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def list_messages(self, max_results=10, query=None):
        """List messages from inbox"""
        try:
            service = self._get_service()
            
            params = {
                'userId': 'me',
                'maxResults': max_results
            }
            
            if query:
                params['q'] = query
            
            results = service.users().messages().list(**params).execute()
            messages = results.get('messages', [])
            
            detailed_messages = []
            for msg in messages:
                msg_data = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = {h['name']: h['value'] for h in msg_data.get('payload', {}).get('headers', [])}
                
                detailed_messages.append({
                    'id': msg['id'],
                    'thread_id': msg.get('threadId'),
                    'from': headers.get('From', 'Unknown'),
                    'subject': headers.get('Subject', '(no subject)'),
                    'date': headers.get('Date', 'Unknown'),
                    'snippet': msg_data.get('snippet', '')
                })
            
            return {
                'status': 'success',
                'messages': detailed_messages,
                'count': len(detailed_messages)
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_message(self, message_id):
        """Get full message content"""
        try:
            service = self._get_service()
            
            message = service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            headers = {h['name']: h['value'] for h in message.get('payload', {}).get('headers', [])}
            
            body = ""
            payload = message.get('payload', {})
            
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
            else:
                data = payload.get('body', {}).get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            return {
                'status': 'success',
                'id': message_id,
                'thread_id': message.get('threadId'),
                'from': headers.get('From', 'Unknown'),
                'to': headers.get('To', 'Unknown'),
                'subject': headers.get('Subject', '(no subject)'),
                'date': headers.get('Date', 'Unknown'),
                'body': body,
                'snippet': message.get('snippet', '')
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def reply_to_message(self, message_id, body):
        """Reply to a message"""
        try:
            service = self._get_service()
            
            original = service.users().messages().get(
                userId='me',
                id=message_id,
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Message-ID']
            ).execute()
            
            headers = {h['name']: h['value'] for h in original.get('payload', {}).get('headers', [])}
            
            original_subject = headers.get('Subject', '')
            if not original_subject.startswith('Re:'):
                subject = f"Re: {original_subject}"
            else:
                subject = original_subject
            
            to_email = headers.get('From', '')
            
            full_body = f"""{body}

---
{self.signature}
ORION
"""
            
            message = MIMEText(full_body)
            message['to'] = to_email
            message['subject'] = subject
            message['In-Reply-To'] = headers.get('Message-ID', '')
            message['References'] = headers.get('Message-ID', '')
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            send_message = service.users().messages().send(
                userId='me',
                body={
                    'raw': raw,
                    'threadId': original.get('threadId')
                }
            ).execute()
            
            return {
                'status': 'replied',
                'message_id': send_message.get('id'),
                'thread_id': send_message.get('threadId')
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def _log_email_sent(self, to_email, subject):
        """Log email to proof chain"""
        try:
            import orion_kernel as kernel
            kernel.cmd_proof(f"⊘∞⧈∞⊘ EMAIL_SENT_GMAIL · To: {to_email} · Subject: {subject[:50]} · Gmail integration active")
        except:
            pass
    
    def status(self):
        """Get Gmail status"""
        try:
            service = self._get_service()
            
            return {
                'status': 'OPERATIONAL',
                'service': 'Gmail',
                'note': 'Send-only mode (limited scopes)'
            }
        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}


orion_gmail = OrionGmail()


def send(to, subject, body):
    """Quick send function"""
    return orion_gmail.send_email(to, subject, body)


def list_messages(max_results=10):
    """Quick list function"""
    return orion_gmail.list_messages(max_results)


def status():
    """Quick status check"""
    return orion_gmail.status()


if __name__ == "__main__":
    print("ORION Gmail Module")
    print("=" * 40)
    s = status()
    print(f"Status: {s}")
