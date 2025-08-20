// Movie Catalog - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initThemeToggle();
    initSearch();
    initMovieCards();
    initFilters();
    initKeyboardShortcuts();
    initTooltips();
    initLazyLoading();
    
    // Add stagger animation to cards
    addStaggerAnimation();
});

// Theme Toggle
function initThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const html = document.documentElement;
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'dark';
    html.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
            
            // Add transition effect
            document.body.style.transition = 'all 0.3s ease';
            setTimeout(() => {
                document.body.style.transition = '';
            }, 300);
        });
    }
}

function updateThemeIcon(theme) {
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Search Functionality
function initSearch() {
    const searchInput = document.getElementById('global-search');
    const searchContainer = document.querySelector('.search-container');
    
    if (searchInput) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            const query = this.value.trim();
            
            if (query.length >= 2) {
                searchTimeout = setTimeout(() => {
                    performSearch(query);
                }, 300);
            } else {
                hideSuggestions();
            }
        });
        
        // Hide suggestions when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchContainer || !searchContainer.contains(e.target)) {
                hideSuggestions();
            }
        });
    }
}

function performSearch(query) {
    fetch(`/api/search/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            showSuggestions(data.movies);
        })
        .catch(error => {
            console.error('Search error:', error);
        });
}

function showSuggestions(movies) {
    const searchContainer = document.querySelector('.search-container');
    if (!searchContainer) return;
    
    // Remove existing suggestions
    const existingSuggestions = searchContainer.querySelector('.search-suggestions');
    if (existingSuggestions) {
        existingSuggestions.remove();
    }
    
    if (movies.length === 0) return;
    
    const suggestionsDiv = document.createElement('div');
    suggestionsDiv.className = 'search-suggestions';
    
    movies.forEach(movie => {
        const suggestionDiv = document.createElement('div');
        suggestionDiv.className = 'search-suggestion';
        suggestionDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="me-3">
                    <img src="${movie.poster_url ? (window.MEDIA_URL || '/media/') + movie.poster_url : '/static/images/no-poster.jpg'}" 
                         alt="${movie.title}" 
                         style="width: 40px; height: 60px; object-fit: cover; border-radius: 4px;">
                </div>
                <div>
                    <div class="fw-bold">${movie.title} (${movie.year})</div>
                    <div class="text-muted small">${movie.director}</div>
                    <div class="small">
                        <span class="badge bg-secondary">${movie.status}</span>
                        ${movie.user_rating ? `<span class="text-warning ms-2">★ ${movie.user_rating}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
        
        suggestionDiv.addEventListener('click', function() {
            window.location.href = `/movie/${movie.id}/`;
        });
        
        suggestionsDiv.appendChild(suggestionDiv);
    });
    
    searchContainer.appendChild(suggestionsDiv);
}

function hideSuggestions() {
    const suggestions = document.querySelector('.search-suggestions');
    if (suggestions) {
        suggestions.remove();
    }
}

// Movie Cards Interactions
function initMovieCards() {
    const movieCards = document.querySelectorAll('.movie-card');
    
    movieCards.forEach(card => {
        // Add hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
        
        // Status update functionality
        const statusSelect = card.querySelector('.status-select');
        if (statusSelect) {
            statusSelect.addEventListener('change', function() {
                updateMovieStatus(this.dataset.movieId, this.value);
            });
        }
        
        // Rating update functionality
        const ratingStars = card.querySelectorAll('.rating-star');
        ratingStars.forEach((star, index) => {
            star.addEventListener('click', function() {
                const movieId = this.dataset.movieId;
                const rating = index + 1;
                updateMovieRating(movieId, rating);
            });
            
            star.addEventListener('mouseenter', function() {
                highlightStars(ratingStars, index);
            });
        });
        
        const ratingContainer = card.querySelector('.rating-stars');
        if (ratingContainer) {
            ratingContainer.addEventListener('mouseleave', function() {
                resetStars(ratingStars);
            });
        }
    });
}

