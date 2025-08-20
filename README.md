# Movie Catalog - Your Personal Cinema Collection

A comprehensive Django web application for cataloging and exploring movies with rich metadata, offline capabilities, and an immersive film-inspired user experience. Built with modern web technologies and designed as a Progressive Web App (PWA) for seamless desktop and mobile usage.

## 🎬 Overview

Movie Catalog transforms the way you organize and discover your personal movie collection. Whether you're a casual movie watcher or a dedicated cinephile, this application provides powerful tools to catalog, rate, and explore films with detailed metadata fetched from industry-leading APIs.

### Key Features

#### **🎯 Core Functionality**

- **Comprehensive Movie Database**: Store unlimited movies with detailed metadata including posters, ratings, cast, crew, and plot summaries
- **Multiple Data Entry Methods**: Add movies individually, batch import multiple titles, or migrate from CSV files
- **Advanced Search & Filtering**: Find movies by title, director, cast, genre, mood, year, or rating with fuzzy search capabilities
- **Watch Status Tracking**: Organize movies by status (Want to Watch, Watching, Watched, Abandoned)
- **Personal Rating System**: Rate movies on a 1-10 scale with personal notes and reviews

##### **🎨 User Experience**

- **Dark Mode Design**: Immersive cinema-inspired interface with glassmorphism effects and subtle film grain
- **Responsive Layout**: Optimized for desktop, tablet, and mobile devices with touch-friendly interactions
- **Interactive Movie Cards**: Hover effects, smooth transitions, and visual status indicators
- **Mood-Based Organization**: Classify and filter movies by emotional tone (intense, uplifting, romantic, etc.)
- **Keyboard Shortcuts**: Power user features for quick navigation and actions

##### **🌐 Modern Web Technologies**

- **Progressive Web App (PWA)**: Install on any device for native app-like experience
- **Offline Capabilities**: Browse your collection and cached content without internet connection
- **Service Worker**: Intelligent caching strategies for optimal performance
- **API Integration**: Automatic metadata fetching from TMDb and OMDb APIs with fallback support

##### **📊 Analytics & Insights**

