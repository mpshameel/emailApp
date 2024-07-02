from email.utils import parseaddr
import imaplib
import email
from datetime import datetime
from email.header import decode_header
from django.shortcuts import render
from django.conf import settings
import json
from imap_tools import MailBox, A
import re

from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup

import imapclient
from email.policy import default
from imapclient import IMAPClient
from email.parser import BytesParser
from email import policy


def fetch_emailsTest(email_id, password, mail_server='imap.gmail.com'):
    # Connect to the mail server
    mail = imaplib.IMAP4_SSL(mail_server)
    mail.login(email_id, password)
    mail.select('inbox')  # Select the inbox folder

    result, data = mail.search(None, 'ALL')
    email_ids = data[0].split()

    for email_id in email_ids:
        result, message_data = mail.fetch(email_id, '(RFC822)')
        raw_email = message_data[0][1]
        msg = email.message_from_bytes(raw_email, policy=default)
        process_email(msg)

    mail.logout()

def process_email(msg):
    text = None
    html = None

    if msg.is_multipart():
        for part in msg.iter_parts():
            content_type = part.get_content_type()
            body = part.get_payload(decode=True)
            if content_type == "text/plain":
                text = body.decode()
            elif content_type == "text/html":
                html = body.decode()
    else:
        content_type = msg.get_content_type()
        body = msg.get_payload(decode=True)
        if content_type == "text/plain":
            text = body.decode()
        elif content_type == "text/html":
            html = body.decode()

    attachments = extract_attachments(msg)
    headers = dict(msg.items())
    in_reply_to = msg['headers']
    if in_reply_to is None:
        print("-----------------------------------")
    else:
        print("-----------------------------------"+str(in_reply_to))
    print(f"-----------------------------------jjj {dict(msg.items())}")
    print(f"Subject: {msg['subject']}")
    print(f"From: {msg['from']}")
    print(f"To: {msg['to']}")
    print(f"Date: {msg['date']}")
    print(f"Text: {text}")
    print(f"HTML: {html}")
    print(f"Attachments: {attachments}")
    print(f"-----------------------------------")

