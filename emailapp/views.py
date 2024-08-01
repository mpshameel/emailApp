from django.shortcuts import get_object_or_404, render
import re

from paramiko import Channel
from emailapp.models import channel, draftBox, draftBox_attachments, mailBox, mailBox_attachments, mailboxBundle, profile, sentBox, sentBox_attachments
from .utils import fetch_emailsTest, fetch_idEmail, fetch_inbox, extract_reply_chain, fetch_allMails, fetch_repliesEmail, fetch_sentEmail, fetch_draftEmail
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChannelAssignRemoveSerializer, ChannelAssignSerializer, ChannelSerializer, EmailCredentialSerializer, EmailRequestSerializer, EmailSerializer, LoginSerializer, MailboxBundleSerializer, PriorityChangeSerializer, ProfileSerializer, ProfileUpdateSerializer, ReplySerializer, StatusChangeSerializer, UpdateAssignedToSerializer, UserSerializer, mailBoxSerializer, SuperUserSerializer, EmailReplyRequestSerializer

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
from django.core.serializers import serialize


def paginate_queryset(queryset, page_no, page_size=100):
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
                        inReplyTo = mail.headers.get('In-Reply-To')
                        print("---------------------------1"+str(inReplyTo))
                        pass
                    else:
                        message_id = str(mail.headers['Message-ID'])
                        inReplyTo = mail.headers.get('In-Reply-To')
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

                # mailboxes_with_empty_in_reply_to = mailBox.objects.filter(in_reply_to=[])
                # paginated_mailboxes = paginate_queryset(mailboxes_with_empty_in_reply_to, page_no)
                allMailboxes = mailBox.objects.all()
                paginated_mailboxes = paginate_queryset(allMailboxes, page_no)
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

                # sent_with_empty_in_reply_to = sentBox.objects.filter(in_reply_to=[])
                # paginated_mailboxes = paginate_queryset(sent_with_empty_in_reply_to, page_no)

                allSentMails = sentBox.objects.all()
                paginated_mailboxes = paginate_queryset(allSentMails, page_no)
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
                        if inReplyTo is None:
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

                # draft_with_empty_in_reply_to = draftBox.objects.filter(in_reply_to=[])
                # paginated_mailboxes = paginate_queryset(draft_with_empty_in_reply_to, page_no)

                allDraftMails = draftBox.objects.all()
                paginated_mailboxes = paginate_queryset(allDraftMails, page_no)
                serializer_mailBox = mailBoxSerializer(paginated_mailboxes, many=True)
                return Response(serializer_mailBox.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class EmailRepliesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EmailReplyRequestSerializer(data=request.data)
        if serializer.is_valid():
            messageId = serializer.validated_data['message_id']
            current_message_id = messageId

            allReplies = []

            inboxMails = mailBox.objects.all()
            sentboxMails = sentBox.objects.all()
            draftboxMails = draftBox.objects.all()

            serializer_mailBox = mailBoxSerializer(inboxMails, many=True)
            serializer_sentBox = mailBoxSerializer(sentboxMails, many=True)
            serializer_draftBox = mailBoxSerializer(draftboxMails, many=True)

            allMails = serializer_mailBox.data + serializer_sentBox.data + serializer_draftBox.data

            # print("---------------"+str(allMails))

            masterMail = [email for email in allMails if email.get('messageId') == messageId]

            print("----------------------------aaaaa"+str(masterMail))
            allReplies = []


            def find_replies(current_message_id, allMails, visited_ids=None):

                if visited_ids is None:
                    visited_ids = set()



                if current_message_id in visited_ids:
                    return allReplies

                visited_ids.add(current_message_id)

                for email in allMails:

                    in_reply_to = email.get('in_reply_to')

                    if not isinstance(in_reply_to, list):
                        if current_message_id == in_reply_to:
                            allReplies.append(email)
                            current_message_id = email.get('messageId')
                            if current_message_id is not None:
                                find_replies(email.get('messageId'), allMails, visited_ids)
                            else:
                                break

                    if current_message_id in in_reply_to:
                        allReplies.append(email)
                        current_message_id = email.get('messageId')

                        if current_message_id is not None:
                            find_replies(email.get('messageId'), allMails, visited_ids)
                        else:
                            break
                        
                return allReplies
            
            allReplies = find_replies(messageId, allMails)
            uniqueReplies = list({email['messageId']: email for email in allReplies}.values())
            allReplies = masterMail.__add__(uniqueReplies)
            print("----------------------------bbbb"+str(allReplies))


            # while current_message_id:
            #     found_replies = False
            #     email_matched = False  # Flag to break out of nested loop and continue with the next while iteration

            #     for email in allMails:
            #         in_reply_to = email.get('in_reply_to')
            #         if in_reply_to is None or (isinstance(in_reply_to, list) and not in_reply_to):
            #             continue

            #         if isinstance(in_reply_to, list):
            #             for element in in_reply_to:
            #                 if element == current_message_id:
            #                     allReplies.append(email)
            #                     found_replies = True
            #                     current_message_id = email.get('message_id')  # Update to the message_id of the current email
            #                     email_matched = True  # Set flag to True to indicate an email match
            #                     print("-------------------fff" + str(allReplies))
            #                     print("-------------------bbbb" + str(current_message_id))
            #                     break  # Break the inner loop

            #         if email_matched:
            #             break  # Break the outer loop if an email matched

            #     if not found_replies:
            #         break


            
                # for email in allMails:
                #     if isinstance(email.get('in_reply_to'), list):
                #         if any(element == current_message_id for element in email['in_reply_to']):
                #             allReplies.append(email)
                #             current_message_id = email.get('in_reply_to')



                    # messageId = replies['In_Reply_To']
                    # message_id= messageId
                    # if not message_id:
                    #     break

                
            serializer_detailMailReplies = mailBoxSerializer(allReplies, many=True)
            return Response(serializer_detailMailReplies.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    




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
    

#edit user api
class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            # Get the currently authenticated user
            user = request.user
            
            # Fetch the profile associated with the user
            profile_id = profile.objects.get(username=user)
        except profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileUpdateSerializer(profile_id, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'Profile updated successfully'}, status=status.HTTP_200_OK)
        
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
    
#edit user api
class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            # Get the currently authenticated user
            user = request.user
            
            # Fetch the profile associated with the user
            profile_id = profile.objects.get(username=user)
        except profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProfileUpdateSerializer(profile_id, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': 'Profile updated successfully'}, status=status.HTTP_200_OK)
        
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
    
#edit user api
class UpdateChannel(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        # Check if the user is a superuser
        if not request.user.is_superuser:
            return Response({'error': 'You have no permission to update this channel'}, status=status.HTTP_403_FORBIDDEN)

        # Get channel data from request
        channel_id = request.data.get('id')
        channel_name = request.data.get('channel')

        try:
            # Fetch the channel to be updated
            channel_instance = channel.objects.get(id=channel_id)
        except channel.DoesNotExist:
            return Response({'error': 'Channel not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update the channel name
        channel_instance.name = channel_name
        channel_instance.save()

        return Response({'success': 'Channel updated successfully'}, status=status.HTTP_200_OK)
    
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

                return Response({'success': 'Channels assigned successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#channel post api
class ChannelRemoveUserView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChannelAssignRemoveSerializer(data=request.data)
        if serializer.is_valid():
            profile_id = serializer.validated_data['profile_id']
            channel_id = serializer.validated_data['channel_ids']

            user_id = str(request.user.id)
            
            if not User.objects.filter(id=request.user.id, is_superuser=True).exists():
                return Response({'error': 'Permission denied'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                profileObj = profile.objects.get(id=profile_id.id)
                
                if channel_id:
                    profileObj.channel.remove(channel_id)
                    profileObj.save()

                return Response({'success': 'Channels removed successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#channel get api
class MailBoxBundleListView(generics.ListAPIView):
    queryset = mailboxBundle.objects.all()
    serializer_class = MailboxBundleSerializer
    permission_classes = [IsAuthenticated]

#channel post api
class MailboxBundleCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = MailboxBundleSerializer(data=request.data)
        if serializer.is_valid():
            email_id = serializer.validated_data['email_id']
            password = serializer.validated_data['password']

            user_id = str(request.user.id)
            
            if not User.objects.filter(id=request.user.id, is_superuser=True).exists():
                return Response({'error': 'Permission denied'}, status=status.HTTP_400_BAD_REQUEST)
            if not email_id:  # Check if the channel name is empty
                return Response({'error': 'Channel name cannot be empty'}, status=status.HTTP_400_BAD_REQUEST)
            elif mailboxBundle.objects.filter(email_id=email_id).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)
        
            mailboxBundle(email_id=email_id,password=password).save()
            return Response({'success': 'Mailbox created successfully'}, status=status.HTTP_201_CREATED)
    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

#edit user api
class UpdateMailboxBundle(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        # Check if the user is a superuser
        if not request.user.is_superuser:
            return Response({'error': 'You have no permission to update this channel'}, status=status.HTTP_403_FORBIDDEN)

        # Get channel data from request
        mailbox_id = request.data.get('id')
        mailbox_email = request.data.get('email')
        mailbox_password = request.data.get('password')

        try:
            # Fetch the channel to be updated
            mailbox_instance = mailboxBundle.objects.get(id=mailbox_id)
        except channel.DoesNotExist:
            return Response({'error': 'Mailbox not found'}, status=status.HTTP_404_NOT_FOUND)

        # Update the channel name
        mailbox_instance.email_id = mailbox_email
        mailbox_instance.password = mailbox_password
        mailbox_instance.save()

        return Response({'success': 'Mailbox updated successfully'}, status=status.HTTP_200_OK)
    


class UpdateAssignedToView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UpdateAssignedToSerializer(data=request.data)
        
        if serializer.is_valid():
            action = serializer.validated_data['action']
            uid = serializer.validated_data['uid']
            messageId = serializer.validated_data['messageId']
            assignedTo = serializer.validated_data['assignedTo']

            # assign = profile.objects.get(id=assignedTo)
            assign = get_object_or_404(profile, id=assignedTo)
            
            if action == 'UPDATE':
                return self.update_assigned_to(uid, messageId, assign)
            elif action == 'DELETE':
                return self.delete_assigned_to(uid, messageId, assign)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_assigned_to(self, uid, messageId, assign):
        # Try to update in mailBox
        try:
            mailbox_instance = mailBox.objects.get(uid=uid, messageId=messageId)
            mailbox_instance.assignedTo.add(assign)
            mailbox_instance.save()

            return Response({'success': 'Mail assigned successfully in mailBox'}, status=status.HTTP_200_OK)
        except mailBox.DoesNotExist:
            pass
        
        # Try to update in sentBox
        try:
            sentbox_instance = sentBox.objects.get(uid=uid, messageId=messageId)
            sentbox_instance.assignedTo.add(assign)
            sentbox_instance.save()
            return Response({'success': 'Mail assigned successfullyin sentBox'}, status=status.HTTP_200_OK)
        except sentBox.DoesNotExist:
            pass
        
        # Try to update in draftBox
        try:
            draftbox_instance = draftBox.objects.get(uid=uid, messageId=messageId)
            draftbox_instance.assignedTo.add(assign)
            draftbox_instance.save()
            return Response({'success': 'Mail assigned successfully in draftBox'}, status=status.HTTP_200_OK)
        except draftBox.DoesNotExist:
            pass

        return Response({'error': 'No matching record found'}, status=status.HTTP_404_NOT_FOUND)

    def delete_assigned_to(self, uid, messageId, assign):
        # Try to delete in mailBox
        try:
            mailbox_instance = mailBox.objects.get(uid=uid, messageId=messageId)
            mailbox_instance.assignedTo.remove(assign)
            mailbox_instance.save()
            return Response({'success': 'Assign deleted successfully in mailBox'}, status=status.HTTP_200_OK)
        except mailBox.DoesNotExist:
            pass
        
        # Try to delete in sentBox
        try:
            sentbox_instance = sentBox.objects.get(uid=uid, messageId=messageId)
            sentbox_instance.assignedTo.remove(assign)
            sentbox_instance.save()
            return Response({'success': 'Assign deleted successfully in sentBox'}, status=status.HTTP_200_OK)
        except sentBox.DoesNotExist:
            pass
        
        # Try to delete in draftBox
        try:
            draftbox_instance = draftBox.objects.get(uid=uid, messageId=messageId)
            draftbox_instance.assignedTo.remove(assign)
            draftbox_instance.save()
            return Response({'success': 'Assign deleted successfully in draftBox'}, status=status.HTTP_200_OK)
        except draftBox.DoesNotExist:
            pass

        return Response({'error': 'No matching record found'}, status=status.HTTP_404_NOT_FOUND)
    

#priority change post api
class PriorityChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PriorityChangeSerializer(data=request.data)
        
        if serializer.is_valid():
            uid = serializer.validated_data['uid']
            messageId = serializer.validated_data['messageId']
            priority = serializer.validated_data['priority']

            return self.update_priority(uid, messageId,priority)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_priority(self, uid, messageId, priority):
        # Try to update in mailBox
        try:
            mailbox_instance = mailBox.objects.get(uid=uid, messageId=messageId)
            mailbox_instance.priority = priority
            mailbox_instance.save()

            return Response({'success': 'Mail priority changed successfully in mailBox'}, status=status.HTTP_200_OK)
        except mailBox.DoesNotExist:
            pass
        
        # Try to update in sentBox
        try:
            sentbox_instance = sentBox.objects.get(uid=uid, messageId=messageId)
            sentbox_instance.priority = priority
            sentbox_instance.save()
            return Response({'success': 'Mail priority changed successfully in sentBox'}, status=status.HTTP_200_OK)
        except sentBox.DoesNotExist:
            pass
        
        # Try to update in draftBox
        try:
            draftbox_instance = draftBox.objects.get(uid=uid, messageId=messageId)
            draftbox_instance.priority = priority
            draftbox_instance.save()
            return Response({'success': 'Mail priority changed successfully in draftBox'}, status=status.HTTP_200_OK)
        except draftBox.DoesNotExist:
            pass

        return Response({'error': 'No matching record found'}, status=status.HTTP_404_NOT_FOUND)
    

#priority change post api
class StatusChangeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = StatusChangeSerializer(data=request.data)
        
        if serializer.is_valid():
            uid = serializer.validated_data['uid']
            messageId = serializer.validated_data['messageId']
            statusValue = serializer.validated_data['status']

            return self.update_status(uid, messageId,statusValue)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update_status(self, uid, messageId, statusValue):
        # Try to update in mailBox
        try:
            mailbox_instance = mailBox.objects.get(uid=uid, messageId=messageId)
            mailbox_instance.status = statusValue
            mailbox_instance.save()

            return Response({'success': 'Mail status changed successfully in mailBox'}, status=status.HTTP_200_OK)
        except mailBox.DoesNotExist:
            pass
        
        # Try to update in sentBox
        try:
            sentbox_instance = sentBox.objects.get(uid=uid, messageId=messageId)
            sentbox_instance.status = statusValue
            sentbox_instance.save()
            return Response({'success': 'Mail status changed successfully in sentBox'}, status=status.HTTP_200_OK)
        except sentBox.DoesNotExist:
            pass
        
        # Try to update in draftBox
        try:
            draftbox_instance = draftBox.objects.get(uid=uid, messageId=messageId)
            draftbox_instance.status = statusValue
            draftbox_instance.save()
            return Response({'success': 'Mail status changed successfully in draftBox'}, status=status.HTTP_200_OK)
        except draftBox.DoesNotExist:
            pass

        return Response({'error': 'No matching record found'}, status=status.HTTP_404_NOT_FOUND)