- **Collection Statistics**: Track total movies, watch status distribution, and viewing patterns
- **Hype Score Algorithm**: Weighted rating system combining IMDb, Rotten Tomatoes, and personal ratings
- **Recently Added**: Quick access to your latest additions
- **Genre Distribution**: Visual breakdown of your collection by genre

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)
- TMDb API key (free registration at [themoviedb.org](https://www.themoviedb.org/settings/api))
- OMDb API key (optional, free registration at [omdbapi.com](http://www.omdbapi.com/apikey.aspx))

### Installation

1. **Clone the Repository**

   ```bash
   git clone <repository-url>
   cd movie_catalog
   ```

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**

   ```bash
   cp .env.example .env
   ```

   Edit `.env` file with your API keys:

   ```bash
   TMDB_API_KEY=your_tmdb_api_key_here
   OMDB_API_KEY=your_omdb_api_key_here
   SECRET_KEY=your_django_secret_key_here
   DEBUG=True
   ```

5. **Database Setup**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run Development Server**

   ```bash
   python manage.py runserver
   ```

7. **Access Application**
   Open your browser and navigate to `http://localhost:8000/`

## 🚫 What not to commit (Git hygiene)

Keep secrets and machine-specific or generated files out of version control:

- Environment files: `.env`, `.env.*`, `*.env` (contain secrets like `SECRET_KEY`, API keys)
- Database files: `db.sqlite3`, `*.sqlite3`
- User content and caches: `media/` (includes `media/cache/` with poster images)
- Collected static: `staticfiles/` (generated via `collectstatic`)
- Python artefacts: `__pycache__/`, `*.pyc`, `*.pyo`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`
- Logs and coverage: `*.log`, `.coverage*`, `htmlcov/`, `coverage.xml`
- Local datasets/imports: `*.csv`, `*.tsv`, `*.xls`, `*.xlsx`
- Virtualenvs: `venv/`, `.venv/`, `env/`
- Editor/OS files: `.idea/`, `.vscode/`, `.DS_Store`, `Thumbs.db`

These rules are included in `.gitignore` so your first commit stays clean.

## 📖 User Guide

### Getting Started

Upon first launch, you'll be greeted by the dashboard showing your collection statistics and recently added movies. The interface is designed to be intuitive, but here's a comprehensive guide to all features.

### Adding Movies

#### **Single Movie Entry**

1. Click the "Add" button in the navigation bar
2. Select "Single Movie" from the dropdown
3. Fill in the movie title and director (required fields)
4. Optionally add release year, watch status, rating, mood tags, and personal notes
5. Click "Add Movie" to save

The application will automatically fetch metadata including poster images, plot summaries, cast information, and ratings from TMDb and OMDb APIs.

#### **Batch Adding**

1. Navigate to Add → Batch Add
2. Enter multiple movies in the text area, one per line
3. Use the format: `Movie Title (Year) - Director Name`
4. Click "Preview" to validate your entries
5. Click "Add Movies" to process the batch

#### **CSV Import**

1. Navigate to Add → CSV Import
2. Download the provided template or prepare your CSV file
3. Ensure your CSV includes required columns: `title`, `director`
4. Optional columns: `year`, `status`, `user_rating`, `user_notes`
5. Upload your file and configure import options
6. Click "Import Movies" to process

### Browsing and Filtering

The movie list page provides powerful filtering and search capabilities:

#### **Search Options**

- **Text Search**: Search across movie titles, directors, and cast members
- **Watch Status**: Filter by Want to Watch, Watching, Watched, or Abandoned
- **Genre Filter**: Select from automatically detected genres
- **Mood Filter**: Filter by emotional tags (intense, funny, romantic, etc.)
- **Year Range**: Specify a range of release years
- **Minimum Rating**: Show only highly-rated movies
- **Sort Options**: Order by date added, title, director, year, or rating

#### **Advanced Features**

- **Fuzzy Search**: Find movies even with partial or misspelled queries
- **Multiple Filters**: Combine multiple criteria for precise results
- **Real-time Updates**: Filters apply instantly without page reloads
- **Persistent Settings**: Your filter preferences are remembered

### Movie Details

Click any movie card to view comprehensive details:

#### **Information Sections**

- **Hero Section**: Large poster, title, director, year, and key ratings
- **Synopsis**: Plot summary and overview
- **Cast & Crew**: Key actors and production team
- **Ratings**: IMDb, Rotten Tomatoes, and your personal rating
- **Genres**: Automatically categorized genres
- **Mood Tags**: Emotional descriptors for the film
- **Personal Notes**: Your private thoughts and reviews

#### **Interactive Elements**

- **Status Dropdown**: Change watch status directly from the detail page
- **Star Rating**: Click to rate the movie on a 1-10 scale
- **Metadata Refresh**: Update information from external APIs
- **Edit Options**: Modify any field or add personal notes

### Mood-Based Organization

One of Movie Catalog's unique features is mood-based organization. Movies can be tagged with emotional descriptors that help you find the perfect film for your current state of mind.

#### **Common Mood Tags**

- **Intense**: Thrillers, action films, psychological dramas
- **Uplifting**: Feel-good movies, inspirational stories
- **Romantic**: Love stories and romantic comedies
- **Dark**: Noir films, dystopian futures, heavy dramas
- **Funny**: Comedies and light-hearted entertainment
- **Thought-provoking**: Films that challenge perspectives
- **Nostalgic**: Period pieces and childhood favorites

#### **Using Mood Filters**

1. Navigate to the Movies page
2. Use the Mood dropdown to select desired emotional tone
3. Combine with other filters for precise recommendations
4. Save favorite filter combinations for quick access

### Offline Usage

Movie Catalog is designed to work seamlessly offline through Progressive Web App technology:

#### **Offline Capabilities**

- **Cached Content**: Previously viewed movies and metadata remain accessible
- **Poster Images**: Downloaded posters are stored locally for offline viewing
- **Search & Filter**: Full functionality available without internet connection
- **Data Sync**: Changes made offline sync automatically when connection is restored

#### **Installation as PWA**

1. Visit the application in a modern browser
2. Look for the "Install App" button or browser prompt
3. Click "Install" to add Movie Catalog to your device
4. Access from your desktop, dock, or home screen like a native app

## 🔧 Configuration

### API Configuration

#### **TMDb API Setup**

1. Register at [themoviedb.org](https://www.themoviedb.org/account/signup)
2. Navigate to Settings → API
3. Request an API key (free for personal use)
4. Add your key to the `.env` file as `TMDB_API_KEY`

#### **OMDb API Setup (Optional)**

1. Register at [omdbapi.com](http://www.omdbapi.com/apikey.aspx)
2. Choose the free tier (1,000 requests per day)
3. Add your key to the `.env` file as `OMDB_API_KEY`

The application uses TMDb as the primary source and falls back to OMDb if needed. OMDb provides additional rating sources like Rotten Tomatoes.

### Database Configuration

Movie Catalog uses SQLite by default, which requires no additional setup. For production deployments or larger collections, you can configure PostgreSQL or MySQL:

#### **PostgreSQL Setup**

```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'movie_catalog',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

#### **Environment Variables**

```bash
DATABASE_URL=postgresql://username:password@localhost:5432/movie_catalog
```

### Caching Configuration

The application includes intelligent caching for optimal performance:

#### **Image Caching**

- Poster images are cached locally in the `/cache/` directory
- Automatic cleanup of old cached images
- Configurable cache size limits

#### **Metadata Caching**

- Movie metadata is stored in the database for offline access
- Automatic refresh of stale data (configurable interval)
- Manual refresh option for individual movies

#### **Service Worker Caching**

- Static assets cached for offline use
- Dynamic content cached with network-first strategy
- Automatic cache updates when new versions are deployed

## 🎨 Customization

### Theme Customization

Movie Catalog includes a sophisticated theming system with dark and light modes:

#### **CSS Custom Properties**

```css
:root {
  --primary-color: #e50914;      /* Netflix red */
  --secondary-color: #f5c518;    /* IMDb gold */
  --background-color: #1a1a1a;   /* Dark background */
  --card-bg: rgba(45, 55, 72, 0.8); /* Card background */
  --text-primary: #ffffff;       /* Primary text */
  --text-secondary: #a0aec0;     /* Secondary text */
}
```

#### **Custom Themes**

1. Create a new CSS file in `/static/css/themes/`
2. Override the custom properties with your color scheme
3. Add theme selection logic to the JavaScript
4. Update the theme toggle functionality

### Adding Custom Fields

To add custom fields to the Movie model:

1. **Update the Model**

   ```python
   # In movies/models.py
   class Movie(models.Model):
       # ... existing fields ...
       custom_field = models.CharField(max_length=255, blank=True)
   ```

2. **Create Migration**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

3. **Update Forms**

   ```python
   # In movies/forms.py
   class MovieForm(forms.ModelForm):
       class Meta:
           fields = ['movie_name', 'director', 'custom_field', ...]
   ```

4. **Update Templates**
   Add the field to your templates in the appropriate sections.

### Custom Mood Tags

Mood tags can be customized to match your personal categorization system:

**Predefined Tags**
Edit the `MOOD_TAG_SUGGESTIONS` list in `static/js/main.js`:

```javascript
const MOOD_TAG_SUGGESTIONS = [
    'your-custom-tag',
    'another-tag',
    // ... more tags
];
```

**AI-Generated Tags**
For automatic mood tag generation, integrate with OpenAI or similar services:

```python
# In movies/services/ai_service.py
def generate_mood_tags(synopsis, genres):
    # Implementation for AI-powered mood tag generation
    pass
```

## 🔌 API Reference

### Internal API Endpoints

Movie Catalog provides several internal API endpoints for advanced usage:

#### **Movie Operations**

- `GET /api/movies/` - List all movies with filtering
- `GET /api/movies/{id}/` - Get movie details
- `POST /api/movies/` - Create new movie
- `PUT /api/movies/{id}/` - Update movie
- `DELETE /api/movies/{id}/` - Delete movie

#### **Metadata Operations**

- `POST /api/movies/{id}/refresh-metadata/` - Refresh movie metadata
- `POST /api/movies/batch-refresh/` - Refresh multiple movies
- `GET /api/movies/{id}/poster/` - Get poster image

#### **Search and Filtering**

- `GET /api/search/?q={query}` - Search movies
- `GET /api/movies/?genre={genre}` - Filter by genre
- `GET /api/movies/?mood={mood}` - Filter by mood
- `GET /api/movies/?status={status}` - Filter by watch status

#### **Statistics**

- `GET /api/stats/` - Get collection statistics
- `GET /api/stats/genres/` - Get genre distribution
- `GET /api/stats/years/` - Get year distribution

### External API Integration

#### **TMDb API Usage**

```python
# Example API call
import requests

def search_movie(title, year=None):
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': title,
        'year': year
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### **OMDb API Usage**

```python
def get_movie_details(imdb_id):
    url = "http://www.omdbapi.com/"
    params = {
        'apikey': settings.OMDB_API_KEY,
        'i': imdb_id,
        'plot': 'full'
    }
    response = requests.get(url, params=params)
    return response.json()
```

## 🧪 Testing

### Running Tests

Movie Catalog includes comprehensive test coverage:

```bash
# Run all tests
python manage.py test

# Run specific test modules
python manage.py test movies.tests.test_models
python manage.py test movies.tests.test_views
python manage.py test movies.tests.test_api

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML coverage report
```

### Test Categories

#### **Model Tests**

- Movie model validation
- Metadata JSON handling
- Hype score calculation
- Status transitions

#### **View Tests**

- Page rendering
- Form submissions
- Authentication requirements
- Error handling

#### **API Tests**

- Endpoint responses
- Data serialization
- Authentication
- Rate limiting

#### **Integration Tests**

- End-to-end workflows
- API integration
- File uploads
- Batch operations

### Writing Custom Tests

```python
# Example test case
from django.test import TestCase
from movies.models import Movie

class MovieModelTest(TestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            movie_name="Test Movie",
            director="Test Director",
            release_year=2023
        )
    
    def test_hype_score_calculation(self):
        self.movie.metadata_json = {'imdb_rating': '8.5'}
        self.movie.user_rating = 9
        expected_score = 8.7  # Weighted average
        self.assertEqual(self.movie.hype_score, expected_score)
```

## 🚀 Deployment

### Production Deployment

#### **Environment Setup**

1. Set `DEBUG=False` in production
2. Configure `ALLOWED_HOSTS` with your domain
3. Use environment variables for sensitive settings
4. Set up proper database (PostgreSQL recommended)
5. Configure static file serving (WhiteNoise or CDN)

#### **Docker Deployment**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "movie_catalog_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

#### **Docker Compose**

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@db:5432/moviedb
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: moviedb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### **Heroku Deployment**

1. Install Heroku CLI
2. Create Heroku app: `heroku create your-app-name`
3. Add PostgreSQL addon: `heroku addons:create heroku-postgresql:hobby-dev`
4. Set environment variables: `heroku config:set TMDB_API_KEY=your_key`
5. Deploy: `git push heroku main`
6. Run migrations: `heroku run python manage.py migrate`

#### **VPS Deployment**

1. Set up server with Python, PostgreSQL, and Nginx
2. Clone repository and install dependencies
3. Configure Gunicorn as WSGI server
4. Set up Nginx as reverse proxy
5. Configure SSL with Let's Encrypt
6. Set up systemd service for auto-restart

### Performance Optimization

#### **Database Optimization**

- Add database indexes for frequently queried fields
- Use select_related() and prefetch_related() for efficient queries
- Implement database connection pooling
- Regular database maintenance and optimization

#### **Caching Strategy**

- Redis for session and cache storage
- CDN for static assets and images
- Browser caching headers
- Database query caching

#### **Frontend Optimization**

- Minify CSS and JavaScript
- Optimize images (WebP format)
- Implement lazy loading
- Use service worker for aggressive caching

## 🔒 Security

### Security Best Practices

#### **Authentication & Authorization**

- Strong password requirements
- Session security configuration
- CSRF protection enabled
- Secure cookie settings

#### **Data Protection**

- Input validation and sanitization
- SQL injection prevention
- XSS protection
- File upload security

#### **API Security**

- Rate limiting implementation
- API key management
- Request validation
- Error message sanitization

#### **Infrastructure Security**

- HTTPS enforcement
- Security headers configuration
- Regular dependency updates
- Monitoring and logging

### Security Configuration

```python
# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

## 🤝 Contributing

We welcome contributions to Movie Catalog! Here's how you can help:

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with appropriate tests
4. Ensure all tests pass: `python manage.py test`
5. Submit a pull request with detailed description

### Contribution Guidelines

#### **Code Style**

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for complex functions
- Maintain consistent formatting

#### **Testing Requirements**

- Write tests for new features
- Maintain or improve test coverage
- Test across different browsers and devices
- Include integration tests for complex workflows

#### **Documentation**

- Update README for new features
- Add inline code comments
- Update API documentation
- Include usage examples

### Feature Requests

We're always looking to improve Movie Catalog. Popular feature requests include:

- **Social Features**: Share collections and recommendations
- **Advanced Analytics**: Viewing patterns and insights
- **Integration APIs**: Connect with streaming services
- **Mobile App**: Native iOS and Android applications
- **AI Recommendations**: Machine learning-powered suggestions

## 📄 License

Movie Catalog is released under the MIT License. See the LICENSE file for details.

## 🙏 Acknowledgments

### **APIs and Services**

- [The Movie Database (TMDb)](https://www.themoviedb.org/) for comprehensive movie metadata
- [OMDb API](http://www.omdbapi.com/) for additional rating sources
- [Font Awesome](https://fontawesome.com/) for beautiful icons

### **Technologies**

- [Django](https://www.djangoproject.com/) web framework
- [Bootstrap](https://getbootstrap.com/) for responsive design
- [SQLite](https://www.sqlite.org/) for database storage

### **Inspiration**

- Netflix for design inspiration
- IMDb for comprehensive movie data
- Letterboxd for social movie cataloging concepts

## 📞 Support

### **Documentations**

- Check this README for comprehensive information
- Review the inline code comments
- Examine the example configurations

### **Community**

- GitHub Issues for bug reports and feature requests
- Discussions for general questions and ideas
- Wiki for additional documentation and tutorials

**Professional Support**
For commercial deployments or custom development, professional support is available through our consulting services.

---

**Movie Catalog** - Transform your movie collection into a rich, searchable, and beautifully organized digital library. Start cataloging today and rediscover the joy of cinema! 🎬✨
