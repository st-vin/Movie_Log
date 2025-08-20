from django.contrib import admin
from .models import Movie


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = [
        'movie_name', 
        'director', 
        'release_year', 
        'status', 
        'user_rating',
        'hype_score',
        'last_updated'
    ]
    
    list_filter = [
        'status',
        'release_year',
        'last_updated',
        'created_at'
    ]
    
    search_fields = [
        'movie_name',
        'director',
        'metadata_json__cast',
        'metadata_json__genres'
    ]
    
    readonly_fields = [
        'created_at',
        'last_updated',
        'hype_score',
        'poster_url',
        'imdb_rating',
        'rt_rating'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('movie_name', 'director', 'release_year')
        }),
        ('User Data', {
            'fields': ('status', 'user_rating', 'user_notes', 'mood_tags')
        }),
        ('Metadata', {
            'fields': ('metadata_json',),
            'classes': ('collapse',)
        }),
        ('Computed Fields', {
            'fields': ('poster_url', 'imdb_rating', 'rt_rating', 'hype_score'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()
