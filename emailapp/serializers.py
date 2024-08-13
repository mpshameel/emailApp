import profile
from paramiko import Channel
from rest_framework import serializers
from .models import channel, mailBox, mailBox_attachments, mailboxBundle, profile
from django.contrib.auth.models import User

class EmailSerializer(serializers.Serializer):
    username = serializers.CharField()
    subject = serializers.CharField()
    from_ = serializers.CharField()  # Ensure this matches the Msg class attribute
    to = serializers.ListField(child=serializers.EmailField())
    date = serializers.CharField()
    text = serializers.CharField()
    html = serializers.CharField(allow_null=True, allow_blank=True)
    flags = serializers.ListField(child=serializers.CharField(), allow_null=True)
    cc = serializers.ListField(child=serializers.EmailField(), allow_null=True)
    bcc = serializers.ListField(child=serializers.EmailField(), allow_null=True)
    reply_to = serializers.ListField(child=serializers.EmailField(), allow_null=True)
    uid = serializers.CharField()
    headers = serializers.DictField()

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = mailBox_attachments
        fields = ['id', 'file', 'description', 'filename', 'file_url']

    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        return obj.file.url


class mailBoxSerializer(serializers.ModelSerializer):
    attachements = AttachmentSerializer(many=True, read_only=True)
    class Meta:
        model = mailBox
        fields = [
            'uid',
            'mailUsername',
            'subject',
            'fromMail',
            'to_mails',
            'date',
            'text',
            'html',
            'flags',
            'cc',
            'bcc',
            'reply_to',
            'messageId',
            'status',
            'assignedTo',
            'channel',
            'priority',
            'attachements',
            'in_reply_to'
        ]


class EmailCredentialSerializer(serializers.Serializer):
    email_id = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class EmailRequestSerializer(serializers.Serializer):
    page_no = serializers.IntegerField()
    credentials = serializers.ListField(child=EmailCredentialSerializer())

class EmailReplyRequestSerializer(serializers.Serializer):
    message_id = serializers.CharField(max_length=255)

class ListOrStringField(serializers.ListField):
    def to_internal_value(self, data):
        if isinstance(data, str):
            return [data]
        if isinstance(data, list):
            return [data]
        raise serializers.ValidationError("Invalid format for in_reply_to field.")

class ReplySerializer(serializers.Serializer):
    uid = serializers.CharField()
    mailUsername = serializers.CharField()
    subject = serializers.CharField()
    fromMail = serializers.EmailField()
    to_mails = serializers.ListField(
        child=serializers.EmailField()
    )
    date = serializers.DateTimeField()
    text = serializers.CharField()
    html = serializers.CharField()
    flags = serializers.ListField(
        child=serializers.CharField()
    )
    cc = serializers.ListField(
        child=serializers.EmailField(), required=False, default=[]
    )
    bcc = serializers.ListField(
        child=serializers.EmailField(), required=False, default=[]
    )
    reply_to = serializers.ListField(
        child=serializers.CharField(), required=False, default=[]
    )
    messageId = serializers.CharField()
    status = serializers.CharField()
    assignedTo = serializers.ListField(
        child=serializers.IntegerField()
    )
    channel = serializers.ListField(
        child=serializers.CharField(), required=False, default=[]
    )
    priority = serializers.CharField(required=False, allow_null=True)
    attachments = serializers.ListField(
        child=serializers.CharField(), required=False, source='attachements', default=[]
    )
    in_reply_to = serializers.ListField(
        child=serializers.CharField(), required=False, default=[]
    )

    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     # Remove backslashes before double quotes in 'html' field
    #     if 'html' in ret and isinstance(ret['html'], str):
    #         ret['html'] = ret['html'].replace('\\"', '"')
    #     return ret

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

class SuperUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email_id = serializers.EmailField()
    channels = serializers.PrimaryKeyRelatedField(queryset=channel.objects.all(), many=True, required=False)

class ChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = channel
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(source='username',read_only=True)
    channels = ChannelSerializer(source='channel', many=True)
    profile_id = serializers.SerializerMethodField()

    class Meta:
        model = profile
        fields = ['profile_id', 'phone', 'alternative_phone', 'dob', 'image', 'usertype','createdBy','channels','user']

    def get_profile_id(self, obj):
        return obj.id
    

class ChannelAssignSerializer(serializers.Serializer):
    profile_id = serializers.PrimaryKeyRelatedField(queryset=profile.objects.all(), many=False, required=False)
    channel_ids = serializers.PrimaryKeyRelatedField(queryset=channel.objects.all(), many=True, required=False)

class ChannelAssignRemoveSerializer(serializers.Serializer):
    profile_id = serializers.PrimaryKeyRelatedField(queryset=profile.objects.all(), many=False, required=False)
    channel_ids = serializers.PrimaryKeyRelatedField(queryset=channel.objects.all(), many=False, required=False)


class MailboxBundleSerializer(serializers.ModelSerializer):
    class Meta:
        model = mailboxBundle
        fields = ['id', 'email_id', 'password']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile
        fields = ['username', 'phone', 'image']

    def validate_username(self, value):
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("User not found")
        return value
    

class ProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile
        fields = ['phone', 'image']

class UpdateAssignedToSerializer(serializers.Serializer):
    action = serializers.CharField()
    uid = serializers.CharField()
    messageId = serializers.CharField()
    assignedTo = serializers.JSONField()

class PriorityChangeSerializer(serializers.Serializer):
    uid = serializers.CharField()
    messageId = serializers.CharField()
    priority = serializers.CharField()


class StatusChangeSerializer(serializers.Serializer):
    uid = serializers.CharField()
    messageId = serializers.CharField()
    status = serializers.CharField()