from django.core.management.base import BaseCommand
from movies.models import Movie
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Fix metadata_json cached_poster_path for all movies'

    def handle(self, *args, **options):
        fixed = 0
        for movie in Movie.objects.all():
            metadata = movie.metadata_json or {}
            poster_url = metadata.get('poster_path')
            if not poster_url:
                continue
            # Generate expected cache filename
            import hashlib
            from urllib.parse import urlparse
            url_hash = hashlib.md5(poster_url.encode()).hexdigest()
            clean_title = "".join(c for c in movie.movie_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_title = clean_title.replace(' ', '_')[:50]
            found = False
            for ext in ['.jpg', '.png', '.jpeg']:
                filename = f"{clean_title}_{url_hash}{ext}"
                cache_path = os.path.join(settings.MEDIA_ROOT, 'cache', filename)
                if os.path.exists(cache_path):
                    # Store forward-slash relative path like 'cache/filename.ext'
                    metadata['cached_poster_path'] = ('cache/' + filename).replace('\\', '/')
                    movie.metadata_json = metadata
                    movie.save()
                    fixed += 1
                    found = True
                    break
            if not found:
                self.stdout.write(self.style.WARNING(f"Poster not found for: {movie.movie_name}"))
        self.stdout.write(self.style.SUCCESS(f"Fixed cached_poster_path for {fixed} movies."))
