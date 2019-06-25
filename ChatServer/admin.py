from django.contrib import admin
from ChatServer.models import *
# Register your models here.


class ChatKeyDisplay(admin.ModelAdmin):
    list_display = ('request', 'key')

admin.site.register(ChatKey, ChatKeyDisplay)
