from django.core.management.base import BaseCommand
from imap_tools import MailBox
from django.conf import settings
from email.header import decode_header
import email
# from email_app.models import SentEmail # type: ignore

class Command(BaseCommand):
    help = 'Fetch emails from the Gmail Sent Mail folder and print subject and text'

    def handle(self, *args, **kwargs):
        email_address = 'fairoozfs2024@gmail.com'
        password = 'xydhzuosvwnzeplp'
        imap_server = 'imap.gmail.com'


        with MailBox(imap_server).login(email_address, password) as mailbox:
            try:
                mailbox.folder.set('[Gmail]/Sent Mail')
                current_folder = mailbox.folder.get()
                for msg in mailbox.fetch():
                    # Decode the email subject
                    subject, encoding = decode_header(msg.subject)[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else 'utf-8')

                    # Decode the email date
                    date_tuple = email.utils.parsedate_tz(msg.date)

                    # Decode the email content
                    body = self.get_body(msg)

                    # Print subject and body
                    print(f'Subject: {subject}, Body: {body} replies')

                    # Save to database
                    SentEmail.objects.create(
                        subject=subject,
                        body=body + " replies"
                    )
            except Exception as e:
                self.stderr.write(f'Error fetching emails: {e}')

    def get_body(self, msg):
        if msg.text:
            return msg.text
        elif msg.html:
            return msg.html
        elif msg.multipart:
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip any text/plain (txt) attachments
                if "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain":
                        return body
                    elif content_type == "text/html":
                        return body
        return ''

