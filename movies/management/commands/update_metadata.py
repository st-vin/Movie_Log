from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from movies.models import Movie
from movies.services import MovieMetadataService
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update movie metadata from TMDb and OMDb APIs, or delete movies by selector'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Update metadata for all movies',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if metadata is recent',
        )
        parser.add_argument(
            '--movie-id',
            type=int,
            help='Update metadata for a specific movie ID',
        )
        parser.add_argument(
            '--title',
            type=str,
            help='Update metadata for movies matching this title',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=10,
            help='Limit number of movies to update (default: 10)',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete matched movies instead of updating (requires --title or --movie-id)',
        )
    
    def handle(self, *args, **options):
        service = MovieMetadataService()
        
        # Validate delete usage to prevent accidental mass deletions
        if options['delete']:
            if options.get('all'):
                raise CommandError("Refusing to delete all movies. Provide --title or --movie-id with --delete.")
            if not options.get('title') and not options.get('movie_id'):
                raise CommandError("When using --delete, you must provide --title or --movie-id.")
        
        # Determine which movies to update
        if options['movie_id']:
            try:
                movies = Movie.objects.filter(id=options['movie_id'])
                if not movies.exists():
                    raise CommandError(f"Movie with ID {options['movie_id']} not found")
            except Movie.DoesNotExist:
                raise CommandError(f"Movie with ID {options['movie_id']} not found")
        
        elif options['title']:
            movies = Movie.objects.filter(movie_name__icontains=options['title'])
            if not movies.exists():
                raise CommandError(f"No movies found matching title '{options['title']}'")
        
        elif options['all']:
            movies = Movie.objects.all()
        
        else:
            # Default: update movies that need refresh
            movies = Movie.objects.all()[:options['limit']]
        
        if not movies.exists():
            self.stdout.write(
                self.style.WARNING('No movies found to update' if not options['delete'] else 'No movies found to delete')
            )
            return
        
        # Deletion flow
        if options['delete']:
            count = movies.count()
            self.stdout.write(self.style.WARNING(f'Found {count} movie(s) to delete'))
            for movie in movies:
                self.stdout.write(f'  - {movie.movie_name} (ID: {movie.id})')
            deleted_count, _ = movies.delete()
            self.stdout.write(self.style.SUCCESS(f'Deleted {deleted_count} record(s)'))
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {movies.count()} movies to update')
        )
        
        updated_count = 0
        failed_count = 0
        
        for movie in movies:
            try:
                self.stdout.write(f'Updating: {movie.movie_name} ({movie.release_year})')
                
                # Check if update is needed (unless forced)
                if not options['force'] and not movie.needs_metadata_refresh():
                    self.stdout.write(
                        self.style.WARNING(f'  Skipping - metadata is recent')
                    )
                    continue
                
                # Update metadata
                service.update_movie_metadata(movie, force_refresh=options['force'])
                
                # Generate mood tags if metadata was updated
                if movie.metadata_json:
                    mood_tags = service.generate_mood_tags(movie.metadata_json)
                    if mood_tags:
                        movie.mood_tags = list(set(movie.mood_tags + mood_tags))
                        movie.save()
                
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Updated successfully')
                )
                
            except Exception as e:
                failed_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Failed: {str(e)}')
                )
                logger.error(f"Failed to update {movie.movie_name}: {e}")
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(f'Updated: {updated_count} movies')
        )
        if failed_count > 0:
            self.stdout.write(
                self.style.ERROR(f'Failed: {failed_count} movies')
            )
        self.stdout.write('='*50)

