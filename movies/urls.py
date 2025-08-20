from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    # Main pages
    path('', views.dashboard, name='dashboard'),
    path('movies/', views.MovieListView.as_view(), name='movie_list'),
    path('movie/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    
    # Add movies
    path('add/', views.AddMovieView.as_view(), name='add_movie'),
    path('batch-add/', views.batch_add_movies, name='batch_add'),
    path('csv-import/', views.csv_import, name='csv_import'),
    
    # AJAX endpoints
    path('api/movie/<int:movie_id>/status/', views.update_movie_status, name='update_status'),
    path('api/movie/<int:movie_id>/rating/', views.update_movie_rating, name='update_rating'),
    path('api/movie/<int:movie_id>/refresh/', views.refresh_metadata, name='refresh_metadata'),
    path('api/search/', views.api_search_movies, name='api_search'),
    path('api/movie/<int:movie_id>/delete/', views.delete_movie, name='delete_movie'),
]

