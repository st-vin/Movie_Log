import os
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from typing import Dict, Optional
import logging
from urllib.parse import urlparse
import hashlib

from .tmdb_service import TMDbService
from .omdb_service import OMDbService

logger = logging.getLogger(__name__)


class MovieMetadataService:
    """Main service for fetching movie metadata with fallback support"""
    
    def __init__(self):
        self.tmdb_service = TMDbService()
        self.omdb_service = OMDbService()
        self.cache_dir = settings.CACHE_DIR
        
        # Ensure cache directory exists
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def fetch_metadata(self, title: str, director: Optional[str] = None, 
                      year: Optional[int] = None) -> Dict:
        """
        Fetch movie metadata using TMDb as primary source and OMDb as fallback
        """
        metadata = {}
        
        # Try TMDb first
        logger.info(f"Fetching metadata for '{title}' from TMDb")
        tmdb_data = self.tmdb_service.find_movie(title, year, director)
        
        if tmdb_data:
            metadata.update(tmdb_data)
            metadata['source'] = 'tmdb'
            logger.info(f"Successfully fetched metadata from TMDb for '{title}'")
        else:
            logger.warning(f"TMDb lookup failed for '{title}', trying OMDb")
            
            # Fallback to OMDb
            omdb_data = self.omdb_service.find_movie(title, year)
            if omdb_data:
                metadata.update(omdb_data)
                metadata['source'] = 'omdb'
                logger.info(f"Successfully fetched metadata from OMDb for '{title}'")
            else:
                logger.error(f"Both TMDb and OMDb lookups failed for '{title}'")
                metadata['source'] = 'none'
        
        # If we have TMDb data but missing some ratings, try to supplement with OMDb
        if metadata.get('source') == 'tmdb' and not metadata.get('imdb_rating'):
            logger.info(f"Supplementing TMDb data with OMDb ratings for '{title}'")
            omdb_data = self.omdb_service.find_movie(
                title, year, metadata.get('imdb_id')
            )
            if omdb_data:
                # Add missing ratings from OMDb
                if omdb_data.get('imdb_rating') and not metadata.get('imdb_rating'):
                    metadata['imdb_rating'] = omdb_data['imdb_rating']
                if omdb_data.get('rt_rating') and not metadata.get('rt_rating'):
                    metadata['rt_rating'] = omdb_data['rt_rating']
                if omdb_data.get('metacritic_rating') and not metadata.get('metacritic_rating'):
                    metadata['metacritic_rating'] = omdb_data['metacritic_rating']
                
                metadata['source'] = 'tmdb+omdb'
        
        return metadata
    
    def cache_poster_image(self, poster_url: str, movie_title: str) -> Optional[str]:
        """
        Download and cache a poster image locally
        Returns the local file path if successful
        """
        if not poster_url or poster_url == 'N/A':
            return None
        
        try:
            # Create a unique filename based on URL hash
            url_hash = hashlib.md5(poster_url.encode()).hexdigest()
            parsed_url = urlparse(poster_url)
            file_extension = os.path.splitext(parsed_url.path)[1] or '.jpg'
            
            # Clean movie title for filename
            clean_title = "".join(c for c in movie_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            clean_title = clean_title.replace(' ', '_')[:50]  # Limit length
            
            filename = f"{clean_title}_{url_hash}{file_extension}"
            cache_path = os.path.join(self.cache_dir, filename)
            
            # Check if already cached
            if os.path.exists(cache_path):
                logger.info(f"Poster already cached: {filename}")
                return cache_path
            
            # Download the image
            logger.info(f"Downloading poster from: {poster_url}")
            response = requests.get(poster_url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Save to cache directory
            with open(cache_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"Poster cached successfully: {filename}")
            return cache_path
            
        except Exception as e:
            logger.error(f"Failed to cache poster image: {e}")
            return None
    
    def get_cached_poster_path(self, poster_url: str, movie_title: str) -> Optional[str]:
        """
        Get the cached poster path if it exists, otherwise cache it
        """
        if not poster_url:
            return None
        
        # Generate the expected cache filename
        url_hash = hashlib.md5(poster_url.encode()).hexdigest()
        clean_title = "".join(c for c in movie_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        clean_title = clean_title.replace(' ', '_')[:50]
        
        # Try different extensions
        for ext in ['.jpg', '.png', '.jpeg']:
            filename = f"{clean_title}_{url_hash}{ext}"
            cache_path = os.path.join(self.cache_dir, filename)
            if os.path.exists(cache_path):
                return cache_path
        
        # If not cached, try to cache it now
        return self.cache_poster_image(poster_url, movie_title)
    
    def update_movie_metadata(self, movie_instance, force_refresh: bool = False):
        """
        Update a movie instance with fresh metadata
        """
        from ..models import Movie  # Import here to avoid circular imports
        
        # Check if refresh is needed
        if not force_refresh and not movie_instance.needs_metadata_refresh(
            settings.METADATA_REFRESH_DAYS
        ):
            logger.info(f"Metadata for '{movie_instance.movie_name}' is still fresh")
            return movie_instance
        
        logger.info(f"Updating metadata for '{movie_instance.movie_name}'")
        
        # Fetch fresh metadata
        metadata = self.fetch_metadata(
            movie_instance.movie_name,
            movie_instance.director,
            movie_instance.release_year
        )
        
        if metadata and metadata.get('source') != 'none':
            # Update the metadata_json field
            movie_instance.metadata_json = metadata
            
            # Cache poster image if available
            poster_url = metadata.get('poster_path')
            if poster_url:
                cached_path = self.cache_poster_image(poster_url, movie_instance.movie_name)
                if cached_path:
                    # Store relative path under MEDIA_ROOT, using forward slashes
                    relative_path = os.path.relpath(cached_path, settings.MEDIA_ROOT)
                    relative_path = relative_path.replace('\\', '/')
                    # Ensure it looks like 'cache/filename.ext'
                    if relative_path.startswith('media/'):
                        relative_path = relative_path[len('media/'):]
                    metadata['cached_poster_path'] = relative_path
                    movie_instance.metadata_json = metadata
            
            movie_instance.save()
            logger.info(f"Successfully updated metadata for '{movie_instance.movie_name}'")
        else:
            logger.warning(f"No metadata found for '{movie_instance.movie_name}'")
        
        return movie_instance
    
    def bulk_update_metadata(self, queryset, force_refresh: bool = False):
        """
        Update metadata for multiple movies
        """
        updated_count = 0
        for movie in queryset:
            try:
                self.update_movie_metadata(movie, force_refresh)
                updated_count += 1
            except Exception as e:
                logger.error(f"Failed to update metadata for '{movie.movie_name}': {e}")
        
        logger.info(f"Updated metadata for {updated_count} movies")
        return updated_count
    
    def generate_mood_tags(self, metadata: Dict) -> list:
        """
        Generate mood tags based on movie metadata
        This is a simple implementation - could be enhanced with AI/ML
        """
        mood_tags = []
        
        # Genre-based mood mapping
        genre_mood_map = {
            'Horror': ['scary', 'intense', 'dark'],
            'Comedy': ['funny', 'lighthearted', 'uplifting'],
            'Drama': ['emotional', 'thought-provoking', 'serious'],
            'Action': ['exciting', 'intense', 'adrenaline'],
            'Romance': ['romantic', 'heartwarming', 'emotional'],
            'Thriller': ['suspenseful', 'intense', 'edge-of-seat'],
            'Sci-Fi': ['futuristic', 'mind-bending', 'imaginative'],
            'Fantasy': ['magical', 'escapist', 'imaginative'],
            'Documentary': ['educational', 'informative', 'real'],
            'Animation': ['family-friendly', 'colorful', 'imaginative'],
            'Crime': ['gritty', 'dark', 'intense'],
            'Mystery': ['puzzling', 'suspenseful', 'intriguing'],
            'War': ['intense', 'dramatic', 'historical'],
            'Western': ['classic', 'adventurous', 'rugged'],
            'Musical': ['uplifting', 'entertaining', 'melodic']
        }
        
        # Add mood tags based on genres
        genres = metadata.get('genres', [])
        for genre in genres:
            if genre in genre_mood_map:
                mood_tags.extend(genre_mood_map[genre])
        
        # Rating-based moods
        rating = metadata.get('imdb_rating')
        if rating:
            try:
                rating_float = float(rating)
                if rating_float >= 8.0:
                    mood_tags.append('highly-rated')
                elif rating_float >= 7.0:
                    mood_tags.append('well-received')
                elif rating_float < 5.0:
                    mood_tags.append('controversial')
            except (ValueError, TypeError):
                pass
        
        # Runtime-based moods
        runtime = metadata.get('runtime')
        if runtime:
            if runtime > 180:
                mood_tags.append('epic')
            elif runtime < 90:
                mood_tags.append('quick-watch')
        
        # Remove duplicates and return
        return list(set(mood_tags))

