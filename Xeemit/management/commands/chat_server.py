from django.utils import timezone
from django.core.management import BaseCommand
from Xeemit.models import *
from ChatServer.tasks import run_server


class Command(BaseCommand):
    help = "This initiates the relay server used for the chat module"

    def handle(self, *args, **options):
        run_server()
