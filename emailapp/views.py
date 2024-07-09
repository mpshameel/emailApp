from django.shortcuts import render
import re

from paramiko import Channel
from emailapp.models import channel, draftBox, draftBox_attachments, mailBox, mailBox_attachments, profile, sentBox, sentBox_attachments
from .utils import fetch_emailsTest, fetch_idEmail, fetch_inbox, extract_reply_chain, fetch_allMails, fetch_repliesEmail, fetch_sentEmail, fetch_draftEmail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChannelAssignSerializer, ChannelSerializer, EmailCredentialSerializer, EmailRequestSerializer, EmailSerializer, LoginSerializer, ProfileSerializer, ReplySerializer, UserSerializer, mailBoxSerializer, SuperUserSerializer

from rest_framework.decorators import api_view
from rest_framework import status
from django.utils.safestring import mark_safe
from django.utils.html import escape

from django.http import HttpResponse
from imap_tools import MailBox, A
from django.core.files.base import ContentFile

from django.core.management import call_command
# return HttpResponse("Some data")

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


def paginate_queryset(queryset, page_no, page_size=10):
    paginator = Paginator(queryset, page_size)
    try:
        page = paginator.page(page_no)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page

class EmailListView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = EmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            page_no = serializer.validated_data['page_no']
            email_credentials = serializer.validated_data['credentials']

            all_mailboxes = []
            for credential in email_credentials:
                email_id = credential['email_id']
                password = credential['password']

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
                paginated_mailboxes = paginate_queryset(mailboxes_with_empty_in_reply_to, page_no)
                serializer_mailBox = mailBoxSerializer(paginated_mailboxes, many=True)

                return Response(serializer_mailBox.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SentListView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = EmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            page_no = serializer.validated_data['page_no']
            email_credentials = serializer.validated_data['credentials']

            all_sentboxes = []
            for credential in email_credentials:
                email_id = credential['email_id']
                password = credential['password']
        
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
                        message_id_tuple = sent.headers.get('message-id')
                        message_id = message_id_tuple[0] if isinstance(message_id_tuple, tuple) else message_id_tuple
                        message_id = message_id.strip() if message_id else ''
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
                paginated_mailboxes = paginate_queryset(sent_with_empty_in_reply_to, page_no)
                serializer_mailBox = mailBoxSerializer(paginated_mailboxes, many=True)

                return Response(serializer_mailBox.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DraftsListView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = EmailRequestSerializer(data=request.data)
        if serializer.is_valid():
            page_no = serializer.validated_data['page_no']
            email_credentials = serializer.validated_data['credentials']

            all_draftboxes = []
            for credential in email_credentials:
                email_id = credential['email_id']
                password = credential['password']
        
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
                        message_id_tuple = draft.headers.get('message-id')
                        message_id = message_id_tuple[0] if isinstance(message_id_tuple, tuple) else message_id_tuple
                        message_id = message_id.strip() if message_id else ''
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
                paginated_mailboxes = paginate_queryset(draft_with_empty_in_reply_to, page_no)
                serializer_mailBox = mailBoxSerializer(paginated_mailboxes, many=True)
                return Response(serializer_mailBox.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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



#login api
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'token': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#create superuser api
class CreateSuperUser(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = SuperUserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            email = serializer.validated_data['email_id']
            channels = serializer.validated_data.get('channels', [])
        

            user_id = str(request.user.id)
            if not User.objects.filter(id=request.user.id, is_superuser=True).exists():
                return Response({'error': 'You have no permission to add Admins'}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_superuser(username=username, email=email, password=password)
            user.save()

            profiles = profile(username=user,usertype="ADMIN",createdBy=user_id)
            profiles.save()

            if channels:
                profiles.channel.set(channels) 
            return Response({'success': 'Superuser created successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#create user api
class CreateUser(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = SuperUserSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            email = serializer.validated_data['email_id']
            channels = serializer.validated_data.get('channels', [])


            user_id = str(request.user.id)
            
            if not User.objects.filter(id=request.user.id, is_superuser=True).exists():
                return Response({'error': 'You have no permission to add Users'}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()


            profiles = profile(username=user,usertype="USER",createdBy=user_id)
            profiles.save()

            if channels:
                profiles.channel.set(channels) 

            return Response({'success': 'User created successfully'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#channel get api
class ChannelListView(generics.ListAPIView):
    queryset = channel.objects.all()
    serializer_class = ChannelSerializer
    permission_classes = [IsAuthenticated]

#channel post api
class ChannelListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChannelSerializer(data=request.data)
        if serializer.is_valid():
            channel_name = serializer.validated_data['name']

            user_id = str(request.user.id)
            
            if not User.objects.filter(id=request.user.id, is_superuser=True).exists():
                return Response({'error': 'Permission denied'}, status=status.HTTP_400_BAD_REQUEST)
            if not channel_name:  # Check if the channel name is empty
                return Response({'error': 'Channel name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
            elif channel.objects.filter(name=channel_name).exists():
                return Response({'error': 'Channel already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
            channel(name=channel_name).save()
            return Response({'success': 'Channel created successfully'}, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#user list get api
class UserListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_superuser:
            profile_list = profile.objects.filter(username__is_superuser=False)
            serializer = ProfileSerializer(profile_list, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

class ProfileListView(generics.RetrieveAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return profile.objects.get(username=self.request.user)
    

#channel post api
class ChannelAssignUserView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChannelAssignSerializer(data=request.data)
        if serializer.is_valid():
            profile_id = serializer.validated_data['profile_id']
            channel_ids = serializer.validated_data.get('channel_ids', [])

            user_id = str(request.user.id)
            
            if not User.objects.filter(id=request.user.id, is_superuser=True).exists():
                return Response({'error': 'Permission denied'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                profileObj = profile.objects.get(id=profile_id.id)
                
                if channel_ids:
                    for channelId in channel_ids:
                        profileObj.channel.add(channelId)
                    profileObj.save()

                return Response({'success': 'Channels added successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)