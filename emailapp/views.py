from django.shortcuts import render
import re
from emailapp.models import draftBox, draftBox_attachments, mailBox, mailBox_attachments, sentBox, sentBox_attachments
from .utils import fetch_emailsTest, fetch_idEmail, fetch_inbox, extract_reply_chain, fetch_allMails, fetch_repliesEmail, fetch_sentEmail, fetch_draftEmail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import EmailSerializer, ReplySerializer, mailBoxSerializer

from rest_framework.decorators import api_view
from rest_framework import status
from django.utils.safestring import mark_safe
from django.utils.html import escape

from django.http import HttpResponse
from imap_tools import MailBox, A
from django.core.files.base import ContentFile

from django.core.management import call_command
# return HttpResponse("Some data")

class EmailListView(APIView):

    def get(self, request):
        email_id = "fairoozfs2024@gmail.com"
        password = "xydhzuosvwnzeplp"

        # fetch_emailsTest(email_id,password)
        emails = fetch_inbox(email_id, password)
        # print("Fetched Emails:", str(emails[0].html) )
        for email in emails:
            print("Email Type:", type(email)) 
        serializer = EmailSerializer(emails, many=True)
        # print("Serialized Data:", serializer.data)

        for mail in emails:
            existCheck = mailBox.objects.filter(uid=mail.uid)
            # mailBox.objects.all().delete()

            if existCheck:
                print("00000"+str(mail.headers))
                pass
            else:
                message_id = str(mail.headers['Message-ID'])
                inReplyTo = mail.headers.get('In-Reply-To')
                print("------------------------1"+str(inReplyTo))
                if inReplyTo is None:
                    inReplyTo = []
                mailbox = mailBox(
                    uid=mail.uid,
                    mailUsername=mail.username,
                    subject=mail.subject,
                    fromMail=mail.from_,
                    to_mails=mail.to,
                    date=mail.date,
                    text=mail.text,
                    html=mail.html,
                    flags=mail.flags,
                    cc=mail.cc,
                    bcc=mail.bcc,
                    reply_to=mail.reply_to,
                    messageId=message_id,
                    in_reply_to = inReplyTo

                )
                mailbox.save()

                if len(mail.attachments) > 0:
                    for attachment_data in mail.attachments:
                        # Extract file content and metadata
                        file_content = attachment_data['payload']
                        filename = attachment_data['filename']
                        content_type = attachment_data['content_type']

                        # Create and save the attachment
                        attachment = mailBox_attachments()
                        attachment.file.save(filename, ContentFile(file_content))
                        attachment.filename = filename
                        attachment.save()

                        # Associate the attachment with the mailbox instance
                        mailbox.attachements.add(attachment)
                mailbox.save()
                
            # Query the mailBox objects from the database and serialize them 
        mailboxes_with_empty_in_reply_to = mailBox.objects.filter(in_reply_to=[])
        serializer_mailBox = mailBoxSerializer(mailboxes_with_empty_in_reply_to, many=True)

        return Response(serializer_mailBox.data, status=status.HTTP_200_OK)

class SentListView(APIView):
    def get(self, request):
        email_id = "fairoozfs2024@gmail.com"
        password = "xydhzuosvwnzeplp"
        
        sents = fetch_sentEmail(email_id, password)
        print("geted Data Data:", str(sents))

        serializer = EmailSerializer(sents, many=True)
        print("Serialized Data:", serializer.data)

        for sent in sents:
            existCheck = sentBox.objects.filter(uid=sent.uid)
            # sentBox.objects.all().delete()
            if existCheck:
                pass
            else:
                message_id = str(sent.headers.get('Message-ID'))
                header = str(sent.headers)
                inReplyTo = sent.headers.get('in-reply-to')
                if inReplyTo is None:
                    inReplyTo = []
                
                sendboxes = sentBox(
                    uid=sent.uid,
                    mailUsername=sent.username,
                    subject=sent.subject,
                    fromMail=sent.from_,
                    to_mails=sent.to,
                    date=sent.date,
                    text=sent.text,
                    html=sent.html,
                    flags=sent.flags,
                    cc=sent.cc,
                    bcc=sent.bcc,
                    reply_to=sent.reply_to,
                    messageId=message_id,
                    in_reply_to = inReplyTo
                )
                sendboxes.save()

                if len(sent.attachments) > 0:
                    for attachment_data in sent.attachments:

                        # Extract file content and metadata
                        file_content = attachment_data['payload']
                        filename = attachment_data['filename']
                        content_type = attachment_data['content_type']

                        # Create and save the attachment
                        attachment = sentBox_attachments()
                        attachment.file.save(filename, ContentFile(file_content))
                        attachment.filename = filename
                        attachment.save()

                        # Associate the attachment with the mailbox instance
                        sendboxes.attachements.add(attachment)
                sendboxes.save()

        # Query the mailBox objects from the database and serialize them 
        sent_with_empty_in_reply_to = sentBox.objects.filter(in_reply_to=[])
        serializer_mailBox = mailBoxSerializer(sent_with_empty_in_reply_to, many=True)

        return Response(serializer_mailBox.data, status=status.HTTP_200_OK)


