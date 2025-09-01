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
    
    def search_tv(self, query: str, first_air_year: Optional[int] = None) -> List[Dict]:
        """Search for TV series by name"""
        params = {'query': query}
        if first_air_year:
            params['first_air_date_year'] = first_air_year
        data = self._make_request('search/tv', params)
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
    
    def get_tv_details(self, tv_id: int) -> Optional[Dict]:
        """Get detailed TV information by TMDb ID"""
        endpoint = f"tv/{tv_id}"
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
            ],
            'type': 'movie'
        }
        
        return formatted_data
    
    def format_tv_data(self, tmdb_data: Dict) -> Dict:
        """Format TMDb TV data for our database structure"""
        if not tmdb_data:
            return {}
        # Cast
        cast = []
        if 'credits' in tmdb_data and 'cast' in tmdb_data['credits']:
            cast = [
                {
                    'name': actor['name'],
                    'character': actor.get('roles', [{}])[0].get('character', '') if isinstance(actor.get('roles'), list) and actor.get('roles') else actor.get('character', ''),
                    'order': actor.get('order', 999)
                }
                for actor in tmdb_data['credits']['cast'][:10]
            ]
        # Crew
        crew = {}
        if tmdb_data.get('created_by'):
            crew['Creator'] = [p.get('name') for p in tmdb_data.get('created_by', []) if p.get('name')]
        if 'credits' in tmdb_data and 'crew' in tmdb_data['credits']:
            for person in tmdb_data['credits']['crew']:
                job = person.get('job', '')
                if job in ['Director', 'Writer', 'Producer', 'Executive Producer', 'Showrunner']:
                    crew.setdefault(job, []).append(person['name'])
        # Genres
        genres = [g['name'] for g in tmdb_data.get('genres', [])]
        # Poster/Backdrop
        poster_url = f"{self.IMAGE_BASE_URL}{tmdb_data['poster_path']}" if tmdb_data.get('poster_path') else ''
        backdrop_url = f"https://image.tmdb.org/t/p/w1280{tmdb_data['backdrop_path']}" if tmdb_data.get('backdrop_path') else ''
        # External IDs
        external_ids = tmdb_data.get('external_ids', {})
        imdb_id = external_ids.get('imdb_id', '')
        return {
            'tmdb_id': tmdb_data.get('id'),
            'imdb_id': imdb_id,
            'title': tmdb_data.get('name', ''),
            'original_title': tmdb_data.get('original_name', ''),
            'overview': tmdb_data.get('overview', ''),
            'release_date': tmdb_data.get('first_air_date', ''),
            'runtime': (tmdb_data.get('episode_run_time') or [None])[0],
            'poster_path': poster_url,
            'backdrop_path': backdrop_url,
            'genres': genres,
            'cast': cast,
            'crew': crew,
            'trailers': [
                {
                    'name': v['name'], 'key': v['key'], 'site': v['site'], 'type': v['type']
                }
                for v in (tmdb_data.get('videos', {}).get('results', []))
                if v.get('type') == 'Trailer' and v.get('site') == 'YouTube'
            ][:3],
            'homepage': tmdb_data.get('homepage', ''),
            'status': tmdb_data.get('status', ''),
            'original_language': tmdb_data.get('original_language', ''),
            'spoken_languages': [
                lang['english_name'] for lang in tmdb_data.get('spoken_languages', [])
            ],
            'type': 'series'
        }
    
    def find_movie(self, title: str, year: Optional[int] = None, director: Optional[str] = None, content_type: Optional[str] = None) -> Optional[Dict]:
        """Find a movie or TV series and return formatted data. Prefers exact matches; avoids loose first-result picks.

        content_type: 'movie' | 'series' | 'documentary' | None
        """
        def normalize(s: str) -> str:
            if not isinstance(s, str):
                return ''
            s = s.lower().strip()
            for ch in [':', '-', ',', '.', '!', '?', '\'', '"']:
                s = s.replace(ch, '')
            # Remove leading articles
            for art in ['the ', 'a ', 'an ']:
                if s.startswith(art):
                    s = s[len(art):]
            return s

        norm_title = normalize(title)

        if content_type == 'series':
            movie_results = []
            tv_results = self.search_tv(title, year)
        elif content_type in ['movie', 'documentary']:
            movie_results = self.search_movies(title, year)
            tv_results = []
        else:
            movie_results = self.search_movies(title, year)
            tv_results = self.search_tv(title, year)

        def pick_exact(results, title_keys: List[str]) -> Optional[Dict]:
            for r in results:
                for key in title_keys:
                    candidate = r.get(key, '')
                    if normalize(candidate) == norm_title:
                        return r
            return None

        # Try exact movie title match
        best_movie = pick_exact(movie_results, ['title', 'original_title'])
        # Try exact TV name match
        best_tv = pick_exact(tv_results, ['name', 'original_name'])

        # If director is provided, try to prefer result whose credits include the director/creator
        def prefer_by_director(results, fetch_details_fn, crew_keys: List[str]) -> Optional[Dict]:
            if not director:
                return None
            dir_norm = normalize(director)
            for r in results[:5]:
                details = fetch_details_fn(r['id'])
                if not details:
                    continue
                # Inspect credits and created_by
                # Collect names
                names = []
                if 'credits' in details:
                    for c in details['credits'].get('crew', []):
                        if c.get('job') in ['Director', 'Writer', 'Producer', 'Executive Producer', 'Showrunner']:
                            names.append(c.get('name', ''))
                for cb in details.get('created_by', []) or []:
                    names.append(cb.get('name', ''))
                if any(normalize(n) == dir_norm for n in names if n):
                    return r
            return None

        if not best_movie and movie_results:
            director_movie = prefer_by_director(movie_results, self.get_movie_details, [])
            if director_movie:
                best_movie = director_movie

        if not best_tv and tv_results:
            director_tv = prefer_by_director(tv_results, self.get_tv_details, [])
            if director_tv:
                best_tv = director_tv

        # Choose priority: exact movie > exact tv > director-matched movie/tv already handled
        chosen = best_movie or best_tv
        
        # If still no choice, use a simple token-overlap score to pick best candidate across movie and TV
        if not chosen:
            def token_set(s: str) -> set:
                return set([t for t in normalize(s).split() if t])
            query_tokens = token_set(title)
            def best_by_tokens(results: List[Dict], keys: List[str]) -> Optional[Dict]:
                best = None
                best_score = 0.0
                for r in results:
                    for key in keys:
                        cand = r.get(key, '')
                        ts = token_set(cand)
                        if not ts:
                            continue
                        inter = len(query_tokens & ts)
                        union = len(query_tokens | ts) or 1
                        score = inter / union
                        if score > best_score:
                            best_score = score
                            best = r
                # Require a minimal similarity to avoid wild mismatches
                return best if best_score >= 0.5 else None
            candidate_movie = best_by_tokens(movie_results, ['title', 'original_title'])
            candidate_tv = best_by_tokens(tv_results, ['name', 'original_name'])
            # Prefer the one with higher token overlap by recomputing
            def score_of(r: Optional[Dict], keys: List[str]) -> float:
                if not r:
                    return 0.0
                # reuse token_set scoring
                best_local = 0.0
                for key in keys:
                    cand = r.get(key, '')
                    ts = token_set(cand)
                    inter = len(query_tokens & ts)
                    union = len(query_tokens | ts) or 1
                    best_local = max(best_local, inter/union)
                return best_local
            if score_of(candidate_tv, ['name', 'original_name']) >= score_of(candidate_movie, ['title', 'original_title']):
                chosen = candidate_tv or candidate_movie
            else:
                chosen = candidate_movie or candidate_tv
            if not chosen:
                return None

        # Fetch details for the chosen item (movie or tv)
        if 'title' in chosen or 'original_title' in chosen:
            details = self.get_movie_details(chosen['id'])
            if not details:
                return None
            # If explicitly searching for a documentary, ensure genre match
            if content_type == 'documentary':
                genre_names = [g['name'] for g in details.get('genres', [])]
                if 'Documentary' not in genre_names:
                    return None
            return self.format_movie_data(details)
        else:
            details = self.get_tv_details(chosen['id'])
            return self.format_tv_data(details) if details else None

