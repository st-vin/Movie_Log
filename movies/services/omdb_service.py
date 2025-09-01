import requests
from django.conf import settings
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class OMDbService:
    """Service class for interacting with the Open Movie Database (OMDb) API"""
    
    BASE_URL = "http://www.omdbapi.com/"
    
    def __init__(self):
        self.api_key = settings.OMDB_API_KEY
        if not self.api_key:
            logger.warning("OMDb API key not configured")
    
    def _make_request(self, params: Dict) -> Optional[Dict]:
        """Make a request to the OMDb API"""
        if not self.api_key:
            logger.error("OMDb API key not available")
            return None
        
        default_params = {
            'apikey': self.api_key,
            'r': 'json'
        }
        default_params.update(params)
        
        try:
            response = requests.get(self.BASE_URL, params=default_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Check if the response indicates an error
            if data.get('Response') == 'False':
                logger.warning(f"OMDb API error: {data.get('Error', 'Unknown error')}")
                return None
            
            return data
        except requests.exceptions.RequestException as e:
            logger.error(f"OMDb API request failed: {e}")
            return None
    
    def search_by_title(self, title: str, year: Optional[int] = None, plot: str = 'full', content_type: str = 'movie') -> Optional[Dict]:
        """Search by exact title. content_type can be 'movie' or 'series'."""
        params = {
            't': title,
            'plot': plot,
            'type': content_type
        }
        if year:
            params['y'] = year
        
        return self._make_request(params)
    
    def search_by_imdb_id(self, imdb_id: str, plot: str = 'full') -> Optional[Dict]:
        """Search for a movie by IMDb ID"""
        params = {
            'i': imdb_id,
            'plot': plot
        }
        return self._make_request(params)
    
    def search_movies(self, query: str, year: Optional[int] = None, content_type: str = 'movie') -> Optional[Dict]:
        """Search (multiple results). content_type can be 'movie' or 'series'."""
        params = {
            's': query,
            'type': content_type
        }
        if year:
            params['y'] = year
        
        return self._make_request(params)
    
    def format_movie_data(self, omdb_data: Dict) -> Dict:
        """Format OMDb data for our database structure"""
        if not omdb_data:
            return {}
        
        # Parse ratings
        ratings = {}
        if 'Ratings' in omdb_data:
            for rating in omdb_data['Ratings']:
                source = rating.get('Source', '')
                value = rating.get('Value', '')
                if 'Internet Movie Database' in source:
                    ratings['imdb_rating'] = value.replace('/10', '')
                elif 'Rotten Tomatoes' in source:
                    ratings['rt_rating'] = value
                elif 'Metacritic' in source:
                    ratings['metacritic_rating'] = value.replace('/100', '')
        
        # Parse cast and crew
        cast = []
        if omdb_data.get('Actors'):
            actors = omdb_data['Actors'].split(', ')
            cast = [{'name': actor.strip(), 'character': '', 'order': i} 
                   for i, actor in enumerate(actors) if actor.strip()]
        
        crew = {}
        if omdb_data.get('Director'):
            directors = [d.strip() for d in omdb_data['Director'].split(',')]
            crew['Director'] = directors
        
        if omdb_data.get('Writer'):
            writers = [w.strip() for w in omdb_data['Writer'].split(',')]
            crew['Writer'] = writers
        
        # Parse genres
        genres = []
        if omdb_data.get('Genre'):
            genres = [g.strip() for g in omdb_data['Genre'].split(',')]
        
        # Parse runtime
        runtime = None
        if omdb_data.get('Runtime'):
            runtime_str = omdb_data['Runtime'].replace(' min', '')
            try:
                runtime = int(runtime_str)
            except (ValueError, TypeError):
                pass
        
        # Parse box office
        box_office = 0
        if omdb_data.get('BoxOffice'):
            box_office_str = omdb_data['BoxOffice'].replace('$', '').replace(',', '')
            try:
                box_office = int(box_office_str)
            except (ValueError, TypeError):
                pass
        
        formatted_data = {
            'omdb_id': omdb_data.get('imdbID', ''),
            'imdb_id': omdb_data.get('imdbID', ''),
            'title': omdb_data.get('Title', ''),
            'year': omdb_data.get('Year', ''),
            'rated': omdb_data.get('Rated', ''),
            'release_date': omdb_data.get('Released', ''),
            'runtime': runtime,
            'genres': genres,
            'director': omdb_data.get('Director', ''),
            'writer': omdb_data.get('Writer', ''),
            'cast': cast,
            'crew': crew,
            'overview': omdb_data.get('Plot', ''),
            'language': omdb_data.get('Language', ''),
            'country': omdb_data.get('Country', ''),
            'awards': omdb_data.get('Awards', ''),
            'poster_path': omdb_data.get('Poster', ''),
            'metascore': omdb_data.get('Metascore', ''),
            'imdb_rating': ratings.get('imdb_rating', ''),
            'rt_rating': ratings.get('rt_rating', ''),
            'metacritic_rating': ratings.get('metacritic_rating', ''),
            'imdb_votes': omdb_data.get('imdbVotes', ''),
            'type': omdb_data.get('Type', ''),
            'dvd': omdb_data.get('DVD', ''),
            'box_office': box_office,
            'production': omdb_data.get('Production', ''),
            'website': omdb_data.get('Website', ''),
        }
        
        return formatted_data
    
    def find_movie(self, title: str, year: Optional[int] = None, imdb_id: Optional[str] = None) -> Optional[Dict]:
        """Find a movie or series and return formatted data. Prefer exact match movie; then exact series; avoid loose first result."""
        omdb_data = None
        
        # Try searching by IMDb ID first if available
        if imdb_id:
            omdb_data = self.search_by_imdb_id(imdb_id)
        
        # If no IMDb ID or search failed, try by title
        if not omdb_data:
            # Attempt movie first
            omdb_data = self.search_by_title(title, year, content_type='movie')
            if not omdb_data:
                # Then series
                omdb_data = self.search_by_title(title, year, content_type='series')
        
        if omdb_data:
            return self.format_movie_data(omdb_data)
        
        return None

