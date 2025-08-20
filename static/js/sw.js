// Movie Catalog Service Worker
// Provides offline functionality and caching

const CACHE_NAME = 'movie-catalog-v1.0.0';
const STATIC_CACHE_NAME = 'movie-catalog-static-v1.0.0';
const DYNAMIC_CACHE_NAME = 'movie-catalog-dynamic-v1.0.0';
const IMAGE_CACHE_NAME = 'movie-catalog-images-v1.0.0';

// Resources to cache immediately
const STATIC_ASSETS = [
  '/',
  '/movies/',
  '/add/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/static/images/no-poster.svg',
  '/static/manifest.json',
  // Add more critical resources as needed
];

// Resources to cache on first access
const DYNAMIC_ASSETS = [
  '/batch-add/',
  '/csv-import/',
  '/admin/',
];

// Image patterns to cache
const IMAGE_PATTERNS = [
  /\/static\/images\//,
  /\/cache\//,
  /\.(?:png|jpg|jpeg|svg|gif|webp)$/i,
];

// API patterns that should be cached
const API_PATTERNS = [
  /\/api\//,
  /\/movie\/\d+\//,
];

// Install event - cache static assets
self.addEventListener('install', event => {
  console.log('[SW] Installing service worker...');
  
  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE_NAME).then(cache => {
        console.log('[SW] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      }),
      
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
  console.log('[SW] Activating service worker...');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE_NAME && 
                cacheName !== DYNAMIC_CACHE_NAME && 
                cacheName !== IMAGE_CACHE_NAME) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      
      // Take control of all clients
      self.clients.claim()
    ])
  );
});

// Fetch event - handle requests with caching strategies
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Skip chrome-extension and other non-http requests
  if (!url.protocol.startsWith('http')) {
    return;
  }
  
  // Handle different types of requests
  if (isImageRequest(request)) {
    event.respondWith(handleImageRequest(request));
  } else if (isAPIRequest(request)) {
    event.respondWith(handleAPIRequest(request));
  } else if (isStaticAsset(request)) {
    event.respondWith(handleStaticRequest(request));
  } else {
    event.respondWith(handleDynamicRequest(request));
  }
});

// Check if request is for an image
function isImageRequest(request) {
  return IMAGE_PATTERNS.some(pattern => pattern.test(request.url));
}

// Check if request is for API data
function isAPIRequest(request) {
  return API_PATTERNS.some(pattern => pattern.test(request.url));
}

// Check if request is for a static asset
function isStaticAsset(request) {
  return STATIC_ASSETS.some(asset => request.url.endsWith(asset)) ||
         request.url.includes('/static/');
}

// Handle image requests - Cache First strategy
async function handleImageRequest(request) {
  try {
    const cache = await caches.open(IMAGE_CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('[SW] Serving cached image:', request.url);
      return cachedResponse;
    }
    
    console.log('[SW] Fetching and caching image:', request.url);
    const response = await fetch(request);
    
    if (response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Image request failed:', error);
    
    // Return placeholder image for failed poster requests
    if (request.url.includes('poster') || request.url.includes('image')) {
      const cache = await caches.open(STATIC_CACHE_NAME);
      return cache.match('/static/images/no-poster.svg');
    }
    
    throw error;
  }
}

// Handle API requests - Network First with cache fallback
async function handleAPIRequest(request) {
  try {
    console.log('[SW] Fetching API data:', request.url);
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] API request failed, trying cache:', error);
    
    const cache = await caches.open(DYNAMIC_CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    throw error;
  }
}

// Handle static assets - Cache First strategy
async function handleStaticRequest(request) {
  try {
    const cache = await caches.open(STATIC_CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      console.log('[SW] Serving cached static asset:', request.url);
      return cachedResponse;
    }
    
    console.log('[SW] Fetching and caching static asset:', request.url);
    const response = await fetch(request);
    
    if (response.ok) {
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Static request failed:', error);
    throw error;
  }
}

// Handle dynamic requests - Network First with cache fallback
async function handleDynamicRequest(request) {
  try {
    console.log('[SW] Fetching dynamic content:', request.url);
    const response = await fetch(request);
    
    if (response.ok) {
      const cache = await caches.open(DYNAMIC_CACHE_NAME);
      cache.put(request, response.clone());
    }
    
    return response;
  } catch (error) {
    console.log('[SW] Dynamic request failed, trying cache:', error);
    
    const cache = await caches.open(DYNAMIC_CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      const offlineResponse = await cache.match('/');
      if (offlineResponse) {
        return offlineResponse;
      }
    }
    
    throw error;
  }
}

// Background sync for when connection is restored
self.addEventListener('sync', event => {
  console.log('[SW] Background sync triggered:', event.tag);
  
  if (event.tag === 'movie-metadata-sync') {
    event.waitUntil(syncMovieMetadata());
  }
});

// Sync movie metadata when online
async function syncMovieMetadata() {
  try {
    console.log('[SW] Syncing movie metadata...');
    
    // Get pending metadata updates from IndexedDB or localStorage
    const pendingUpdates = await getPendingMetadataUpdates();
    
    for (const update of pendingUpdates) {
      try {
        const response = await fetch('/api/update-metadata/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await getCSRFToken(),
          },
          body: JSON.stringify(update)
        });
        
        if (response.ok) {
          await removePendingUpdate(update.id);
          console.log('[SW] Synced metadata for movie:', update.movieId);
        }
      } catch (error) {
        console.log('[SW] Failed to sync metadata for movie:', update.movieId, error);
      }
    }
  } catch (error) {
    console.log('[SW] Background sync failed:', error);
  }
}

// Helper functions for background sync
async function getPendingMetadataUpdates() {
  // This would typically use IndexedDB
  // For now, return empty array
  return [];
}

async function removePendingUpdate(updateId) {
  // Remove from IndexedDB
  console.log('[SW] Removing pending update:', updateId);
}

async function getCSRFToken() {
  // Get CSRF token from cookie or meta tag
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
  }
  return '';
}

// Push notification handling
self.addEventListener('push', event => {
  console.log('[SW] Push notification received');
  
  const options = {
    body: 'New movie metadata available!',
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'View Movies',
        icon: '/static/images/shortcut-browse.png'
      },
      {
        action: 'close',
        title: 'Close',
        icon: '/static/images/shortcut-close.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('Movie Catalog', options)
  );
});

// Handle notification clicks
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification clicked:', event.action);
  
  event.notification.close();
  
  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/movies/')
    );
  }
});

// Message handling for communication with main thread
self.addEventListener('message', event => {
  console.log('[SW] Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'GET_VERSION') {
    event.ports[0].postMessage({ version: CACHE_NAME });
  }
  
  if (event.data && event.data.type === 'CLEAR_CACHE') {
    event.waitUntil(clearAllCaches());
  }
});

// Clear all caches
async function clearAllCaches() {
  const cacheNames = await caches.keys();
  await Promise.all(
    cacheNames.map(cacheName => caches.delete(cacheName))
  );
  console.log('[SW] All caches cleared');
}

console.log('[SW] Service worker loaded successfully');

