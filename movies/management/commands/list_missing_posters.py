from django.core.management.base import BaseCommand
from movies.models import Movie
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'List movies with missing poster files in media/cache/'

    def handle(self, *args, **options):
        missing = []
        for movie in Movie.objects.all():
            poster_path = ''
            if movie.metadata_json:
                poster_path = movie.metadata_json.get('cached_poster_path', '')
            # Normalize to forward-slash relative path under MEDIA_ROOT
            poster_path = str(poster_path).replace('\\', '/').lstrip('/')
            if poster_path.startswith('media/'):
                poster_path = poster_path[len('media/'):]
            if poster_path and not os.path.exists(os.path.join(settings.MEDIA_ROOT, poster_path)):
                missing.append((movie.movie_name, poster_path))
        if missing:
            self.stdout.write(self.style.WARNING('Movies with missing poster files:'))
            for name, path in missing:
                self.stdout.write(f'- {name}: {path}')
        else:
            self.stdout.write(self.style.SUCCESS('All movies have poster files present.'))
