# ✈️ Wanderlust - AI Travel Planner

A multi-agent tourism system that helps you plan your trips by providing weather information, tourist attractions, photos, and Google Maps integration for any destination worldwide.

## 🌟 Features

- **🔍 Smart Destination Search** - Enter any city or place name to explore
- **🌤️ Real-time Weather** - Get current temperature, humidity, rain chance, and wind speed
- **🏛️ Top Attractions** - Discover up to 5 tourist attractions near your destination
- **📍 Google Maps Integration** - View locations, get directions, find nearby restaurants & hotels
- **📸 Photo Gallery** - View photos of attractions from Wikipedia and Unsplash
- **🗺️ Interactive Map Preview** - Embedded OpenStreetMap preview for each location
- **📱 Responsive Design** - Works seamlessly on desktop, tablet, and mobile

## 🏗️ System Architecture

This project implements a **Multi-Agent System** with the following agents:

| Agent | Role | API Used |
|-------|------|----------|
| **Tourism Agent** | Parent orchestrator that coordinates all child agents | - |
| **Geocoding Agent** | Converts place names to coordinates (latitude/longitude) | [Nominatim API](https://nominatim.org/) |
| **Weather Agent** | Fetches current weather data for the location | [Open-Meteo API](https://open-meteo.com/) |
| **Places Agent** | Finds tourist attractions, parks, museums, historic sites | [Overpass API](https://overpass-api.de/) |
| **Photo Agent** | Retrieves photos for attractions | [Wikipedia API](https://www.mediawiki.org/wiki/API) + [Unsplash](https://unsplash.com/) |

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                      User Query                          │
│            "I want to visit Paris"                       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                   TOURISM AGENT                          │
│                  (Parent/Orchestrator)                   │
│  • Parses user query                                     │
│  • Extracts destination name                             │
│  • Determines user intent (weather/places/both)          │
│  • Coordinates child agents                              │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┬─────────────┐
        │             │             │             │
        ▼             ▼             ▼             ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│ GEOCODING │  │  WEATHER  │  │  PLACES   │  │   PHOTO   │
│   AGENT   │  │   AGENT   │  │   AGENT   │  │   AGENT   │
├───────────┤  ├───────────┤  ├───────────┤  ├───────────┤
│ Nominatim │  │ Open-Meteo│  │ Overpass  │  │ Wikipedia │
│    API    │  │    API    │  │    API    │  │ + Unsplash│
└─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
      │              │              │              │
      ▼              ▼              ▼              ▼
┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐
│Coordinates│  │ Weather   │  │ Attractions│  │  Photos   │
│ lat, lon  │  │   Data    │  │   List    │  │   URLs    │
└───────────┘  └───────────┘  └───────────┘  └───────────┘
```

## 📁 Project Structure

```
wanderlust/
├── app.py              # Streamlit app with all agents
├── index.html          # Frontend HTML (optional, for reference)
├── styles.css          # Additional CSS styles (optional)
├── script.js           # Frontend JavaScript (optional, for reference)
├── requirements.txt    # Python dependencies
└── README.md           # Project documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone or create the project folder**
   ```bash
   mkdir wanderlust
   cd wanderlust
   ```

2. **Save all project files** (`app.py`, `requirements.txt`, `README.md`) into the folder

3. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open your browser**
   ```
   http://localhost:8501
   ```

## ☁️ Deploy to Streamlit Cloud

1. **Push your code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/wanderlust.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect your GitHub repository
   - Select `app.py` as the main file
   - Click "Deploy"

3. **Your app will be live at:**
   ```
   https://YOUR_APP_NAME.streamlit.app
   ```

## 💡 Usage Examples

### Example 1: Plan a Trip
```
Input: "I'm going to Bangalore, let's plan my trip"
Output: Weather info + Top 5 attractions in Bangalore
```

### Example 2: Check Weather Only
```
Input: "What is the temperature in Tokyo?"
Output: Current weather conditions in Tokyo
```

### Example 3: Find Attractions Only
```
Input: "Places to visit in Paris"
Output: Top 5 tourist attractions in Paris
```

### Example 4: Combined Query
```
Input: "I want to visit Dubai, what's the weather and places to see?"
Output: Weather info + Top 5 attractions in Dubai
```

### Example 5: Unknown Location
```
Input: "Take me to Xyzland"
Output: "I don't know if 'Xyzland' exists. Please check the spelling."
```

## 🛠️ Technologies Used

### Backend
- **Python 3.8+** - Programming language
- **Streamlit** - Web framework for data apps
- **Requests** - HTTP library for API calls

### Frontend (Built into Streamlit)
- **Streamlit Components** - UI elements
- **Custom CSS** - Styling
- **HTML/Markdown** - Content rendering

### External APIs
- **Nominatim** - Geocoding (OpenStreetMap)
- **Open-Meteo** - Weather data
- **Overpass** - Points of interest (OpenStreetMap)
- **Wikipedia** - Photos
- **Unsplash** - Fallback photos
- **OpenStreetMap** - Embedded map preview
- **Google Maps** - Directions & nearby places

## 🎨 UI Features

- **Travel-themed design** with warm orange/amber color palette
- **Glass-morphism cards** with backdrop blur
- **Quick destination suggestions** (Paris, Tokyo, New York, Dubai, Bali)
- **Expandable attraction cards** with maps and photos
- **Fully responsive** for all screen sizes

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [OpenStreetMap](https://www.openstreetmap.org/) - Map data
- [Open-Meteo](https://open-meteo.com/) - Free weather API
- [Unsplash](https://unsplash.com/) - Beautiful photos
- [Wikipedia](https://www.wikipedia.org/) - Place information and images
- [Streamlit](https://streamlit.io/) - Amazing web framework


---

**Happy Travels! ✈️🌍**
