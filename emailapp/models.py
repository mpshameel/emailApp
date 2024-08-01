from django.db import models
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



class channel(models.Model):
    name = models.CharField(max_length=100,null=True,blank=True)

class profile(models.Model):
    username = models.ForeignKey(User,on_delete=models.CASCADE)
    phone = models.BigIntegerField(null=True, blank=True)
    alternative_phone = models.CharField(max_length=100,null=False,blank=True)
    dob = models.CharField(max_length=100,null=False,blank=True)
    image = models.ImageField(upload_to='profile-pic',null=True,blank=True)
    usertype = models.CharField(max_length=100,null=False,blank=True)
    channel = models.ManyToManyField(channel, blank=True)
    createdBy = models.CharField(max_length=100,null=False,blank=True)
    
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
    cc = models.JSONField(default=list, blank=True,null=True)
    bcc = models.JSONField(default=list, blank=True,null=True)
    reply_to = models.CharField(max_length=100,null=True,blank=True)
    messageId = models.CharField(max_length=100,null=True,blank=True)
    attachements = models.ManyToManyField(mailBox_attachments, blank=True)
    in_reply_to = models.JSONField(default=list, blank=True) 
    references = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,default="open")
    is_deleted = models.BooleanField(default=False,blank=False,null=False,editable=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    assignedTo = models.ManyToManyField(profile, blank=True)
    channel = models.JSONField(default=list, blank=True,null=True)
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
    cc = models.JSONField(default=list, blank=True,null=True)
    bcc = models.JSONField(default=list, blank=True,null=True)
    reply_to = models.CharField(max_length=100,null=True,blank=True)
    messageId = models.CharField(max_length=100,null=True,blank=True)
    attachements = models.ManyToManyField(sentBox_attachments, blank=True)
    in_reply_to = models.JSONField(default=list, blank=True) 
    references = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,default="open")
    is_deleted = models.BooleanField(default=False,blank=False,null=False,editable=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    assignedTo = models.ManyToManyField(profile, blank=True)
    channel = models.JSONField(default=list, blank=True,null=True)
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
    cc = models.JSONField(default=list, blank=True,null=True)
    bcc = models.JSONField(default=list, blank=True,null=True)
    reply_to = models.CharField(max_length=100,null=True,blank=True)
    messageId = models.CharField(max_length=100,null=True,blank=True)
    attachements = models.ManyToManyField(draftBox_attachments, blank=True)
    in_reply_to = models.JSONField(default=list, blank=True) 
    references = models.CharField(max_length=100,null=True,blank=True)
    status = models.CharField(max_length=100,default="open")
    is_deleted = models.BooleanField(default=False,blank=False,null=False,editable=True)
    created_at = models.DateTimeField(auto_now_add=True,blank=True, null=True)
    assignedTo = models.ManyToManyField(profile, blank=True)
    channel = models.JSONField(default=list, blank=True,null=True)
    priority = models.CharField(max_length=100,null=True,blank=True,default="")


    def save(self, *args, **kwargs):
        if self.in_reply_to is None:
            self.in_reply_to = []
        super().save(*args, **kwargs)

    def __str__(self):
        return self.subject
    

class mailboxBundle(models.Model):
    # username = models.ForeignKey(User,on_delete=models.CASCADE)
    email_id = models.CharField(max_length=100,null=True,blank=True)
    password = models.CharField(max_length=100,null=True,blank=True)