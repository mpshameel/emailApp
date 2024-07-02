import imaplib
import email
from email.header import decode_header

def connect_to_mailbox():
    # Connect to the server
    mail = imaplib.IMAP4_SSL("imap.server.com")
    mail.login("your_email@example.com", "password")
    mail.select("inbox")  # Connect to inbox
    return mail

def fetch_emails(mail):
    # Search for all emails in the mailbox
    status, messages = mail.search(None, "ALL")
    email_ids = messages[0].split()
    email_list = []

    for e_id in email_ids:
        status, msg_data = mail.fetch(e_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                email_list.append(parse_email(msg))
    return email_list

def parse_email(msg):
    # Extract the basic details
    parsed_email = {
        "uid": msg["Message-ID"],
        "subject": decode_header(msg["Subject"])[0][0],
        "from": msg["From"],
        "to": msg.get("To", "").split(", "),
        "cc": msg.get("Cc", "").split(", "),
        "bcc": msg.get("Bcc", "").split(", "),
        "reply_to": msg.get("Reply-To", "").split(", "),
        "date": msg["Date"],
        "in_reply_to": msg["In-Reply-To"],
        "references": msg.get("References", "").split(", "),
        "text": get_text(msg),
        "html": get_html(msg),
        "flags": [],  # Flags would be fetched from the server differently
        "headers": dict(msg.items()),
        "size": len(msg.as_bytes())
    }
    return parsed_email

def get_text(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()

def get_html(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()

mail = connect_to_mailbox()
emails = fetch_emails(mail)


def link_emails(emails):
    email_dict = {}
    for email in emails:
        email_dict[email["uid"]] = email

    threads = []
    for email in emails:
        if email["in_reply_to"]:
            parent = email_dict.get(email["in_reply_to"])
            if parent:
                parent.setdefault("replies", []).append(email)
        else:
            threads.append(email)

    return threads

email_threads = link_emails(emails)
