from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
# API endpoint to delete a movie
from django.views.decorators.csrf import ensure_csrf_cookie
@require_http_methods(["DELETE", "POST"])
@ensure_csrf_cookie
def delete_movie(request, movie_id):
    """API endpoint to delete a movie by ID"""
    try:
        movie = get_object_or_404(Movie, id=movie_id)
        movie.delete()
        return JsonResponse({'success': True, 'message': 'Movie deleted successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.views.generic import ListView, DetailView, CreateView
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
import json
import csv
import io
from typing import Dict, List

from .models import Movie
from .services import MovieMetadataService
from .forms import MovieForm, BatchMovieForm, CSVImportForm


class MovieListView(ListView):
    """Main movie list view with filtering and search"""
    model = Movie
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Movie.objects.all()
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(movie_name__icontains=search_query) |
                Q(director__icontains=search_query) |
                Q(metadata_json__cast__icontains=search_query) |
                Q(metadata_json__genres__icontains=search_query)
            )
        
        # Status filter
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Genre filter
        genre_filter = self.request.GET.get('genre', '')
        if genre_filter:
            queryset = queryset.filter(metadata_json__genres__icontains=genre_filter)
        
        # Media type filter
        media_type = self.request.GET.get('type', '')
        if media_type:
            if media_type == 'documentary':
                queryset = queryset.filter(metadata_json__genres__icontains='Documentary')
            else:
                queryset = queryset.filter(metadata_json__type__iexact=media_type)
        
        # Mood filter
        mood_filter = self.request.GET.get('mood', '')
        if mood_filter:
            queryset = queryset.filter(mood_tags__icontains=mood_filter)
        
        # Year range filter
        year_from = self.request.GET.get('year_from', '')
        year_to = self.request.GET.get('year_to', '')
        if year_from:
            try:
                queryset = queryset.filter(release_year__gte=int(year_from))
            except ValueError:
                pass
        if year_to:
            try:
                queryset = queryset.filter(release_year__lte=int(year_to))
            except ValueError:
                pass
        
        # Rating filter
        min_rating = self.request.GET.get('min_rating', '')
        if min_rating:
            try:
                queryset = queryset.filter(user_rating__gte=int(min_rating))
            except ValueError:
                pass
        
        # Sorting
        sort_by = self.request.GET.get('sort', '-created_at')
        valid_sorts = [
            'movie_name', '-movie_name',
            'director', '-director',
            'release_year', '-release_year',
            'user_rating', '-user_rating',
            'created_at', '-created_at',
            'last_updated', '-last_updated'
        ]
        if sort_by in valid_sorts:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add filter options to context
        context['search_query'] = self.request.GET.get('search', '')
        context['status_filter'] = self.request.GET.get('status', '')
        context['genre_filter'] = self.request.GET.get('genre', '')
        context['mood_filter'] = self.request.GET.get('mood', '')
        context['year_from'] = self.request.GET.get('year_from', '')
        context['year_to'] = self.request.GET.get('year_to', '')
        context['min_rating'] = self.request.GET.get('min_rating', '')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')
        context['media_type'] = self.request.GET.get('type', '')
        
        # Get unique values for filter dropdowns
        context['status_choices'] = Movie.WATCH_STATUS_CHOICES
        context['available_genres'] = self._get_available_genres()
        context['available_moods'] = self._get_available_moods()
        
        return context
    
    def _get_available_genres(self):
        """Get list of all genres from movie metadata"""
        genres = set()
        for movie in Movie.objects.exclude(metadata_json__isnull=True):
            movie_genres = movie.metadata_json.get('genres', [])
            if isinstance(movie_genres, list):
                genres.update(movie_genres)
        return sorted(list(genres))
    
    def _get_available_moods(self):
        """Get list of all mood tags"""
        moods = set()
        for movie in Movie.objects.exclude(mood_tags__isnull=True):
            if isinstance(movie.mood_tags, list):
                moods.update(movie.mood_tags)
        return sorted(list(moods))


class MovieDetailView(DetailView):
    """Detailed view of a single movie"""
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add related movies (same director or genre)
        movie = self.object
        related_movies = Movie.objects.filter(
            Q(director=movie.director) |
            Q(metadata_json__genres__overlap=movie.genres)
        ).exclude(id=movie.id)[:6]
        
        context['related_movies'] = related_movies
        return context


class AddMovieView(CreateView):
    """Add a single movie"""
    model = Movie
    form_class = MovieForm
    template_name = 'movies/add_movie.html'
    success_url = '/'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Fetch metadata for the new movie
        service = MovieMetadataService()
        try:
            # Pass content_type hint from form if provided
            content_type = form.cleaned_data.get('content_type')
            service.update_movie_metadata(self.object, force_refresh=True, content_type=content_type)
            messages.success(
                self.request, 
                f'Movie "{self.object.movie_name}" added successfully with metadata!'
            )
        except Exception as e:
            messages.warning(
                self.request,
                f'Movie added but metadata fetch failed: {str(e)}'
            )
        
        return response


def batch_add_movies(request):
    """Add multiple movies at once"""
    if request.method == 'POST':
        form = BatchMovieForm(request.POST)
        if form.is_valid():
            movies_text = form.cleaned_data['movies_text']
            lines = [line.strip() for line in movies_text.split('\n') if line.strip()]
            
            added_count = 0
            failed_movies = []
            
            for line in lines:
                try:
                    # Parse line format: "Movie Title (Year) - Director"
                    parts = line.split(' - ')
                    if len(parts) != 2:
                        failed_movies.append(f"Invalid format: {line}")
                        continue
                    
                    title_year = parts[0].strip()
                    director = parts[1].strip()
                    
                    # Extract year from title
                    if '(' in title_year and ')' in title_year:
                        title = title_year.split('(')[0].strip()
                        year_str = title_year.split('(')[1].split(')')[0].strip()
                        try:
                            year = int(year_str)
                        except ValueError:
                            year = None
                    else:
                        title = title_year
                        year = None
                    
                    # Check if movie already exists
                    if Movie.objects.filter(
                        movie_name__iexact=title,
                        director__iexact=director,
                        release_year=year
                    ).exists():
                        failed_movies.append(f"Already exists: {line}")
                        continue
                    
                    # Create movie
                    movie = Movie.objects.create(
                        movie_name=title,
                        director=director,
                        release_year=year or 2000  # Default year if not provided
                    )
                    
                    # Fetch metadata in background (optional)
                    try:
                        service = MovieMetadataService()
                        service.update_movie_metadata(movie, force_refresh=True)
                    except Exception:
                        pass  # Ignore metadata errors for batch import
                    
                    added_count += 1
                    
                except Exception as e:
                    failed_movies.append(f"Error processing: {line} - {str(e)}")
            
            # Show results
            if added_count > 0:
                messages.success(request, f'Successfully added {added_count} movies!')
            
            if failed_movies:
                messages.warning(
                    request,
                    f'Failed to add {len(failed_movies)} movies: ' + 
                    ', '.join(failed_movies[:5]) +
                    ('...' if len(failed_movies) > 5 else '')
                )
            
            return redirect('movie_list')
    else:
        form = BatchMovieForm()
    
    return render(request, 'movies/batch_add.html', {'form': form})


def csv_import(request):
    """Import movies from CSV file"""
    if request.method == 'POST':
        form = CSVImportForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            
            # Read CSV file
            try:
                decoded_file = csv_file.read().decode('utf-8')
                csv_data = csv.DictReader(io.StringIO(decoded_file))
                
                added_count = 0
                failed_movies = []
                
                for row in csv_data:
                    try:
                        title = row.get('title', '').strip()
                        director = row.get('director', '').strip()
                        year_str = row.get('year', '').strip()
                        
                        if not title or not director:
                            failed_movies.append(f"Missing title or director in row: {row}")
                            continue
                        
                        # Parse year
                        year = None
                        if year_str:
                            try:
                                year = int(year_str)
                            except ValueError:
                                pass
                        
                        # Check if movie already exists
                        if Movie.objects.filter(
                            movie_name__iexact=title,
                            director__iexact=director,
                            release_year=year
                        ).exists():
                            failed_movies.append(f"Already exists: {title}")
                            continue
                        
                        # Create movie
                        movie_data = {
                            'movie_name': title,
                            'director': director,
                            'release_year': year or 2000,
                        }
                        
                        # Add optional fields if present
                        if 'status' in row and row['status']:
                            status_map = {choice[1]: choice[0] for choice in Movie.WATCH_STATUS_CHOICES}
                            if row['status'] in status_map:
                                movie_data['status'] = status_map[row['status']]
                        
                        if 'user_rating' in row and row['user_rating']:
                            try:
                                movie_data['user_rating'] = int(row['user_rating'])
                            except ValueError:
                                pass
                        
                        if 'user_notes' in row:
                            movie_data['user_notes'] = row['user_notes']
                        
                        movie = Movie.objects.create(**movie_data)
                        added_count += 1
                        
                    except Exception as e:
                        failed_movies.append(f"Error processing row {row}: {str(e)}")
                
                # Show results
                if added_count > 0:
                    messages.success(request, f'Successfully imported {added_count} movies!')
                
                if failed_movies:
                    messages.warning(
                        request,
                        f'Failed to import {len(failed_movies)} movies. Check the format.'
                    )
                
                return redirect('movie_list')
                
            except Exception as e:
                messages.error(request, f'Error reading CSV file: {str(e)}')
    else:
        form = CSVImportForm()
    
    return render(request, 'movies/csv_import.html', {'form': form})


@require_http_methods(["POST"])
def update_movie_status(request, movie_id):
    """AJAX endpoint to update movie watch status"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    try:
        data = json.loads(request.body)
        new_status = data.get('status')
        
        if new_status in [choice[0] for choice in Movie.WATCH_STATUS_CHOICES]:
            movie.status = new_status
            movie.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Status updated to {movie.get_status_display()}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Invalid status'
            }, status=400)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["POST"])
def update_movie_rating(request, movie_id):
    """AJAX endpoint to update movie user rating"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    try:
        data = json.loads(request.body)
        new_rating = data.get('rating')
        
        if new_rating is None:
            movie.user_rating = None
        else:
            rating_int = int(new_rating)
            if 1 <= rating_int <= 10:
                movie.user_rating = rating_int
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'Rating must be between 1 and 10'
                }, status=400)
        
        movie.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Rating updated to {movie.user_rating or "None"}',
            'hype_score': movie.hype_score
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=500)