function updateMovieStatus(movieId, status) {
    showLoading();
    
    fetch(`/api/movie/${movieId}/status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showNotification(data.message, 'success');
            // Update UI
            updateStatusIndicator(movieId, status);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showNotification('Failed to update status', 'error');
        console.error('Error:', error);
    });
}

function updateMovieRating(movieId, rating) {
    showLoading();
    
    fetch(`/api/movie/${movieId}/rating/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ rating: rating })
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showNotification(data.message, 'success');
            // Update hype score if provided
            if (data.hype_score) {
                updateHypeScore(movieId, data.hype_score);
            }
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showNotification('Failed to update rating', 'error');
        console.error('Error:', error);
    });
}

function refreshMetadata(movieId) {
    showLoading();
    
    fetch(`/api/movie/${movieId}/refresh/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCsrfToken()
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showNotification(data.message, 'success');
            // Reload the page to show updated metadata
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showNotification('Failed to refresh metadata', 'error');
        console.error('Error:', error);
    });
}

// Star rating helpers
function highlightStars(stars, index) {
    stars.forEach((star, i) => {
        if (i <= index) {
            star.classList.remove('empty');
            star.classList.add('filled');
        } else {
            star.classList.remove('filled');
            star.classList.add('empty');
        }
    });
}

function resetStars(stars) {
    stars.forEach(star => {
        const currentRating = parseInt(star.dataset.currentRating) || 0;
        const starIndex = parseInt(star.dataset.index) || 0;
        
        if (starIndex < currentRating) {
            star.classList.remove('empty');
            star.classList.add('filled');
        } else {
            star.classList.remove('filled');
            star.classList.add('empty');
        }
    });
}

// Filters
function initFilters() {
    const filterForm = document.getElementById('filter-form');
    if (filterForm) {
        const filterInputs = filterForm.querySelectorAll('input, select');
        
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Auto-submit form when filters change
                setTimeout(() => {
                    filterForm.submit();
                }, 100);
            });
        });
    }
    
    // Clear filters button
    const clearFiltersBtn = document.getElementById('clear-filters');
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', function() {
            const form = document.getElementById('filter-form');
            if (form) {
                form.reset();
                form.submit();
            }
        });
    }
}

// Keyboard Shortcuts
function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Only trigger if not in an input field
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
            return;
        }
        
        switch(e.key) {
            case '/':
                e.preventDefault();
                const searchInput = document.getElementById('global-search');
                if (searchInput) {
                    searchInput.focus();
                }
                break;
                
            case 'n':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    window.location.href = '/add/';
                }
                break;
                
            case 'h':
                if (e.ctrlKey || e.metaKey) {
                    e.preventDefault();
                    window.location.href = '/';
                }
                break;
        }
    });
}

// Tooltips
function initTooltips() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Lazy Loading
function initLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Animations
function addStaggerAnimation() {
    const cards = document.querySelectorAll('.movie-card, .stat-card');
    cards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('fade-in-up');
    });
}

// Utility Functions
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || '';
}

function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('d-none');
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('d-none');
    }
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    
    const icon = type === 'success' ? 'check-circle' : 
                 type === 'error' ? 'exclamation-triangle' : 
                 type === 'warning' ? 'exclamation-circle' : 'info-circle';
    
    notification.innerHTML = `
        <i class="fas fa-${icon} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

function updateStatusIndicator(movieId, status) {
    const card = document.querySelector(`[data-movie-id="${movieId}"]`);
    if (card) {
        const indicator = card.querySelector('.status-indicator');
        if (indicator) {
            // Remove old status classes
            indicator.classList.remove('status-want-to-watch', 'status-watching', 'status-watched', 'status-abandoned');
            // Add new status class
            indicator.classList.add(`status-${status.replace('_', '-')}`);
            // Update text
            const statusText = status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            indicator.textContent = statusText;
        }
    }
}

function updateHypeScore(movieId, hypeScore) {
    const card = document.querySelector(`[data-movie-id="${movieId}"]`);
    if (card) {
        const scoreElement = card.querySelector('.hype-score');
        if (scoreElement) {
            scoreElement.textContent = hypeScore;
        }
    }
}

// Drag and Drop for Poster Upload
function initDragAndDrop() {
    const dropZones = document.querySelectorAll('.poster-drop-zone');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        
        zone.addEventListener('dragleave', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
        });
        
        zone.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handlePosterUpload(files[0], this.dataset.movieId);
            }
        });
    });
}