class DraftsListView(APIView):
    def get(self, request):
        email_id = "fairoozfs2024@gmail.com"
        password = "xydhzuosvwnzeplp"
        
        drafts = fetch_draftEmail(email_id, password)
        print("geted Data Data:", str(drafts))

        serializer = EmailSerializer(drafts, many=True)
        print("Serialized Data:", serializer.data)

        for draft in drafts:
            existCheck = draftBox.objects.filter(uid=draft.uid)
            # draftBox.objects.all().delete()

            if existCheck:
                pass
            else:
                message_id = str(draft.headers.get('Message-ID'))
                header = str(draft.headers)
                inReplyTo = draft.headers.get('in-reply-to')
                # if inReplyTo is None:
                inReplyTo = []
                
                draftBoxes = draftBox(
                    uid=draft.uid,
                    mailUsername=draft.username,
                    subject=draft.subject,
                    fromMail=draft.from_,
                    to_mails=draft.to,
                    date=draft.date,
                    text=draft.text,
                    html=draft.html,
                    flags=draft.flags,
                    cc=draft.cc,
                    bcc=draft.bcc,
                    reply_to=draft.reply_to,
                    messageId=message_id,
                    in_reply_to = inReplyTo
                )

                draftBoxes.save()

                if len(draft.attachments) > 0:
                    for attachment_data in draft.attachments:

                        # Extract file content and metadata
                        file_content = attachment_data['payload']
                        filename = attachment_data['filename']
                        content_type = attachment_data['content_type']

                        # Create and save the attachment
                        attachment = draftBox_attachments()
                        attachment.file.save(filename, ContentFile(file_content))
                        attachment.filename = filename
                        attachment.save()

                        # Associate the attachment with the mailbox instance
                        draftBoxes.attachements.add(attachment)
                draftBoxes.save()

        # Query the mailBox objects from the database and serialize them 
        draft_with_empty_in_reply_to = draftBox.objects.filter(in_reply_to=[])
        serializer_mailBox = mailBoxSerializer(draft_with_empty_in_reply_to, many=True)
        return Response(serializer_mailBox.data, status=status.HTTP_200_OK)
    

class EmailRepliesView(APIView):
    def get(self, request, format=None):
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

        email_id = "fairoozfs2024@gmail.com"
        password = "xydhzuosvwnzeplp"
        messageId = "<CAMe7ZKJWuamE8Q7WMWqZTP4rKgPFNjmOTd2cG4urQRmbESjCOw@mail.gmail.com>"
        
        # ------------------------------------
        # messageId = "('<CAMe7ZKJWuamE8Q7WMWqZTP4rKgPFNjmOTd2cG4urQRmbESjCOw@mail.gmail.com>')"

        # allMails = fetch_allMails(email_id, password)

        # allReplies = []

        # masterEmail = fetch_idEmail(allMails,messageId)
        # allReplies.extend(masterEmail)
        # while messageId:
        #     message_id, replies = fetch_repliesEmail(allMails, messageId)
        #     if replies:
        #         allReplies.extend(replies)
        #     messageId = message_id
        #     if not message_id:
        #         break

        # for reply in allReplies:
        #     print(f"Reply from------------ {reply.from_}: {reply.subject} {reply.username}")

        # serializer_detailMailReplies = mailBoxSerializer(allReplies, many=True)
        # return Response(serializer_detailMailReplies.data, status=status.HTTP_200_OK)
        # ---------------------------------------------

        masterMail = mailBox.objects.all()
        sentbox = sentBox.objects.all()
        draftbox = draftBox.objects.all()


        serializer_mailBox = mailBoxSerializer(masterMail, many=True)
        serializer_sentBox = mailBoxSerializer(sentbox, many=True)
        serializer_draftBox = mailBoxSerializer(draftbox, many=True)

        allMails = serializer_mailBox.data + serializer_sentBox.data + serializer_draftBox.data

        allReplies = []
        masterMail = [email for email in allMails if email.get('messageId') == messageId]
        allReplies.extend(masterMail)

        while messageId:
            replies = [email for email in allMails if email.get('in_reply_to') == messageId]
            # print("---------------------cc"+str(replies))
            if replies:
                allReplies.extend(replies)

            messageId = replies['in-reply-to']
            message_id= messageId
            if not message_id:
                break





        # print("---------------------cc"+str(allReplies))

                
        serializer_detailMailReplies = mailBoxSerializer(allMails, many=True)
        return Response(serializer_detailMailReplies.data, status=status.HTTP_200_OK)