def fetch_inbox(email_id, password, mail_server='imap.gmail.com', mail_port=993, max_emails=10):
    class Msg:
        def __init__(self,username, subject, from_, to, date, text, html, flags, cc, bcc, reply_to, uid, headers, attachments):
            self.username = username
            self.subject = subject
            self.from_ = from_
            self.to = to
            self.date = date
            self.text = text
            self.html = html
            self.flags = flags
            self.cc = cc
            self.bcc = bcc
            self.reply_to = reply_to
            self.uid = uid
            self.headers = headers
            self.attachments = attachments

    # Connect to the email server
    mail = imaplib.IMAP4_SSL(mail_server, mail_port)
    try:
        mail.login(email_id, password)
    except imaplib.IMAP4.error:
        print("Login failed.")
        return []

    # Select the mailbox you want to use
    status, messages = mail.select('inbox')
    if status != 'OK':
        print("Failed to select mailbox.")
        return []

    # Search for all emails in the inbox
    status, data = mail.search(None, 'ALL')
    if status != 'OK':
        print("Error searching for emails.")
        return []

    # Convert messages to a list of email IDs
    email_ids = data[0].split()
    if not email_ids:
        print("No emails found.")
        return []

    # Process a limited number of emails
    email_ids = email_ids[-max_emails:]

    # List to store email details
    emails = []
    try:
        for email_id in email_ids:
            print("---------------------------------####")
            status, data = mail.fetch(email_id,  '(FLAGS BODY.PEEK[])')
            if status != 'OK':
                print(f"Error fetching email ID {email_id}")
                continue

            raw_email = data[0][1]
            msg = email.message_from_bytes(raw_email)

            # Decode the email subject
            subject, encoding = decode_header(msg['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')

            to = msg.get('To')
            from_ = msg.get('From')
            date = msg.get('Date')

            # Process the 'To' field correctly
            to_addresses = [addr.strip() for addr in to.split(',')] if to else []
            parsed_emails = re.findall(r'[\w\.-]+@[\w\.-]+', str(to_addresses))

             # Extract username from the 'From' field
            name, email_address = parseaddr(from_)
            username = name if name else email_address

            # Decode the email date
            date_tuple = email.utils.parsedate_tz(date)
            if date_tuple:
                local_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
            else:
                local_date = datetime.now()

            text = None
            html = None
            attachments = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    content_type = part.get_content_type()
                    body = part.get_payload(decode=True)
                    if content_type == "text/plain":
                        text = body.decode()
                    elif content_type == "text/html":
                        html = body.decode()
            else:
                content_type = msg.get_content_type()
                body = msg.get_payload(decode=True)
                if content_type == "text/plain":
                    text = body.decode()
                elif content_type == "text/html":
                    html = body.decode()

            # Extract flags
            flags = []
            for response_part in data:
                if isinstance(response_part, tuple):
                    flag_response = response_part[0].decode()
                    if 'FLAGS' in flag_response:
                        flags = flag_response.split('FLAGS')[1].strip().strip('()').split()


            to = parsed_emails
            flags = flags
            cc = msg.get_all('Cc', [])
            bcc = msg.get_all('Bcc', [])
            reply_to = msg.get_all('Reply-To', [])
            uid = email_id.decode('utf-8')
            headers = dict(msg.items())
            


            attachments = extract_attachments(msg)
            emails.append(Msg(
                username= username,
                subject=subject,
                from_=from_,
                to=to,
                date=date,
                text=text,
                html=html,
                flags=flags,
                cc=cc,
                bcc=bcc,
                reply_to=reply_to,
                uid=uid,
                headers=headers,
                attachments=attachments
            ),)

    except Exception as e:
        print(f"An error occurred: {e}")

    mail.logout()
    return emails

def extract_attachments(msg):
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_maintype() == 'multipart':
                continue
            if part.get('Content-Disposition') is None:
                continue
            attachment = {
                'filename': part.get_filename(),
                'content_type': part.get_content_type(),
                'payload': part.get_payload(decode=True)
            }
            attachments.append(attachment)
    else:
        if msg.get_content_maintype() != 'multipart' and msg.get('Content-Disposition'):
            attachment = {
                'filename': msg.get_filename(),
                'content_type': msg.get_content_type(),
                'payload': msg.get_payload(decode=True)
            }
            attachments.append(attachment)
    return attachments
    
def extract_NonMultiAttachments(msg):
    attachments = []
    for att in msg.attachments:
        attachment = {
            'filename': att.filename,
            'content_type': att.content_type,
            'payload': att.payload
        }
        attachments.append(attachment)
    return attachments


# Test Codes

def email_to_dict(msg):
    return {
        'subject': msg.subject,
        'from': msg.from_,
        'to': msg.to,
        'date': msg.date.isoformat() if msg.date else None,
        'text': msg.text,
        'html': msg.html,
        'flags': msg.flags,
        'cc': msg.cc,
        'bcc': msg.bcc,
        'reply_to': msg.reply_to,
        'uid': msg.uid,
        'headers': dict(msg.headers),
        # Add other fields as needed
    }


def fetch_sentEmail(email_id, password, mail_server='imap.gmail.com'):
    class Msg:
        def __init__(self,username, subject, from_, to, date, text, html, flags, cc, bcc, reply_to, uid, headers, attachments):
            self.username = username
            self.subject = subject
            self.from_ = from_
            self.to = to
            self.date = date
            self.text = text
            self.html = html
            self.flags = flags
            self.cc = cc
            self.bcc = bcc
            self.reply_to = reply_to
            self.uid = uid
            self.headers = headers
            self.attachments = attachments

    send = []
    with MailBox(mail_server).login(email_id, password) as mailbox:
        try:
            # Try to select the correct folder for "Sent Mail"
            # mailbox.folder.set('[Gmail]/Sent Mail')
            try:
                print("Attempting to set folder '[Gmail]/Sent Mail'...")
                mailbox.folder.set('[Gmail]/Sent Mail')
                print("Folder '[Gmail]/Sent Mail' set successfully.")
            except Exception as e:
                print(f"Failed to select folder: {e}")
                return send
            # Get the selected folder
            current_folder = mailbox.folder.get()   
            messages = mailbox.fetch(A(all=True))

            # Fetch emails from the selected folder
            try:
                print("Attempting to fetch emails from the selected folder..."+str(current_folder))
                for msg in messages:
                    # Extract the username from the email_id
                    match = re.match(r"([^@]+)@", email_id)
                    if match:
                        username = match.group(1)
                    else:
                        username = email_id

                    attachments = []
                    attachments = extract_NonMultiAttachments(msg)
                    
                    send.append(Msg(
                        username=username,
                        subject=msg.subject,
                        from_=msg.from_,
                        to=msg.to,
                        date=msg.date,
                        text=msg.text,
                        html=msg.html,
                        flags=msg.flags,
                        cc=msg.cc,
                        bcc=msg.bcc,
                        reply_to=msg.reply_to,
                        uid=msg.uid,
                        headers=msg.headers,
                        attachments=attachments
                    ),)
                    print(f"Fetched email: {msg.subject}")
                print("Emails fetched successfully.")
            except Exception as e:
                print(f"Failed to fetch emails: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
    return send


def fetch_draftEmail(email_id, password, mail_server='imap.gmail.com'):
    class Msg:
        def __init__(self,username, subject, from_, to, date, text, html, flags, cc, bcc, reply_to, uid, headers, attachments):
            self.username = username
            self.subject = subject
            self.from_ = from_
            self.to = to
            self.date = date
            self.text = text
            self.html = html
            self.flags = flags
            self.cc = cc
            self.bcc = bcc
            self.reply_to = reply_to
            self.uid = uid
            self.headers = headers
            self.attachments = attachments

    drafts = []
    with MailBox(mail_server).login(email_id, password) as mailbox:
        try:
            # Try to select the correct folder for "Sent Mail"
            # mailbox.folder.set('[Gmail]/Sent Mail')
            try:
                print("Attempting to set folder '[Gmail]/Drafts'...")
                mailbox.folder.set('[Gmail]/Drafts')
                print("Folder '[Gmail]/Drafts' set successfully.")
            except Exception as e:
                print(f"Failed to select folder: {e}")
                return drafts
            # Get the selected folder
            current_folder = mailbox.folder.get()   
            messages = list(mailbox.fetch(A(all=True))) 

            # Fetch emails from the selected folder
            try:
                print("Attempting to fetch emails from the selected folder...")
                for msg in messages:
                    # Extract the username from the email_id
                    match = re.match(r"([^@]+)@", email_id)
                    if match:
                        username = match.group(1)
                    else:
                        username = email_id

                    attachments = []
                    attachments = extract_NonMultiAttachments(msg)

                    drafts.append(Msg(
                        username=username,
                        subject=msg.subject,
                        from_=msg.from_,
                        to=msg.to,
                        date=msg.date,
                        text=msg.text,
                        html=msg.html,
                        flags=msg.flags,
                        cc=msg.cc,
                        bcc=msg.bcc,
                        reply_to=msg.reply_to,
                        uid=msg.uid,
                        headers=msg.headers,
                        attachments=attachments
                    ),)
                    print(f"Fetched email: {msg.subject}")
                print("Emails fetched successfully.")
            except Exception as e:
                print(f"Failed to fetch emails: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
    return drafts



def fetch_allMails(email_id, password, mail_server='imap.gmail.com', mail_port=993, max_emails=5):
    class Msg:
        def __init__(self,username, subject, from_, to, date, text, html, flags, cc, bcc, reply_to, uid, headers, attachments):
            self.username = username
            self.subject = subject
            self.from_ = from_
            self.to = to
            self.date = date
            self.text = text
            self.html = html
            self.flags = flags
            self.cc = cc
            self.bcc = bcc
            self.reply_to = reply_to
            self.uid = uid
            self.headers = headers
            self.attachments = attachments

    allMails = []
    with MailBox(mail_server).login(email_id, password) as mailbox:
        try:
            # Try to select the correct folder for "Sent Mail"
            # mailbox.folder.set('[Gmail]/Sent Mail')
            try:
                print("Attempting to set folder '[Gmail]/All Mail'...")
                mailbox.folder.set('[Gmail]/All Mail')
                print("Folder '[Gmail]/All Mail' set successfully.")
            except Exception as e:
                print(f"Failed to select folder: {e}")
                return allMails
            # Get the selected folder
            current_folder = mailbox.folder.get()   
            messages = list(mailbox.fetch(A(all=True))) 

            # Fetch emails from the selected folder
            try:
                print("Attempting to fetch emails from the selected folder...")
                for msg in messages:
                    # Extract the username from the email_id
                    match = re.match(r"([^@]+)@", email_id)
                    if match:
                        username = match.group(1)
                    else:
                        username = email_id

                    attachments = []
                    attachments = extract_NonMultiAttachments(msg)

                    allMails.append(Msg(
                        username=username,
                        subject=msg.subject,
                        from_=msg.from_,
                        to=msg.to,
                        date=msg.date,
                        text=msg.text,
                        html=msg.html,
                        flags=msg.flags,
                        cc=msg.cc,
                        bcc=msg.bcc,
                        reply_to=msg.reply_to,
                        uid=msg.uid,
                        headers=msg.headers,
                        attachments=attachments
                    ),)
                    print(f"Fetched email: {msg.subject}")
                print("Emails fetched successfully.")
            except Exception as e:
                print(f"Failed to fetch emails: {e}")

        except Exception as e:
            print(f"An error occurred: {e}")
    return allMails

def fetch_idEmail(allMails, messageId):
    class Msg:
        def __init__(self,username, subject, from_, to, date, text, html, flags, cc, bcc, reply_to, uid, headers, attachments):
            self.username = username
            self.subject = subject
            self.from_ = from_
            self.to = to
            self.date = date
            self.text = text
            self.html = html
            self.flags = flags
            self.cc = cc
            self.bcc = bcc
            self.reply_to = reply_to
            self.uid = uid
            self.headers = headers
            self.attachments = attachments

    detailEmail = []
    for email in allMails:
        emailMessageId = str(email.headers.get('message-id')).replace(",","")

        if emailMessageId == messageId:
            detailEmail.append(Msg(
                username=email.username,
                subject=email.subject,
                from_=email.from_,
                to=email.to,
                date=email.date,
                text=email.text,
                html=email.html,
                flags=email.flags,
                cc=email.cc,
                bcc=email.bcc,
                reply_to=email.reply_to,
                uid=email.uid,
                headers=email.headers,
                attachments=email.attachments
                ),)
        else:
            pass
    return detailEmail


def fetch_repliesEmail(allMails, messageId):
    class Msg:
        def __init__(self,username, subject, from_, to, date, text, html, flags, cc, bcc, reply_to, uid, headers, attachments):
            self.username = username
            self.subject = subject
            self.from_ = from_
            self.to = to
            self.date = date
            self.text = text
            self.html = html
            self.flags = flags
            self.cc = cc
            self.bcc = bcc
            self.reply_to = reply_to
            self.uid = uid
            self.headers = headers,
            self.attachments = attachments

    replies = []
    message_id = messageId
    for email in allMails:
        try :
            in_reply_to = email.headers.get('in-reply-to') if email.headers.get('in-reply-to') else None
            in_reply_to = str(in_reply_to).replace(",","")
            message_id = str(messageId).replace(",","")
            # print("------------------------------------ggg  "+str(in_reply_to)+"    "+str(message_id))
            if in_reply_to and in_reply_to == message_id:
                print("---------------------vvvvvvv"+str(email.username))
                replies.append(Msg(
                    username=email.username,
                    subject=email.subject,
                    from_=email.from_,
                    to=email.to,
                    date=email.date,
                    text=email.text,
                    html=email.html,
                    flags=email.flags,
                    cc=email.cc,
                    bcc=email.bcc,
                    reply_to=email.reply_to,
                    uid=email.uid,
                    headers=email.headers,
                    attachments=email.attachments
                ),)
                message_id = email.headers.get('message-id')
                # in_replly_to = email.headers.get('in-reply-to')
                # print("----------------------------------1"+str(message_id)+"-------------"+str(email.headers.get('message-id')))
                return message_id, replies
                
            # else:
            #     # print("---------------------------eeee2")
            #     pass
        except Exception as e:
            print(".")
            in_reply_to = ""
    return None, replies

    # class Msg:
    #     def __init__(self,username, subject, from_, to, date, text, html, flags, cc, bcc, reply_to, uid, headers):
    #         self.username = username
    #         self.subject = subject
    #         self.from_ = from_
    #         self.to = to
    #         self.date = date
    #         self.text = text
    #         self.html = html
    #         self.flags = flags
    #         self.cc = cc
    #         self.bcc = bcc
    #         self.reply_to = reply_to
    #         self.uid = uid
    #         self.headers = headers

    # # Connect to the email server
    # mail = imaplib.IMAP4_SSL(mail_server, mail_port)
    # try:
    #     mail.login(email_id, password)
    # except imaplib.IMAP4.error:
    #     print("Login failed.")
    #     return []

    # # Select the mailbox you want to use
    # status, messages = mail.select('inbox')
    # if status != 'OK':
    #     print("Failed to select mailbox.")
    #     return []
    
    # # List all mailboxes
    # result, mailboxes = mail.list()
    # if result == 'OK':
    #     print("Mailboxes:")
    #     for mailbox in mailboxes:
    #         print(mailbox.decode())

    # # After listing mailboxes, you can select the correct one
    # # For example, 'INBOX' is a common default name
    # folder = 'All Mail'  # Adjust based on the listed mailboxes

    # try:
    #     mail.select(folder)
    # except Exception as e:
    #     print(f"Failed to select folder '{folder}': {e}")
    #     return

    # result, data = mail.search(None, 'ALL')
    # email_ids = data[0].split()
    # print("---------------------------------gg "+str(data[0]))

    # emails = []

    # for email_id in email_ids:
    #     result, message_data = mail.fetch(email_id, '(RFC822)')
    #     raw_email = message_data[0][1]
    #     msg = email.message_from_bytes(raw_email)

    #     subject = decode_header(msg['subject'])[0][0]
    #     if isinstance(subject, bytes):
    #         subject = subject.decode()

    #     sender = msg['from']
    #     date = msg['date']
    #     body = ""

    #     if msg.is_multipart():
    #         for part in msg.walk():
    #             if part.get_content_type() == 'text/plain':
    #                 body = part.get_payload(decode=True).decode()
    #                 break
    #             elif part.get_content_type() == 'text/html':
    #                 html_body = part.get_payload(decode=True).decode()
    #                 soup = BeautifulSoup(html_body, 'html.parser')
    #                 body = soup.get_text()
    #     else:
    #         body = msg.get_payload(decode=True).decode()

    #     emails.append({
    #         'subject': subject,
    #         'sender': sender,
    #         'date': date,
    #         'body': body
    #     })

    # mail.logout()
    # return emails








def extract_reply_chain(mail, msg):
    reply_chain = []
    current_msg = msg
    
    while current_msg:
        body = get_email_body(current_msg)
        reply = extract_reply(body)
        reply_chain.append({
            'from': current_msg['From'],
            'date': current_msg['Date'],
            'reply': reply
        })
        
        in_reply_to = current_msg.get('In-Reply-To')
        if in_reply_to:
            next_msg_id = in_reply_to.strip('<>')
            status, next_msg_data = mail.search(None, f'HEADER Message-ID "{next_msg_id}"')
            if status != 'OK' or not next_msg_data[0]:
                break
            next_msg_id = next_msg_data[0].split()[-1]  # Get the latest email with the same Message-ID
            status, next_msg_data = mail.fetch(next_msg_id, "(RFC822)")
            if status != 'OK' or not next_msg_data:
                break
            next_msg = email.message_from_bytes(next_msg_data[0][1])
            current_msg = next_msg
        else:
            current_msg = None
    
    return reply_chain

def get_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))
            try:
                part_body = part.get_payload(decode=True).decode()
            except:
                part_body = ""
            if content_type == "text/plain" and "attachment" not in content_disposition:
                body += part_body
    else:
        body = msg.get_payload(decode=True).decode()
    return body

def extract_reply(body):
    lines = body.split('\n')
    reply_lines = []
    found_reply = False
    
    for line in reversed(lines):
        if line.startswith('>') or line.startswith('On ') and 'wrote:' in line:
            found_reply = True
            continue
        if found_reply:
            reply_lines.insert(0, line)
    
    return '\n'.join(reply_lines).strip()