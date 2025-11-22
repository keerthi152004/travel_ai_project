"""
Multi-Agent Tourism System - Flask Backend
==========================================
Run: pip install flask requests flask-cors
Then: python app.py

Access frontend at: http://localhost:5000
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
from typing import Optional
from dataclasses import dataclass, asdict
import re
import urllib.parse

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)


# ============== Data Classes ==============

@dataclass
class Location:
    name: str
    display_name: str
    lat: float
    lon: float

@dataclass
class Weather:
    temperature: float
    humidity: int
    precipitation_probability: int
    wind_speed: float
    description: str

@dataclass
class Place:
    name: str
    place_type: str
    lat: float
    lon: float


# ============== Geocoding Agent ==============

class GeocodingAgent:
    """Converts place names to coordinates using Nominatim API"""
    BASE_URL = "https://nominatim.openstreetmap.org/search"
    
    def __init__(self):
        self.headers = {"User-Agent": "TourismAgentDemo/1.0"}
        self.logs = []
    
    def get_coordinates(self, place_name: str) -> tuple[Optional[Location], list]:
        self.logs = []
        self.logs.append({"agent": "Geocoding Agent", "message": f"Searching for '{place_name}'...", "type": "info"})
        
        params = {"q": place_name, "format": "json", "limit": 1}
        
        try:
            response = requests.get(self.BASE_URL, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                self.logs.append({"agent": "Geocoding Agent", "message": "Could not find location", "type": "error"})
                return None, self.logs
            
            location = Location(
                name=place_name,
                display_name=data[0]["display_name"],
                lat=float(data[0]["lat"]),
                lon=float(data[0]["lon"])
            )
            self.logs.append({"agent": "Geocoding Agent", "message": f"Found: {location.display_name[:50]}...", "type": "success"})
            return location, self.logs
            
        except Exception as e:
            self.logs.append({"agent": "Geocoding Agent", "message": f"API Error: {str(e)}", "type": "error"})
            return None, self.logs


# ============== Weather Agent ==============

class WeatherAgent:
    """Fetches weather data using Open-Meteo API"""
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    WEATHER_CODES = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle",
        55: "Dense drizzle", 61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        80: "Rain showers", 81: "Moderate showers", 82: "Violent showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail"
    }
    
    def __init__(self):
        self.logs = []
    
    def get_weather(self, lat: float, lon: float) -> tuple[Optional[Weather], list]:
        self.logs = []
        self.logs.append({"agent": "Weather Agent", "message": f"Fetching weather for ({lat:.2f}, {lon:.2f})...", "type": "info"})
        
        params = {
            "latitude": lat, "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m",
            "timezone": "auto"
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if "current" not in data:
                self.logs.append({"agent": "Weather Agent", "message": "No weather data", "type": "error"})
                return None, self.logs
            
            current = data["current"]
            weather = Weather(
                temperature=current["temperature_2m"],
                humidity=current["relative_humidity_2m"],
                precipitation_probability=current.get("precipitation_probability", 0),
                wind_speed=current["wind_speed_10m"],
                description=self.WEATHER_CODES.get(current.get("weather_code", 0), "Unknown")
            )
            self.logs.append({"agent": "Weather Agent", "message": f"Retrieved: {weather.temperature}°C, {weather.description}", "type": "success"})
            return weather, self.logs
            
        except Exception as e:
            self.logs.append({"agent": "Weather Agent", "message": f"API Error: {str(e)}", "type": "error"})
            return None, self.logs


# ============== Places Agent ==============

class PlacesAgent:
    """Finds tourist attractions using Overpass API"""
    BASE_URL = "https://overpass-api.de/api/interpreter"
    
    def __init__(self):
        self.logs = []
    
    def get_places(self, lat: float, lon: float, limit: int = 5) -> tuple[list[Place], list]:
        self.logs = []
        self.logs.append({"agent": "Places Agent", "message": f"Searching attractions near ({lat:.2f}, {lon:.2f})...", "type": "info"})
        
        query = f"""
        [out:json][timeout:25];
        (
          node["tourism"="attraction"](around:10000,{lat},{lon});
          way["tourism"="attraction"](around:10000,{lat},{lon});
          node["historic"](around:10000,{lat},{lon});
          node["leisure"="park"]["name"](around:10000,{lat},{lon});
          node["tourism"="museum"](around:10000,{lat},{lon});
          node["amenity"="place_of_worship"]["name"](around:10000,{lat},{lon});
        );
        out body center 30;
        """
        
        try:
            response = requests.post(self.BASE_URL, data=query, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if "elements" not in data or not data["elements"]:
                self.logs.append({"agent": "Places Agent", "message": "No attractions found", "type": "error"})
                return [], self.logs
            
            seen, places = set(), []
            for el in data["elements"]:
                tags = el.get("tags", {})
                name = tags.get("name")
                
                # Get coordinates
                if el.get("type") == "way" and "center" in el:
                    p_lat, p_lon = el["center"]["lat"], el["center"]["lon"]
                else:
                    p_lat, p_lon = el.get("lat", lat), el.get("lon", lon)
                
                if name and name not in seen:
                    seen.add(name)
                    ptype = tags.get("tourism") or tags.get("historic") or tags.get("leisure") or "attraction"
                    places.append(Place(name=name, place_type=ptype, lat=p_lat, lon=p_lon))
                    if len(places) >= limit:
                        break
            
            self.logs.append({"agent": "Places Agent", "message": f"Found {len(places)} attractions", "type": "success"})
            return places, self.logs
            
        except Exception as e:
            self.logs.append({"agent": "Places Agent", "message": f"API Error: {str(e)}", "type": "error"})
            return [], self.logs


# ============== Photo Agent ==============

class PhotoAgent:
    """Fetches photos using Wikipedia API and Unsplash Source"""
    
    def __init__(self):
        self.logs = []
        self.headers = {"User-Agent": "TourismAgentDemo/1.0"}
    
    def get_photos(self, place_name: str, city_name: str = "", limit: int = 6) -> tuple[list[dict], list]:
        self.logs = []
        self.logs.append({"agent": "Photo Agent", "message": f"Searching photos for '{place_name}'...", "type": "info"})
        
        photos = []
        
        # Method 1: Try Wikipedia API for the place
        wiki_photos = self._get_wikipedia_images(place_name)
        photos.extend(wiki_photos)
        
        # Method 2: Try with city name added
        if len(photos) < limit and city_name:
            wiki_photos2 = self._get_wikipedia_images(f"{place_name} {city_name}")
            for p in wiki_photos2:
                if p not in photos:
                    photos.append(p)
        
        # Method 3: Use Unsplash Source (free, no API key needed)
        if len(photos) < limit:
            search_term = urllib.parse.quote(place_name)
            for i in range(limit - len(photos)):
                photos.append({
                    "url": f"https://source.unsplash.com/400x300/?{search_term},landmark&sig={i}",
                    "thumb": f"https://source.unsplash.com/400x300/?{search_term},landmark&sig={i}",
                    "source": "Unsplash"
                })
        
        photos = photos[:limit]
        
        if photos:
            self.logs.append({"agent": "Photo Agent", "message": f"Found {len(photos)} photos", "type": "success"})
        else:
            self.logs.append({"agent": "Photo Agent", "message": "No photos found", "type": "error"})
        
        return photos, self.logs
    
    def _get_wikipedia_images(self, search_term: str) -> list[dict]:
        """Get images from Wikipedia"""
        photos = []
        
        try:
            # First, search for the Wikipedia page
            search_url = "https://en.wikipedia.org/w/api.php"
            search_params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": search_term,
                "srlimit": 1
            }
            
            response = requests.get(search_url, params=search_params, headers=self.headers, timeout=10)
            data = response.json()
            
            if not data.get("query", {}).get("search"):
                return photos
            
            page_title = data["query"]["search"][0]["title"]
            
            # Get images from the page
            images_params = {
                "action": "query",
                "format": "json",
                "titles": page_title,
                "prop": "images",
                "imlimit": 10
            }
            
            response = requests.get(search_url, params=images_params, headers=self.headers, timeout=10)
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                images = page.get("images", [])
                for img in images:
                    img_title = img.get("title", "")
                    # Filter out icons, logos, etc.
                    if any(skip in img_title.lower() for skip in ["icon", "logo", "flag", "map", "symbol", ".svg", "commons-logo"]):
                        continue
                    
                    # Get image URL
                    img_url = self._get_image_url(img_title)
                    if img_url:
                        photos.append({
                            "url": img_url,
                            "thumb": img_url,
                            "source": "Wikipedia"
                        })
                        if len(photos) >= 4:
                            break
                            
        except Exception as e:
            pass
        
        return photos
    
    def _get_image_url(self, file_title: str) -> Optional[str]:
        """Get direct URL for a Wikipedia image"""
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "titles": file_title,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 400
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=5)
            data = response.json()
            
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                imageinfo = page.get("imageinfo", [{}])[0]
                return imageinfo.get("thumburl") or imageinfo.get("url")
                
        except:
            pass
        
        return None


# ============== Tourism Agent (Parent) ==============

class TourismAgent:
    """Parent agent that orchestrates the tourism system"""
    
    def __init__(self):
        self.geocoding = GeocodingAgent()
        self.weather_agent = WeatherAgent()
        self.places_agent = PlacesAgent()
        self.photo_agent = PhotoAgent()
        self.current_city = ""
    
    def parse_query(self, query: str) -> tuple[str, bool, bool]:
        q = query.lower()
        wants_weather = any(w in q for w in ["weather", "temperature", "rain", "climate", "hot", "cold"])
        wants_places = any(w in q for w in ["place", "visit", "attraction", "see", "plan", "trip", "tour", "go"])
        
        if not wants_weather and not wants_places:
            wants_weather, wants_places = True, True
        
        patterns = [
            r"(?:to|in|at|visit|going to)\s+([A-Za-z\s]+?)(?:,|\.|what|and|$|\?)",
            r"^([A-Za-z\s]+?)(?:,|\.|what|and|$|\?)"
        ]
        
        place = None
        for p in patterns:
            m = re.search(p, query, re.IGNORECASE)
            if m:
                place = m.group(1).strip()
                for w in ["let's", "lets", "please", "i want to", "i'm", "im"]:
                    place = place.lower().replace(w, "").strip()
                if place:
                    break
        
        return (place or query.strip(), wants_weather, wants_places)
    
    def process(self, query: str) -> dict:
        all_logs = []
        all_logs.append({"agent": "Tourism Agent", "message": f"Processing: {query}", "type": "info"})
        
        place_name, wants_weather, wants_places = self.parse_query(query)
        all_logs.append({"agent": "Tourism Agent", "message": f"Place: {place_name}, Weather: {wants_weather}, Places: {wants_places}", "type": "info"})
        
        # Geocode
        location, logs = self.geocoding.get_coordinates(place_name)
        all_logs.extend(logs)
        
        if not location:
            return {
                "success": False,
                "error": f"I don't know if \"{place_name}\" exists. Please check the spelling.",
                "logs": all_logs
            }
        
        # Store city name for photo searches
        self.current_city = place_name.title()
        
        result = {
            "success": True,
            "place": place_name.title(),
            "display_name": location.display_name,
            "city_lat": location.lat,
            "city_lon": location.lon,
            "weather": None,
            "places": [],
            "logs": all_logs
        }
        
        # Weather
        if wants_weather:
            weather, logs = self.weather_agent.get_weather(location.lat, location.lon)
            all_logs.extend(logs)
            if weather:
                result["weather"] = asdict(weather)
        
        # Places
        if wants_places:
            places, logs = self.places_agent.get_places(location.lat, location.lon)
            all_logs.extend(logs)
            result["places"] = [asdict(p) for p in places]
        
        all_logs.append({"agent": "Tourism Agent", "message": "Processing complete!", "type": "success"})
        return result
    
    def get_place_details(self, place_name: str, lat: float, lon: float, city: str = "") -> dict:
        """Get photos for a specific place"""
        all_logs = []
        all_logs.append({"agent": "Tourism Agent", "message": f"Fetching details for '{place_name}'...", "type": "info"})
        
        # Get photos
        photos, logs = self.photo_agent.get_photos(place_name, city or self.current_city)
        all_logs.extend(logs)
        
        all_logs.append({"agent": "Tourism Agent", "message": "Details fetched!", "type": "success"})
        
        return {
            "success": True,
            "name": place_name,
            "lat": lat,
            "lon": lon,
            "photos": photos,
            "logs": all_logs
        }


# Initialize agent
agent = TourismAgent()


# ============== Routes ==============

@app.route("/")
def index():
    return send_from_directory('.', 'index.html')

@app.route("/styles.css")
def styles():
    return send_from_directory('.', 'styles.css')

@app.route("/script.js")
def script():
    return send_from_directory('.', 'script.js')

@app.route("/api/query", methods=["POST"])
def query():
    data = request.json
    user_query = data.get("query", "")
    if not user_query:
        return jsonify({"success": False, "error": "No query provided"})
    result = agent.process(user_query)
    return jsonify(result)

@app.route("/api/place-details", methods=["POST"])
def place_details():
    data = request.json
    name = data.get("name", "")
    lat = data.get("lat", 0)
    lon = data.get("lon", 0)
    city = data.get("city", "")
    if not name:
        return jsonify({"success": False, "error": "No place name provided"})
    result = agent.get_place_details(name, lat, lon, city)
    return jsonify(result)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("  ✈️  Wanderlust - AI Travel Planner")
    print("="*50)
    print("\n  Server running at: http://localhost:5000")
    print("  Open this URL in your browser")
    print("  Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)