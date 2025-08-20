# Movie Catalog - Deployment Guide

This guide provides step-by-step instructions for deploying the Movie Catalog application in various environments.

## Quick Start (Development)

1. **Clone and Setup**

   ```bash
   git clone <repository-url>
   cd movie_catalog
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment Configuration**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Database Setup**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run Development Server**

   ```bash
   python manage.py runserver
   ```

## Production Deployment Options

### Option 1: Heroku (Recommended for beginners)

1. **Install Heroku CLI**

   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Create Heroku App**

   ```bash
   heroku create your-movie-catalog
   heroku addons:create heroku-postgresql:hobby-dev
   ```

3. **Configure Environment Variables**

   ```bash
   heroku config:set TMDB_API_KEY=your_tmdb_key
   heroku config:set OMDB_API_KEY=your_omdb_key
   heroku config:set SECRET_KEY=your_secret_key
   heroku config:set DEBUG=False
   ```

4. **Deploy**

   ```bash
   git push heroku main
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### Option 2: DigitalOcean App Platform

1. **Create App**
   - Connect your GitHub repository
   - Choose Python as the runtime
   - Set build command: `pip install -r requirements.txt`
   - Set run command: `gunicorn movie_catalog_project.wsgi:application --bind 0.0.0.0:$PORT`

2. **Add Database**
   - Add PostgreSQL database component
   - Configure DATABASE_URL environment variable

3. **Environment Variables**

   ```env
   TMDB_API_KEY=your_tmdb_key
   OMDB_API_KEY=your_omdb_key
   SECRET_KEY=your_secret_key
   DEBUG=False
   ```

### Option 3: VPS (Ubuntu/CentOS)

1. **Server Setup**

   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Install dependencies
   sudo apt install python3 python3-pip python3-venv nginx postgresql postgresql-contrib
   ```

2. **Database Setup**

   ```bash
   sudo -u postgres createuser --interactive
   sudo -u postgres createdb moviedb
   ```

3. **Application Setup**

   ```bash
   cd /var/www
   sudo git clone <repository-url> movie_catalog
   sudo chown -R $USER:$USER movie_catalog
   cd movie_catalog
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install gunicorn psycopg2-binary
   ```

4. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env with production settings
   ```

5. **Database Migration**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py collectstatic
   python manage.py createsuperuser
   ```

6. **Gunicorn Service**

   ```bash
   sudo nano /etc/systemd/system/movie_catalog.service
   ```

   ```ini
   [Unit]
   Description=Movie Catalog Django App
   After=network.target
   
   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/var/www/movie_catalog
   Environment="PATH=/var/www/movie_catalog/venv/bin"
   ExecStart=/var/www/movie_catalog/venv/bin/gunicorn --workers 3 --bind unix:/var/www/movie_catalog/movie_catalog.sock movie_catalog_project.wsgi:application
   
   [Install]
   WantedBy=multi-user.target
   ```

7. **Nginx Configuration**

   ```bash
   sudo nano /etc/nginx/sites-available/movie_catalog
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location = /favicon.ico { access_log off; log_not_found off; }
       location /static/ {
           root /var/www/movie_catalog;
       }
       
       location /media/ {
           root /var/www/movie_catalog;
       }
       
       location / {
           include proxy_params;
           proxy_pass http://unix:/var/www/movie_catalog/movie_catalog.sock;
       }
   }
   ```

8. **Enable Services**

   ```bash
   sudo systemctl start movie_catalog
   sudo systemctl enable movie_catalog
   sudo ln -s /etc/nginx/sites-available/movie_catalog /etc/nginx/sites-enabled
   sudo systemctl restart nginx
   ```

### Option 4: Docker Deployment

1. **Create Dockerfile**

   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   RUN python manage.py collectstatic --noinput
   
   EXPOSE 8000
   
   CMD ["gunicorn", "--bind", "0.0.0.0:8000", "movie_catalog_project.wsgi:application"]
   ```

2. **Docker Compose**

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
         - TMDB_API_KEY=${TMDB_API_KEY}
         - OMDB_API_KEY=${OMDB_API_KEY}
       depends_on:
         - db
       volumes:
         - ./cache:/app/cache
         - ./media:/app/media
     
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

3. **Deploy**

   ```bash
   docker-compose up -d
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

## Environment Variables

### Required Variables

```env
SECRET_KEY=your-secret-key-here
TMDB_API_KEY=your-tmdb-api-key
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### Optional Variables

```env
OMDB_API_KEY=your-omdb-api-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
REDIS_URL=redis://localhost:6379/0
```

## SSL/HTTPS Setup

### Using Let's Encrypt (Certbot)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
sudo systemctl reload nginx
```

### Using Cloudflare

1. Add your domain to Cloudflare
2. Update DNS records to point to your server
3. Enable "Full (strict)" SSL mode
4. Configure Nginx for HTTPS

## Performance Optimization

### Database Optimization

```python
# In settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        }
    }
}
```

### Caching Setup

```python
# Redis caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Static Files (CDN)

```python
# AWS S3 for static files
AWS_ACCESS_KEY_ID = 'your-access-key'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
AWS_S3_REGION_NAME = 'us-east-1'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.StaticS3Boto3Storage'
```

## Monitoring and Maintenance

### Health Checks

```python
# Add to urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

### Logging Configuration

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/var/log/movie_catalog/django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Backup Strategy

```bash
# Database backup
pg_dump moviedb > backup_$(date +%Y%m%d_%H%M%S).sql

# Media files backup
tar -czf media_backup_$(date +%Y%m%d_%H%M%S).tar.gz media/

# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump moviedb > $BACKUP_DIR/db_backup_$DATE.sql

# Media backup
tar -czf $BACKUP_DIR/media_backup_$DATE.tar.gz media/

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

## Troubleshooting

### Common Issues

1. **Static Files Not Loading**

   ```bash
   python manage.py collectstatic --clear
   ```

2. **Database Connection Errors**
   - Check DATABASE_URL format
   - Verify database credentials
   - Ensure database server is running

3. **API Rate Limits**
   - Check API key validity
   - Monitor API usage
   - Implement request throttling

4. **Memory Issues**
   - Increase server memory
   - Optimize database queries
   - Enable caching

### Debug Mode

```python
# Temporarily enable debug mode
DEBUG = True
ALLOWED_HOSTS = ['*']
```

### Log Analysis

```bash
# View Django logs
tail -f /var/log/movie_catalog/django.log

# View Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# View system logs
journalctl -u movie_catalog -f
```

## Security Checklist

- [ ] DEBUG = False in production
- [ ] Strong SECRET_KEY
- [ ] HTTPS enabled
- [ ] Database credentials secured
- [ ] API keys in environment variables
- [ ] Regular security updates
- [ ] Firewall configured
- [ ] Backup strategy implemented
- [ ] Monitoring enabled

## Support

For deployment issues or questions:

1. Check the troubleshooting section
2. Review Django deployment documentation
3. Check server logs for error messages
4. Verify environment variables and configuration

---

**Movie Catalog** - Successfully deployed and ready to catalog your cinema collection! 🎬
