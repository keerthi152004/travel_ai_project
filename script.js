// ============== DOM Elements ==============
const input = document.getElementById('queryInput');
const btn = document.getElementById('searchBtn');
const loadingIndicator = document.getElementById('loadingIndicator');
const resultsDiv = document.getElementById('results');
const modal = document.getElementById('placeModal');
const modalTitle = document.getElementById('modalTitle');
const photosContainer = document.getElementById('photosContainer');
const mapFrame = document.getElementById('mapFrame');

// Google Maps buttons
const viewMapBtn = document.getElementById('viewMapBtn');
const directionsBtn = document.getElementById('directionsBtn');
const nearbyBtn = document.getElementById('nearbyBtn');
const hotelsBtn = document.getElementById('hotelsBtn');

// Store current city info
let currentCity = '';
let cityLat = 0;
let cityLon = 0;

// ============== Event Listeners ==============
input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') processQuery();
});

// Close modal on outside click
modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
});

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeModal();
});

// ============== Set Query from Suggestions ==============
function setQuery(place) {
    input.value = place;
    processQuery();
}

// ============== Main Query Function ==============
async function processQuery() {
    const query = input.value.trim();
    if (!query) return;
    
    // Update UI state
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>Searching...</span>';
    loadingIndicator.classList.add('active');
    resultsDiv.classList.remove('active');
    resultsDiv.innerHTML = '';
    
    try {
        const response = await fetch('/api/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        
        // Store city info
        if (data.success) {
            currentCity = data.place;
            cityLat = data.city_lat;
            cityLon = data.city_lon;
        }
        
        displayResults(data);
        
    } catch (error) {
        resultsDiv.innerHTML = `
            <div class="error-box">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Connection Error</h3>
                <p>Make sure the server is running on http://localhost:5000</p>
            </div>`;
        resultsDiv.classList.add('active');
    }
    
    // Reset UI
    loadingIndicator.classList.remove('active');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-paper-plane"></i><span>Explore</span>';
}

// ============== Display Results ==============
function displayResults(data) {
    if (!data.success) {
        resultsDiv.innerHTML = `
            <div class="error-box">
                <i class="fas fa-map-marker-alt"></i>
                <h3>Location Not Found</h3>
                <p>${data.error}</p>
            </div>`;
        resultsDiv.classList.add('active');
        return;
    }
    
    let html = `
        <div class="location-header">
            <div class="location-icon">
                <i class="fas fa-map-marker-alt"></i>
            </div>
            <div class="location-info">
                <h2>${data.place}</h2>
                <p><i class="fas fa-globe"></i> ${data.display_name}</p>
            </div>
        </div>
        <div class="cards-grid">`;
    
    // Weather Card
    if (data.weather) {
        html += `
            <div class="card weather-card">
                <div class="card-header">
                    <div class="card-icon">
                        <i class="fas fa-cloud-sun"></i>
                    </div>
                    <h3>Weather Now</h3>
                </div>
                <div class="weather-grid">
                    <div class="weather-item">
                        <i class="fas fa-temperature-high" style="color:#ef4444"></i>
                        <div class="value">${data.weather.temperature}°C</div>
                        <div class="label">Temperature</div>
                    </div>
                    <div class="weather-item">
                        <i class="fas fa-cloud-rain" style="color:#3b82f6"></i>
                        <div class="value">${data.weather.precipitation_probability}%</div>
                        <div class="label">Rain Chance</div>
                    </div>
                    <div class="weather-item">
                        <i class="fas fa-tint" style="color:#06b6d4"></i>
                        <div class="value">${data.weather.humidity}%</div>
                        <div class="label">Humidity</div>
                    </div>
                    <div class="weather-item">
                        <i class="fas fa-wind" style="color:#8b5cf6"></i>
                        <div class="value">${data.weather.wind_speed}</div>
                        <div class="label">Wind km/h</div>
                    </div>
                </div>
                <div class="weather-desc">
                    <i class="fas fa-info-circle"></i> ${data.weather.description}
                </div>
            </div>`;
    }
    
    // Places Card
    if (data.places && data.places.length > 0) {
        html += `
            <div class="card places-card">
                <div class="card-header">
                    <div class="card-icon">
                        <i class="fas fa-map-marked-alt"></i>
                    </div>
                    <h3>Top Attractions</h3>
                </div>`;
        
        data.places.forEach((place, i) => {
            const escapedName = escapeHtml(place.name);
            const dataName = place.name.replace(/'/g, "\\'");
            
            html += `
                <div class="place-item" onclick="openPlaceDetails('${dataName}', ${place.lat}, ${place.lon})">
                    <div class="place-num">${i + 1}</div>
                    <div class="place-info">
                        <h4>${escapedName}</h4>
                        <span><i class="fas fa-tag"></i> ${escapeHtml(place.place_type)}</span>
                    </div>
                    <i class="fas fa-chevron-right place-arrow"></i>
                </div>`;
        });
        
        html += `</div>`;
    }
    
    html += `</div>`;
    resultsDiv.innerHTML = html;
    resultsDiv.classList.add('active');
    
    // Smooth scroll to results
    resultsDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============== Place Details Modal ==============
async function openPlaceDetails(name, lat, lon) {
    // Open modal
    modal.classList.add('active');
    modalTitle.textContent = name;
    document.body.style.overflow = 'hidden';
    
    // Setup Google Maps links
    const encodedName = encodeURIComponent(name);
    const encodedCity = encodeURIComponent(currentCity);
    
    // View location in Google Maps
    viewMapBtn.href = `https://www.google.com/maps/search/?api=1&query=${lat},${lon}`;
    
    // Get directions
    directionsBtn.href = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lon}&travelmode=driving`;
    
    // Nearby restaurants
    nearbyBtn.href = `https://www.google.com/maps/search/restaurants/@${lat},${lon},16z`;
    
    // Nearby hotels
    hotelsBtn.href = `https://www.google.com/maps/search/hotels/@${lat},${lon},16z`;
    
    // Set embedded map preview
    mapFrame.src = `https://www.openstreetmap.org/export/embed.html?bbox=${lon-0.01},${lat-0.01},${lon+0.01},${lat+0.01}&layer=mapnik&marker=${lat},${lon}`;
    
    // Show loading state for photos
    photosContainer.innerHTML = `
        <div class="photos-loading">
            <div class="spinner"></div>
            <p>Loading photos...</p>
        </div>`;
    
    // Fetch place details (photos)
    try {
        const response = await fetch('/api/place-details', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, lat, lon, city: currentCity })
        });
        
        const data = await response.json();
        displayPhotos(data.photos || []);
        
    } catch (error) {
        photosContainer.innerHTML = `
            <div class="no-photos">
                <i class="fas fa-image"></i>
                <p>Failed to load photos</p>
            </div>`;
    }
}

// ============== Display Photos ==============
function displayPhotos(photos) {
    if (!photos || photos.length === 0) {
        photosContainer.innerHTML = `
            <div class="no-photos">
                <i class="fas fa-camera"></i>
                <p>No photos available</p>
            </div>`;
        return;
    }
    
    photosContainer.innerHTML = photos.map((photo, index) => `
        <div class="photo-item" onclick="openFullImage('${photo.url}')">
            <img 
                src="${photo.thumb || photo.url}" 
                alt="Photo" 
                loading="lazy" 
                onerror="this.onerror=null; this.src='https://source.unsplash.com/400x400/?travel,landmark&sig=${index}';"
            >
        </div>
    `).join('');
}

// ============== Open Full Image ==============
function openFullImage(url) {
    const largeUrl = url.replace('/400x300/', '/1200x900/').replace('iiurlwidth=400', 'iiurlwidth=1200');
    window.open(largeUrl, '_blank');
}

// ============== Close Modal ==============
function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = '';
    mapFrame.src = '';
}

// ============== Utility Functions ==============
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}