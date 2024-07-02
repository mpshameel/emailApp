from imap_tools import MailBox, MailboxFolderSelectError
from email.header import decode_header
import json
from imap_tools import MailBox

email_id = "fairoozfs2024@gmail.com"
password = "xydhzuosvwnzeplp"
# Get date, subject and body len of all emails from INBOX folder
with MailBox('imap.gmail.com').login('fairoozfs2024@gmail.com', 'xydhzuosvwnzeplp') as mailbox:
    try:
        # Try to select the correct folder for "Sent Mail"
        mailbox.folder.set('[Gmail]/Sent Mail')
        # Get the selected folder
        current_folder = mailbox.folder.get()
        print(current_folder + "00000000000")
        
        # Fetch emails from the selected folder
        for msg in mailbox.fetch():
            email_dict = email_to_dict(msg) # type: ignore
            json_string = json.dumps(email_dict, indent=4)
            print("---------------------------ggg" + json_string)
            # print(msg.subject,msg.text+"replies")
    except MailboxFolderSelectError:
        print("The folder does not exist.")
        # print(msg.date, msg.subject, len(msg.text or msg.html),msg.text)
    # mailbox.move("14918","Drafts")