@require_http_methods(["POST"])
def refresh_metadata(request, movie_id):
    """AJAX endpoint to refresh movie metadata"""
    movie = get_object_or_404(Movie, id=movie_id)
    
    try:
        service = MovieMetadataService()
        service.update_movie_metadata(movie, force_refresh=True)
        
        return JsonResponse({
            'success': True,
            'message': 'Metadata refreshed successfully',
            'poster_url': movie.poster_url,
            'hype_score': movie.hype_score
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Failed to refresh metadata: {str(e)}'
        }, status=500)


def api_search_movies(request):
    """API endpoint for movie search (for AJAX)"""
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'movies': []})
    
    movies = Movie.objects.filter(
        Q(movie_name__icontains=query) |
        Q(director__icontains=query)
    )[:10]
    
    results = []
    for movie in movies:
        results.append({
            'id': movie.id,
            'title': movie.movie_name,
            'director': movie.director,
            'year': movie.release_year,
            'poster_url': movie.poster_url,
            'status': movie.get_status_display(),
            'user_rating': movie.user_rating,
            'hype_score': movie.hype_score
        })
    
    return JsonResponse({'movies': results})


def dashboard(request):
    """Dashboard with statistics and recent movies"""
    context = {
        'total_movies': Movie.objects.count(),
        'watched_movies': Movie.objects.filter(status='watched').count(),
        'want_to_watch': Movie.objects.filter(status='want_to_watch').count(),
        'currently_watching': Movie.objects.filter(status='watching').count(),
        'recent_movies': Movie.objects.order_by('-created_at')[:6],
        'top_rated': Movie.objects.filter(user_rating__isnull=False).order_by('-user_rating')[:6],
        'needs_metadata': Movie.objects.filter(metadata_json__isnull=True).count(),
    }
    
    return render(request, 'movies/dashboard.html', context)


