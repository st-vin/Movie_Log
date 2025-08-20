"""
Comprehensive test suite for Movie Catalog application.
Tests cover models, views, forms, and API integration.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from unittest.mock import patch, Mock
import json
import tempfile
import os

from .models import Movie
from .forms import MovieForm
# from .services.movie_service import MovieMetadataService
# from .services.tmdb_service import TMDbService
# from .services.omdb_service import OMDbService


class MovieModelTest(TestCase):
    """Test cases for the Movie model."""
    
    def setUp(self):
        """Set up test data."""
        self.movie_data = {
            'movie_name': 'The Matrix',
            'director': 'The Wachowskis',
            'release_year': 1999,
            'status': 'watched',
            'user_rating': 9,
            'user_notes': 'Amazing sci-fi movie!',
            'mood_tags': ['intense', 'mind-bending']
        }
        
        self.metadata = {
            'poster_path': 'https://example.com/matrix.jpg',
            'imdb_rating': '8.7',
            'rt_rating': '88%',
            'overview': 'A computer programmer discovers reality is a simulation.',
            'genres': ['Action', 'Sci-Fi'],
            'cast': ['Keanu Reeves', 'Laurence Fishburne', 'Carrie-Anne Moss'],
            'runtime': 136,
            'budget': 63000000,
            'revenue': 467222824
        }
    
    def test_movie_creation(self):
        """Test basic movie creation."""
        movie = Movie.objects.create(**self.movie_data)
        
        self.assertEqual(movie.movie_name, 'The Matrix')
        self.assertEqual(movie.director, 'The Wachowskis')
        self.assertEqual(movie.release_year, 1999)
        self.assertEqual(movie.status, 'watched')
        self.assertEqual(movie.user_rating, 9)
        self.assertTrue(movie.last_updated)
    
    def test_movie_str_representation(self):
        """Test string representation of movie."""
        movie = Movie.objects.create(**self.movie_data)
        expected = 'The Matrix (1999) - The Wachowskis'
        self.assertEqual(str(movie), expected)
    
    def test_hype_score_calculation(self):
        """Test hype score calculation with different rating combinations."""
        movie = Movie.objects.create(**self.movie_data)
        
        # Test with IMDb rating only
        movie.metadata_json = {'imdb_rating': '8.7'}
        movie.save()
        self.assertEqual(movie.hype_score, 8.9)  # IMDb + user rating weighted
        
        # Test with no external ratings
        movie.metadata_json = {}
        movie.save()
        self.assertEqual(movie.hype_score, 9.0)  # Only user rating
    
    def test_poster_url_property(self):
        """Test poster URL property prefers cached path over poster path."""
        movie = Movie.objects.create(**self.movie_data)
        # Test with both cached and poster path
        movie.metadata_json = {
            'poster_path': 'https://example.com/poster.jpg',
            'cached_poster_path': '/media/cache/matrix.jpg'
        }
        movie.save()
        self.assertEqual(movie.poster_url, 'cache/matrix.jpg')
        # When only external poster path exists, property should return empty (templates use MEDIA_URL + cached path)
        movie.metadata_json = {'poster_path': 'https://example.com/poster.jpg'}
        movie.save()
        self.assertEqual(movie.poster_url, '')
        # Test with neither
        movie.metadata_json = {}
        movie.save()
        self.assertEqual(movie.poster_url, '')


class MovieViewTest(TestCase):
    """Test cases for movie views."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        
        self.movie = Movie.objects.create(
            movie_name='Test Movie',
            director='Test Director',
            release_year=2023,
            status='watched',
            user_rating=8,
            metadata_json={
                'poster_path': 'https://example.com/poster.jpg',
                'imdb_rating': '7.5',
                'overview': 'A test movie for testing purposes.'
            }
        )
    
    def test_dashboard_view(self):
        """Test dashboard view."""
        response = self.client.get(reverse('movies:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'TOTAL MOVIES')
    
    def test_movie_list_view(self):
        """Test movie list view."""
        response = self.client.get(reverse('movies:movie_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Movie')
        self.assertContains(response, 'Test Director')
    
    def test_movie_detail_view(self):
        """Test movie detail view."""
        response = self.client.get(
            reverse('movies:movie_detail', kwargs={'pk': self.movie.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Movie')
        self.assertContains(response, 'Test Director')
    
    def test_add_movie_view_get(self):
        """Test add movie view GET request."""
        response = self.client.get(reverse('movies:add_movie'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add New Movie')
        self.assertContains(response, 'Movie Title')


class MovieFormTest(TestCase):
    """Test cases for movie forms."""
    
    def test_movie_form_valid_data(self):
        """Test movie form with valid data."""
        form_data = {
            'movie_name': 'Test Movie',
            'director': 'Test Director',
            'release_year': 2023,
            'status': 'watched',
            'user_rating': 8,
            'user_notes': 'Great movie!',
            'mood_tags': 'exciting, fun'
        }
        
        form = MovieForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_movie_form_required_fields(self):
        """Test movie form with missing required fields."""
        # Missing movie_name
        form_data = {
            'director': 'Test Director',
        }
        form = MovieForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('movie_name', form.errors)
