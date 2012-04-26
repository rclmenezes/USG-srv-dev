from django.core.management.base import BaseCommand, CommandError
from tigerapps.rooms.models import *

class Command(BaseCommand):
    args = '<no args right now>'
    help = 'Resets room availability (for now, make all available)'

    def handle(self, *args, **options):
        self.stdout.write('Marking all rooms available\n')
        Room.objects.all().update(avail=True)
        self.stdout.write('Done\n')