@require_http_methods(["POST"])
def set_poster_from_url(request, movie_id):
    """AJAX endpoint to set/update poster by providing an image URL.

    Expects JSON body: { "url": "https://..." }
    Downloads and caches the image, saves relative cached path to metadata_json.cached_poster_path
    and returns the relative poster_url for display.
    """
    movie = get_object_or_404(Movie, id=movie_id)

    try:
        data = json.loads(request.body)
        poster_url = (data.get('url') or '').strip()
        if not poster_url:
            return JsonResponse({'success': False, 'message': 'Poster URL is required'}, status=400)

        # Basic validation
        if not (poster_url.startswith('http://') or poster_url.startswith('https://')):
            return JsonResponse({'success': False, 'message': 'URL must start with http:// or https://'}, status=400)

        service = MovieMetadataService()
        # Try to reuse cache if already present; otherwise download now
        cached_path = service.get_cached_poster_path(poster_url, movie.movie_name)
        if not cached_path:
            return JsonResponse({'success': False, 'message': 'Failed to download poster'}, status=500)

        # Store relative path under MEDIA_ROOT with forward slashes
        from django.conf import settings
        import os
        relative_path = os.path.relpath(cached_path, settings.MEDIA_ROOT).replace('\\', '/')
        if relative_path.startswith('media/'):
            relative_path = relative_path[len('media/'):]

        # Update movie metadata_json
        metadata = movie.metadata_json or {}
        metadata['cached_poster_path'] = relative_path
        # Also keep original source url for reference
        metadata['poster_path'] = poster_url
        movie.metadata_json = metadata
        movie.save(update_fields=['metadata_json', 'last_updated'])

        return JsonResponse({
            'success': True,
            'message': 'Poster updated successfully',
            'poster_url': movie.poster_url
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
