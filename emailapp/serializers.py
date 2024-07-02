from rest_framework import serializers
from .models import mailBox, mailBox_attachments

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
            'aasignedTo',
            'channel',
            'priority',
            'attachements',
        ]

class ReplySerializer(serializers.Serializer):
    class Meta:
        uid = serializers.CharField(max_length=255)
        mailUsername = serializers.CharField(max_length=255)
        subject = serializers.CharField(max_length=255)
        fromMail = serializers.EmailField()
        to_mails = serializers.ListField(child=serializers.EmailField())
        date = serializers.DateTimeField()
        text = serializers.CharField()
        html = serializers.CharField()
        flags = serializers.ListField(child=serializers.CharField())
        cc = serializers.ListField(child=serializers.EmailField(), required=False, allow_null=True)
        bcc = serializers.ListField(child=serializers.EmailField(), required=False, allow_null=True)
        reply_to = serializers.CharField(max_length=255, required=False, allow_null=True)
        messageId = serializers.CharField(max_length=255)
        status = serializers.CharField(max_length=255)
        assignedTo = serializers.CharField(max_length=255)
        channel = serializers.CharField(max_length=255)
        priority = serializers.CharField(max_length=255)

    # def to_representation(self, instance):
    #     ret = super().to_representation(instance)
    #     # Remove backslashes before double quotes in 'html' field
    #     if 'html' in ret and isinstance(ret['html'], str):
    #         ret['html'] = ret['html'].replace('\\"', '"')
    #     return ret