from django.core.management.base import BaseCommand, CommandError
from tigerapps.rooms.models import Draw, Building, Room, PastDraw, PastDrawEntry

class Command(BaseCommand):
    args = '<year stats_file.txt>'
    help = 'Imports draw statistics for rooms from a file for given year'

    def handle(self, *args, **options):
        year = int(args[0])
        statfile = args[1]
        # Create the past draws
        self.stdout.write('Creating past draws for year %d\n' % year);
        pastdraws = {}
        for draw in Draw.objects.all():
            try:
                pastdraws[draw.name] = PastDraw.objects.get(year=year, 
                                                            draw__name=draw.name)
            except:
                pastdraws[draw.name] = PastDraw(draw=draw, year=year, numrooms=0, 
                                                numpeople=0)
                pastdraws[draw.name].save()
        self.stdout.write('Draws Created\n')

        f = open(statfile)
        line = f.readline()
        while line:
            toks = line.strip().split(',')
            number = toks[0]
            bldgname = toks[1]
            occ = int(toks[2])
            draw = toks[3]
            sqft = int(toks[4])
            timestamp = int(toks[5])
            pastdraw = pastdraws[draw]
            # Create a new past draw entry if we have a matching room
            rooms = Room.objects.filter(building__name__iexact=bldgname, 
                                       number__iexact=number)
            if rooms:
                room = rooms[0]
                entry = PastDrawEntry(pastdraw=pastdraw, room=room,
                                      timestamp=timestamp, 
                                      roomrank=pastdraw.numrooms,
                                      peoplerank=pastdraw.numpeople)
                entry.save()
            else:
                self.stderr.write(line)
            
            # Track ranks within draw
            pastdraw.numrooms += 1
            pastdraw.numpeople += occ
            line = f.readline()
            
        self.stdout.write('Done\n')
        # for poll_id in args:
        #     try:
        #         poll = Poll.objects.get(pk=int(poll_id))
        #     except Poll.DoesNotExist:
        #         raise CommandError('Poll "%s" does not exist' % poll_id)

        #     poll.opened = False
        #     poll.save()

        #     self.stdout.write('Successfully closed poll "%s"\n' % poll_id)