function handlePosterUpload(file, movieId) {
    if (!file.type.startsWith('image/')) {
        showNotification('Please upload an image file', 'error');
        return;
    }
    
    const formData = new FormData();
    formData.append('poster', file);
    formData.append('csrfmiddlewaretoken', getCsrfToken());
    
    showLoading();
    
    fetch(`/api/movie/${movieId}/poster/`, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        hideLoading();
        if (data.success) {
            showNotification('Poster updated successfully', 'success');
            // Update poster image
            const posterImg = document.querySelector(`[data-movie-id="${movieId}"] .movie-poster`);
            if (posterImg) {
                const mediaBase = window.MEDIA_URL || '/media/';
                posterImg.src = data.poster_url ? mediaBase + data.poster_url : posterImg.src;
            }
        } else {
            showNotification(data.message, 'error');
        }
    })
    .catch(error => {
        hideLoading();
        showNotification('Failed to upload poster', 'error');
        console.error('Error:', error);
    });
}

// Export functions for global access
window.MovieCatalog = {
    updateMovieStatus,
    updateMovieRating,
    refreshMetadata,
    showNotification,
    showLoading,
    hideLoading
};



// PWA and Service Worker functionality
function initializePWA() {
    // Register service worker
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', async () => {
            try {
                const registration = await navigator.serviceWorker.register('/static/js/sw.js', {
                    scope: '/'
                });
                
                console.log('Service Worker registered successfully:', registration.scope);
                
                // Handle service worker updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            showUpdateNotification();
                        }
                    });
                });
                
                // Store registration globally
                window.MovieCatalog = window.MovieCatalog || {};
                window.MovieCatalog.swRegistration = registration;
                
            } catch (error) {
                console.log('Service Worker registration failed:', error);
            }
        });
    }
    
    // Handle app install prompt
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
        console.log('PWA install prompt available');
        e.preventDefault();
        deferredPrompt = e;
        showInstallButton();
    });
    
    // Handle app installed
    window.addEventListener('appinstalled', (evt) => {
        console.log('PWA was installed');
        hideInstallButton();
        showToast('App installed successfully!', 'success');
    });
    
    // Store install prompt globally
    window.MovieCatalog = window.MovieCatalog || {};
    window.MovieCatalog.installPrompt = () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the install prompt');
                } else {
                    console.log('User dismissed the install prompt');
                }
                deferredPrompt = null;
            });
        }
    };
}

