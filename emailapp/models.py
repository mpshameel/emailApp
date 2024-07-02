from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class mailBox_attachments(models.Model):
    file = models.FileField(upload_to='emailAttachments/')
    description = models.CharField(max_length=255, blank=True)
    filename = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.filename


class mailBox(models.Model):
    # username = models.ForeignKey(User,on_delete=models.CASCADE)
    uid = models.CharField(max_length=100,null=True,blank=True)
    mailUsername = models.CharField(max_length=100,null=True,blank=True)
    subject = models.CharField(max_length=100,null=True,blank=True)
    fromMail = models.CharField(max_length=100,null=True,blank=True)
    to_mails = models.JSONField(default=list, blank=True,null=True)
    date = models.CharField(max_length=100,null=True,blank=True)
    text = models.CharField(max_length=100,null=True,blank=True)
    html = models.CharField(max_length=100,null=True,blank=True)
    flags = models.JSONField(default=list, blank=True,null=True)
    cc = models.CharField(max_length=100,null=True,blank=True)
    bcc = models.CharField(max_length=100,null=True,blank=True)
    reply_to = models.CharField(max_length=100,null=True,blank=True)
    messageId = models.CharField(max_length=100,null=True,blank=True)
    attachements = models.ManyToManyField(mailBox_attachments, blank=True)
    in_reply_to = models.JSONField(default=list, blank=True) 
    references = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,default="open")
    is_deleted = models.BooleanField(default=False,blank=False,null=False,editable=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    aasignedTo = models.CharField(max_length=100,null=True,blank=True,default="")
    channel = models.CharField(max_length=100,null=True,blank=True,default="")
    priority = models.CharField(max_length=100,null=True,blank=True,default="")

    def save(self, *args, **kwargs):
        if self.in_reply_to is None:
            self.in_reply_to = []
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject


class sentBox_attachments(models.Model):
    file = models.FileField(upload_to='sendAttachments/')
    description = models.CharField(max_length=255, blank=True)
    filename = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.filename


class sentBox(models.Model):
    # username = models.ForeignKey(User,on_delete=models.CASCADE)
    uid = models.CharField(max_length=100,null=True,blank=True)
    mailUsername = models.CharField(max_length=100,null=True,blank=True)
    subject = models.CharField(max_length=100,null=True,blank=True)
    fromMail = models.CharField(max_length=100,null=True,blank=True)
    to_mails = models.JSONField(default=list, blank=True,null=True)
    date = models.CharField(max_length=100,null=True,blank=True)
    text = models.CharField(max_length=100,null=True,blank=True)
    html = models.CharField(max_length=100,null=True,blank=True)
    flags = models.JSONField(default=list, blank=True,null=True)
    cc = models.CharField(max_length=100,null=True,blank=True)
    bcc = models.CharField(max_length=100,null=True,blank=True)
    reply_to = models.CharField(max_length=100,null=True,blank=True)
    messageId = models.CharField(max_length=100,null=True,blank=True)
    attachements = models.ManyToManyField(sentBox_attachments, blank=True)
    in_reply_to = models.JSONField(default=list, blank=True) 
    references = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,default="open")
    is_deleted = models.BooleanField(default=False,blank=False,null=False,editable=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    aasignedTo = models.CharField(max_length=100,null=True,blank=True,default="")
    channel = models.CharField(max_length=100,null=True,blank=True,default="")
    priority = models.CharField(max_length=100,null=True,blank=True,default="")


    def save(self, *args, **kwargs):
        if self.in_reply_to is None:
            self.in_reply_to = []
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject


class draftBox_attachments(models.Model):
    file = models.FileField(upload_to='draftAttachments/')
    description = models.CharField(max_length=255, blank=True)
    filename = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.filename


class draftBox(models.Model):
    # username = models.ForeignKey(User,on_delete=models.CASCADE)
    uid = models.CharField(max_length=100,null=True,blank=True)
    mailUsername = models.CharField(max_length=100,null=True,blank=True)
    subject = models.CharField(max_length=100,null=True,blank=True)
    fromMail = models.CharField(max_length=100,null=True,blank=True)
    to_mails = models.JSONField(default=list, blank=True,null=True)
    date = models.CharField(max_length=100,null=True,blank=True)
    text = models.CharField(max_length=100,null=True,blank=True)
    html = models.CharField(max_length=100,null=True,blank=True)
    flags = models.JSONField(default=list, blank=True,null=True)
    cc = models.CharField(max_length=100,null=True,blank=True)
    bcc = models.CharField(max_length=100,null=True,blank=True)
    reply_to = models.CharField(max_length=100,null=True,blank=True)
    messageId = models.CharField(max_length=100,null=True,blank=True)
    attachements = models.ManyToManyField(draftBox_attachments, blank=True)
    in_reply_to = models.JSONField(default=list, blank=True) 
    references = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,default="open")
    is_deleted = models.BooleanField(default=False,blank=False,null=False,editable=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    aasignedTo = models.CharField(max_length=100,null=True,blank=True,default="")
    channel = models.CharField(max_length=100,null=True,blank=True,default="")
    priority = models.CharField(max_length=100,null=True,blank=True,default="")


    def save(self, *args, **kwargs):
        if self.in_reply_to is None:
            self.in_reply_to = []
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject