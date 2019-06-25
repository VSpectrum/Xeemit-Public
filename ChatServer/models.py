from django.db import models
from Xeemit.models import UserProfile as User, Request
from django.utils import timezone as datetime


class RequestChat(models.Model):
    messageID = models.AutoField(primary_key=True)
    request = models.ForeignKey(Request)
    fromUser = models.ForeignKey(User, related_name='from_user')
    toUser = models.ForeignKey(User, related_name='to_user')
    message = models.CharField(max_length=2000)
    statusRead = models.BooleanField(default=False)
    dateCreated = models.DateTimeField(default=datetime.now, blank=False)

    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'

    def __str__(self):
        return str(self.messageID)


class ChatKey(models.Model):
    request = models.OneToOneField(Request)
    key = models.CharField(max_length=60)

    class Meta:
        verbose_name = 'Chat Key'
        verbose_name_plural = 'Chat Keys'

    def __str__(self):
        return str(self.key)
