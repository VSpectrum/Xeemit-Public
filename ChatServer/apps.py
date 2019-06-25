from django.apps import AppConfig


class ChatServerConfig(AppConfig):
    name="ChatServer"

    def ready(self):
        print "Initializing Chat Server"