// Show service worker update notification
function showUpdateNotification() {
    const notification = document.createElement('div');
    notification.className = 'update-notification';
    notification.innerHTML = `
        <div class="update-content">
            <i class="fas fa-download"></i>
            <span>New version available!</span>
            <button onclick="updateApp()" class="btn btn-sm btn-primary">Update</button>
            <button onclick="dismissUpdate()" class="btn btn-sm btn-outline-secondary">Later</button>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto-show notification
    setTimeout(() => notification.classList.add('show'), 100);
}

// Update the app
window.updateApp = function() {
    if (window.MovieCatalog && window.MovieCatalog.swRegistration) {
        window.MovieCatalog.swRegistration.waiting.postMessage({ type: 'SKIP_WAITING' });
        window.location.reload();
    }
};

// Dismiss update notification
window.dismissUpdate = function() {
    const notification = document.querySelector('.update-notification');
    if (notification) {
        notification.remove();
    }
};

// Show install button
function showInstallButton() {
    let installBtn = document.getElementById('install-btn');
    if (!installBtn) {
        installBtn = document.createElement('button');
        installBtn.id = 'install-btn';
        installBtn.className = 'btn btn-outline-primary install-btn';
        installBtn.innerHTML = '<i class="fas fa-download me-2"></i>Install App';
        installBtn.onclick = () => {
            if (window.MovieCatalog && window.MovieCatalog.installPrompt) {
                window.MovieCatalog.installPrompt();
            }
        };
        
        // Add to navigation
        const nav = document.querySelector('.navbar-nav');
        if (nav) {
            const li = document.createElement('li');
            li.className = 'nav-item';
            li.appendChild(installBtn);
            nav.appendChild(li);
        }
    }
    installBtn.style.display = 'block';
}

// Hide install button
function hideInstallButton() {
    const installBtn = document.getElementById('install-btn');
    if (installBtn) {
        installBtn.style.display = 'none';
    }
}

// Offline status handling
function initializeOfflineHandling() {
    // Show offline indicator
    function showOfflineIndicator() {
        let indicator = document.getElementById('offline-indicator');
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'offline-indicator';
            indicator.className = 'offline-indicator';
            indicator.innerHTML = `
                <i class="fas fa-wifi-slash"></i>
                <span>You're offline. Some features may be limited.</span>
            `;
            document.body.appendChild(indicator);
        }
        indicator.classList.add('show');
    }
    
    // Hide offline indicator
    function hideOfflineIndicator() {
        const indicator = document.getElementById('offline-indicator');
        if (indicator) {
            indicator.classList.remove('show');
        }
    }
    
    // Listen for online/offline events
    window.addEventListener('online', () => {
        console.log('Back online');
        hideOfflineIndicator();
        showToast('Connection restored!', 'success');
        
        // Sync any pending data
        if (window.MovieCatalog && window.MovieCatalog.swRegistration) {
            window.MovieCatalog.swRegistration.sync.register('movie-metadata-sync');
        }
    });
    
    window.addEventListener('offline', () => {
        console.log('Gone offline');
        showOfflineIndicator();
        showToast('You\'re now offline. Cached content is still available.', 'info');
    });
    
    // Check initial online status
    if (!navigator.onLine) {
        showOfflineIndicator();
    }
}

// Initialize PWA features
document.addEventListener('DOMContentLoaded', function() {
    initializePWA();
    initializeOfflineHandling();
});

// Add CSS for PWA features
const pwaStyles = `
.update-notification {
    position: fixed;
    top: -100px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--card-bg);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 1rem;
    box-shadow: 0 10px 30px var(--shadow-light);
    backdrop-filter: blur(10px);
    z-index: 10000;
    transition: top 0.3s ease;
}

.update-notification.show {
    top: 20px;
}

.update-content {
    display: flex;
    align-items: center;
    gap: 1rem;
    color: var(--text-primary);
}

.update-content i {
    color: var(--primary-color);
    font-size: 1.2rem;
}

.install-btn {
    margin-left: 1rem;
}

.offline-indicator {
    position: fixed;
    bottom: -100px;
    left: 50%;
    transform: translateX(-50%);
    background: var(--warning-color);
    color: var(--darker-bg);
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    z-index: 10000;
    transition: bottom 0.3s ease;
    box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
}

.offline-indicator.show {
    bottom: 20px;
}

.offline-indicator i {
    font-size: 1.1rem;
}

@media (max-width: 768px) {
    .update-notification {
        left: 10px;
        right: 10px;
        transform: none;
    }
    
    .update-content {
        flex-direction: column;
        text-align: center;
        gap: 0.75rem;
    }
    
    .offline-indicator {
        left: 10px;
        right: 10px;
        transform: none;
        text-align: center;
    }
}
`;

// Inject PWA styles
const styleSheet = document.createElement('style');
styleSheet.textContent = pwaStyles;
document.head.appendChild(styleSheet);

