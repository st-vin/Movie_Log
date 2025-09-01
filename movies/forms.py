from django import forms
from django.core.exceptions import ValidationError
from .models import Movie


class MovieForm(forms.ModelForm):
    """Form for adding/editing a single movie"""
    
    CONTENT_TYPE_CHOICES = [
        ('movie', 'Movie'),
        ('series', 'Series'),
        ('documentary', 'Documentary'),
    ]

    content_type = forms.ChoiceField(
        choices=CONTENT_TYPE_CHOICES,
        initial='movie',
        widget=forms.RadioSelect,
        label='Media Type',
        required=False,
        help_text='Select the media type to improve search accuracy'
    )

    # Override JSONField auto form field to accept a simple comma-separated string
    mood_tags = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter mood tags separated by commas (optional)'
        })
    )

    class Meta:
        model = Movie
        fields = ['movie_name', 'director', 'release_year', 'status', 'user_rating', 'user_notes', 'mood_tags']
        widgets = {
            'movie_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter movie title',
                'required': True
            }),
            'director': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter director name',
                'required': True
            }),
            'release_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter release year',
                'min': 1888,
                'max': 2030
            }),
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'user_rating': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Rate 1-10 (optional)',
                'min': 1,
                'max': 10
            }),
            'user_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your notes about this movie (optional)',
                'rows': 3
            }),
        }
    
    def clean_mood_tags(self):
        """Convert comma-separated string to list"""
        mood_tags = self.cleaned_data.get('mood_tags', '')
        if isinstance(mood_tags, str):
            if mood_tags.strip():
                return [tag.strip() for tag in mood_tags.split(',') if tag.strip()]
            else:
                return []
        return mood_tags
    
    def clean_release_year(self):
        """Validate release year"""
        year = self.cleaned_data.get('release_year')
        if year and (year < 1888 or year > 2030):
            raise ValidationError('Release year must be between 1888 and 2030')
        return year


class BatchMovieForm(forms.Form):
    """Form for adding multiple movies at once"""
    
    movies_text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 15,
            'placeholder': 'Enter movies in the format:\nMovie Title (Year) - Director\n\nExample:\nThe Matrix (1999) - The Wachowskis\nPulp Fiction (1994) - Quentin Tarantino\nThe Godfather (1972) - Francis Ford Coppola'
        }),
        help_text='Enter one movie per line in the format: "Movie Title (Year) - Director"',
        label='Movies List'
    )
    
    def clean_movies_text(self):
        """Validate the movies text format"""
        movies_text = self.cleaned_data.get('movies_text', '')
        lines = [line.strip() for line in movies_text.split('\n') if line.strip()]
        
        if not lines:
            raise ValidationError('Please enter at least one movie')
        
        # Validate format of each line
        invalid_lines = []
        for i, line in enumerate(lines, 1):
            if ' - ' not in line:
                invalid_lines.append(f"Line {i}: Missing ' - ' separator")
            else:
                parts = line.split(' - ')
                if len(parts) != 2:
                    invalid_lines.append(f"Line {i}: Invalid format")
                elif not parts[0].strip() or not parts[1].strip():
                    invalid_lines.append(f"Line {i}: Missing title or director")
        
        if invalid_lines:
            raise ValidationError(
                'Invalid format on the following lines:\n' + 
                '\n'.join(invalid_lines[:5]) +
                ('\n...' if len(invalid_lines) > 5 else '')
            )
        
        return movies_text


class CSVImportForm(forms.Form):
    """Form for importing movies from CSV file"""
    
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text='Upload a CSV file with columns: title, director, year (optional: status, user_rating, user_notes)',
        label='CSV File'
    )
    
    def clean_csv_file(self):
        """Validate CSV file"""
        csv_file = self.cleaned_data.get('csv_file')
        
        if not csv_file:
            raise ValidationError('Please select a CSV file')
        
        # Check file extension
        if not csv_file.name.lower().endswith('.csv'):
            raise ValidationError('File must be a CSV file (.csv extension)')
        
        # Check file size (limit to 5MB)
        if csv_file.size > 5 * 1024 * 1024:
            raise ValidationError('File size must be less than 5MB')
        
        return csv_file


class MovieSearchForm(forms.Form):
    """Form for advanced movie search"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search movies, directors, actors...',
            'id': 'search-input'
        }),
        label='Search'
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Statuses')] + Movie.WATCH_STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Watch Status'
    )
    
    genre = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter genre'
        }),
        label='Genre'
    )
    
    mood = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter mood tag'
        }),
        label='Mood'
    )
    
    year_from = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'From year',
            'min': 1888,
            'max': 2030
        }),
        label='Year From'
    )
    
    year_to = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'To year',
            'min': 1888,
            'max': 2030
        }),
        label='Year To'
    )
    
    min_rating = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum rating',
            'min': 1,
            'max': 10
        }),
        label='Minimum Rating'
    )
    
    sort = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('movie_name', 'Title A-Z'),
            ('-movie_name', 'Title Z-A'),
            ('director', 'Director A-Z'),
            ('-director', 'Director Z-A'),
            ('-release_year', 'Year (Newest)'),
            ('release_year', 'Year (Oldest)'),
            ('-user_rating', 'Rating (Highest)'),
            ('user_rating', 'Rating (Lowest)'),
            ('-last_updated', 'Recently Updated'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Sort By',
        initial='-created_at'
    )


class QuickAddForm(forms.Form):
    """Quick form for adding a movie with minimal fields"""
    
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Movie title',
            'required': True
        }),
        label='Title'
    )
    
    director = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Director name',
            'required': True
        }),
        label='Director'
    )
    
    year = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Year (optional)',
            'min': 1888,
            'max': 2030
        }),
        label='Year'
    )
    
    def save(self):
        """Create a movie from the form data"""
        if self.is_valid():
            return Movie.objects.create(
                movie_name=self.cleaned_data['title'],
                director=self.cleaned_data['director'],
                release_year=self.cleaned_data.get('year') or 2000
            )
        return None

