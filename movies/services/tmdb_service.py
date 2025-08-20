import requests
import os
from django.conf import settings
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class TMDbService:
    """Service class for interacting with The Movie Database (TMDb) API"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
    
    def __init__(self):
        self.api_key = settings.TMDB_API_KEY
        if not self.api_key:
            logger.warning("TMDb API key not configured")
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to the TMDb API"""
        if not self.api_key:
            logger.error("TMDb API key not available")
            return None
        
        url = f"{self.BASE_URL}/{endpoint}"
        default_params = {
            'api_key': self.api_key,
            'language': 'en-US'
        }
        
        if params:
            default_params.update(params)
        
        try:
            response = requests.get(url, params=default_params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"TMDb API request failed: {e}")
            return None
    
    def search_movies(self, query: str, year: Optional[int] = None) -> List[Dict]:
        """Search for movies by title"""
        params = {'query': query}
        if year:
            params['year'] = year
        
        data = self._make_request('search/movie', params)
        if data and 'results' in data:
            return data['results']
        return []
    
    def get_movie_details(self, movie_id: int) -> Optional[Dict]:
        """Get detailed movie information by TMDb ID"""
        endpoint = f"movie/{movie_id}"
        params = {
            'append_to_response': 'credits,external_ids,keywords,videos'
        }
        return self._make_request(endpoint, params)
    
    def get_movie_credits(self, movie_id: int) -> Optional[Dict]:
        """Get movie cast and crew information"""
        endpoint = f"movie/{movie_id}/credits"
        return self._make_request(endpoint)
    
    def format_movie_data(self, tmdb_data: Dict) -> Dict:
        """Format TMDb data for our database structure"""
        if not tmdb_data:
            return {}
        
        # Extract cast information
        cast = []
        if 'credits' in tmdb_data and 'cast' in tmdb_data['credits']:
            cast = [
                {
                    'name': actor['name'],
                    'character': actor.get('character', ''),
                    'order': actor.get('order', 999)
                }
                for actor in tmdb_data['credits']['cast'][:10]  # Top 10 cast members
            ]
        
        # Extract crew information (director, writer, etc.)
        crew = {}
        if 'credits' in tmdb_data and 'crew' in tmdb_data['credits']:
            for person in tmdb_data['credits']['crew']:
                job = person.get('job', '')
                if job in ['Director', 'Writer', 'Producer']:
                    if job not in crew:
                        crew[job] = []
                    crew[job].append(person['name'])
        
        # Extract genres
        genres = []
        if 'genres' in tmdb_data:
            genres = [genre['name'] for genre in tmdb_data['genres']]
        
        # Build poster URL
        poster_url = ''
        if tmdb_data.get('poster_path'):
            poster_url = f"{self.IMAGE_BASE_URL}{tmdb_data['poster_path']}"
        
        # Build backdrop URL
        backdrop_url = ''
        if tmdb_data.get('backdrop_path'):
            backdrop_url = f"https://image.tmdb.org/t/p/w1280{tmdb_data['backdrop_path']}"
        
        # Extract external IDs
        external_ids = tmdb_data.get('external_ids', {})
        imdb_id = external_ids.get('imdb_id', '')
        
        # Extract videos (trailers)
        trailers = []
        if 'videos' in tmdb_data and 'results' in tmdb_data['videos']:
            trailers = [
                {
                    'name': video['name'],
                    'key': video['key'],
                    'site': video['site'],
                    'type': video['type']
                }
                for video in tmdb_data['videos']['results']
                if video['type'] == 'Trailer' and video['site'] == 'YouTube'
            ][:3]  # Top 3 trailers
        
        formatted_data = {
            'tmdb_id': tmdb_data.get('id'),
            'imdb_id': imdb_id,
            'title': tmdb_data.get('title', ''),
            'original_title': tmdb_data.get('original_title', ''),
            'overview': tmdb_data.get('overview', ''),
            'release_date': tmdb_data.get('release_date', ''),
            'runtime': tmdb_data.get('runtime'),
            'budget': tmdb_data.get('budget', 0),
            'revenue': tmdb_data.get('revenue', 0),
            'popularity': tmdb_data.get('popularity', 0),
            'vote_average': tmdb_data.get('vote_average', 0),
            'vote_count': tmdb_data.get('vote_count', 0),
            'poster_path': poster_url,
            'backdrop_path': backdrop_url,
            'genres': genres,
            'cast': cast,
            'crew': crew,
            'trailers': trailers,
            'tagline': tmdb_data.get('tagline', ''),
            'homepage': tmdb_data.get('homepage', ''),
            'status': tmdb_data.get('status', ''),
            'original_language': tmdb_data.get('original_language', ''),
            'production_companies': [
                company['name'] for company in tmdb_data.get('production_companies', [])
            ],
            'production_countries': [
                country['name'] for country in tmdb_data.get('production_countries', [])
            ],
            'spoken_languages': [
                lang['english_name'] for lang in tmdb_data.get('spoken_languages', [])
            ]
        }
        
        return formatted_data
    
    def find_movie(self, title: str, year: Optional[int] = None, director: Optional[str] = None) -> Optional[Dict]:
        """Find a movie and return formatted data"""
        # Search for movies
        search_results = self.search_movies(title, year)
        
        if not search_results:
            return None
        
        # If we have multiple results, try to find the best match
        best_match = None
        for result in search_results:
            # Exact title match gets priority
            if result.get('title', '').lower() == title.lower():
                best_match = result
                break
            # Original title match
            elif result.get('original_title', '').lower() == title.lower():
                best_match = result
                break
        
        # If no exact match, use the first result (most popular)
        if not best_match and search_results:
            best_match = search_results[0]
        
        if not best_match:
            return None
        
        # Get detailed information
        movie_details = self.get_movie_details(best_match['id'])
        if movie_details:
            return self.format_movie_data(movie_details)
        
        return None

