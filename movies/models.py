from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json
from datetime import datetime


class Movie(models.Model):
    """
    Movie model to store movie information and metadata
    """
    
    # Watch status choices
    WATCH_STATUS_CHOICES = [
        ('want_to_watch', 'Want to Watch'),
        ('watching', 'Watching'),
        ('watched', 'Watched'),
        ('abandoned', 'Abandoned'),
    ]
    
    # Core movie information
    movie_name = models.CharField(max_length=255, help_text="Title of the movie")
    director = models.CharField(max_length=255, help_text="Director name")
    release_year = models.IntegerField(
        validators=[MinValueValidator(1888), MaxValueValidator(2030)],
        help_text="Year of release"
    )
    
    # Metadata from APIs (TMDb/OMDb)
    metadata_json = models.JSONField(
        default=dict,
        blank=True,
        help_text="TMDb/OMDb metadata (poster URL, ratings, synopsis, cast, genre, etc.)"
    )
    
    # User-specific data
    status = models.CharField(
        max_length=20,
        choices=WATCH_STATUS_CHOICES,
        default='want_to_watch',
        help_text="Watch status"
    )
    
    mood_tags = models.JSONField(
        default=list,
        blank=True,
        null=True,
        help_text="Mood tags (manual or AI-generated)"
    )
    
    user_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="User-assigned rating (1-10)"
    )
    
    user_notes = models.TextField(
        blank=True,
        help_text="User notes"
    )
    
    # Timestamps
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="Last metadata refresh"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['movie_name']),
            models.Index(fields=['director']),
            models.Index(fields=['release_year']),
            models.Index(fields=['status']),
            models.Index(fields=['last_updated']),
        ]
    
    def __str__(self):
        return f"{self.movie_name} ({self.release_year}) - {self.director}"
    
    @property
    def poster_url(self):
        """Get poster URL path relative to MEDIA_ROOT, preferring cached path.

        Returns values like 'cache/filename.jpg' (no leading slash).
        """
        if not self.metadata_json:
            return ''
        cached_path = self.metadata_json.get('cached_poster_path')
        if cached_path:
            # Normalize to forward-slash and strip any leading 'media/' or '/'
            normalized = str(cached_path).replace('\\', '/').lstrip('/')
            if normalized.startswith('media/'):
                normalized = normalized[len('media/'):]
            return normalized
        # No cached poster path available; do not return external URL here
        return ''
    
    @property
    def imdb_rating(self):
        """Get IMDb rating from metadata"""
        if self.metadata_json:
            return self.metadata_json.get('imdb_rating', '')
        return ''
    
    @property
    def rt_rating(self):
        """Get Rotten Tomatoes rating from metadata"""
        if self.metadata_json:
            return self.metadata_json.get('rt_rating', '')
        return ''
    
    @property
    def synopsis(self):
        """Get movie synopsis from metadata"""
        if self.metadata_json:
            return self.metadata_json.get('overview', '')
        return ''
    
    @property
    def genres(self):
        """Get movie genres from metadata"""
        if self.metadata_json and 'genres' in self.metadata_json:
            return self.metadata_json.get('genres', [])
        return []
    
    @property
    def cast(self):
        """Get movie cast from metadata"""
        if self.metadata_json and 'cast' in self.metadata_json:
            return self.metadata_json.get('cast', [])
        return []
    
    @property
    def hype_score(self):
        """Calculate hype score based on ratings and user rating"""
        scores = []
        
        # Add IMDb rating (scale to 10)
        if self.imdb_rating:
            try:
                imdb_score = float(self.imdb_rating)
                scores.append(imdb_score)
            except (ValueError, TypeError):
                pass
        
        # Add RT rating (scale to 10)
        if self.rt_rating:
            try:
                rt_score = float(self.rt_rating.replace('%', '')) / 10
                scores.append(rt_score)
            except (ValueError, TypeError):
                pass
        
        # Add user rating with higher weight
        if self.user_rating:
            scores.extend([self.user_rating] * 2)  # Double weight for user rating
        
        if scores:
            return round(sum(scores) / len(scores), 1)
        return 0.0
    
    def needs_metadata_refresh(self, days=30):
        """Check if metadata needs refresh based on last_updated"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        if not self.last_updated:
            return True
        
        refresh_threshold = timezone.now() - timedelta(days=days)
        return self.last_updated < refresh_threshold
    
    def add_mood_tag(self, tag):
        """Add a mood tag to the movie"""
        if tag not in self.mood_tags:
            self.mood_tags.append(tag)
            self.save()
    
    def remove_mood_tag(self, tag):
        """Remove a mood tag from the movie"""
        if tag in self.mood_tags:
            self.mood_tags.remove(tag)
            self.save()
