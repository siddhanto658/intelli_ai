"""
Open-Meteo Weather API - Free, no API key required
Alternative to 7Timer and wttr.in
"""
import requests
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class OpenMeteoWeather:
    """Open-Meteo free weather API."""
    
    # City coordinates (expand as needed)
    CITY_COORDS = {
        "cuttack": {"lat": 20.46, "lon": 86.02},
        "delhi": {"lat": 28.61, "lon": 77.21},
        "mumbai": {"lat": 19.08, "lon": 72.88},
        "bangalore": {"lat": 12.97, "lon": 77.59},
        "chennai": {"lat": 13.08, "lon": 80.28},
        "kolkata": {"lat": 22.57, "lon": 88.36},
        "hyderabad": {"lat": 17.38, "lon": 78.48},
        "pune": {"lat": 18.52, "lon": 73.85},
        "bhubaneswar": {"lat": 20.27, "lon": 85.84},
    }
    
    @staticmethod
    def get_current(city: str = "cuttack") -> Optional[str]:
        """Get current weather."""
        coords = OpenMeteoWeather.CITY_COORDS.get(city.lower(), {"lat": 20.46, "lon": 86.02})
        
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "current_weather": "true",
                "temperature_unit": "celsius"
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            weather = data.get("current_weather", {})
            
            if not weather:
                return None
            
            temp = weather.get("temperature")
            wind = weather.get("windspeed")
            weather_code = weather.get("weathercode", 0)
            
            condition = OpenMeteoWeather._get_condition(weather_code)
            
            return f"{temp}°C, {condition}, Wind: {wind} km/h"
            
        except Exception as e:
            logger.error(f"Open-Meteo error: {e}")
            return None
    
    @staticmethod
    def get_forecast(city: str = "cuttack", days: int = 3) -> Optional[str]:
        """Get forecast for next few days."""
        coords = OpenMeteoWeather.CITY_COORDS.get(city.lower(), {"lat": 20.46, "lon": 86.02})
        
        try:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": coords["lat"],
                "longitude": coords["lon"],
                "daily": "temperature_2m_max,temperature_2m_min,weathercode",
                "temperature_unit": "celsius",
                "timezone": "auto",
                "forecast_days": days
            }
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            daily = data.get("daily", {})
            
            if not daily:
                return None
            
            results = []
            dates = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            codes = daily.get("weathercode", [])
            
            for i in range(len(dates)):
                date = dates[i].split("-")[-1] + "-" + dates[i].split("-")[-2]
                condition = OpenMeteoWeather._get_condition(codes[i])
                results.append(f"{date}: {min_temps[i]}°-{max_temps[i]}°C, {condition}")
            
            return " | ".join(results)
            
        except Exception as e:
            logger.error(f"Open-Meteo forecast error: {e}")
            return None
    
    @staticmethod
    def _get_condition(code: int) -> str:
        """Convert weather code to condition."""
        conditions = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Fog",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow",
            73: "Moderate snow",
            75: "Heavy snow",
            80: "Rain showers",
            81: "Moderate showers",
            82: "Violent showers",
            95: "Thunderstorm",
            96: "Thunderstorm with hail",
        }
        return conditions.get(code, "Unknown")


def get_weather(city: str = "cuttack") -> Optional[str]:
    """Quick function to get current weather."""
    return OpenMeteoWeather.get_current(city)


def get_forecast(city: str = "cuttack", days: int = 3) -> Optional[str]:
    """Quick function to get forecast."""
    return OpenMeteoWeather.get_forecast(city, days)