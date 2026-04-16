"""
Weather API Module - Smart weather fetching with fallback support
Uses 7Timer ASTRO for detailed data, wttr.in as backup
"""
import requests
import re
import xml.etree.ElementTree as ET
from typing import Optional, Dict, Any
from intelli.core.logger import log_info, log_warning, log_error


# Weather interpretation mappings
CLOUD_COVER_MAP = {
    1: "Clear",
    2: "Clear",
    3: "Mostly Clear",
    4: "Partly Cloudy",
    5: "Mostly Cloudy",
    6: "Cloudy",
    7: "Overcast",
    8: "Obscured",
    9: "Foggy"
}

SEEING_MAP = {
    1: "Poor",
    2: "Below Average",
    3: "Average",
    4: "Good",
    5: "Excellent",
    6: "Excellent"
}

TRANSPARENCY_MAP = {
    1: "Very Poor",
    2: "Poor",
    3: "Average",
    4: "Good",
    5: "Excellent",
    6: "Excellent",
    7: "Outstanding"
}

RAIN_TYPE_MAP = {
    "none": "No Rain",
    "rain": "Light Rain",
    "snow": "Snow",
    "frzg": "Freezing Rain"
}

WIND_DIR_MAP = {
    "N": "North", "S": "South", "E": "East", "W": "West",
    "NE": "Northeast", "NW": "Northwest", "SE": "Southeast", "SW": "Southwest"
}


def _parse_user_query(query: str) -> Dict[str, Any]:
    """Parse user's weather query to determine what they want."""
    query = query.lower()
    
    result = {
        "city": "cuttack",  # default
        "forecast_type": "current",  # current, hourly, tomorrow, extended
        "detail_level": "simple",  # simple or detailed (astro data)
        "specific_asking": []  # specific things asked
    }
    
    # Extract city
    cities = ["cuttack", "delhi", "mumbai", "bangalore", "chennai", "kolkata", "hyderabad", "pune", "bhubaneswar"]
    for city in cities:
        if city in query:
            result["city"] = city
            break
    
    # Determine forecast type
    if "tomorrow" in query:
        result["forecast_type"] = "tomorrow"
    elif "hourly" in query or "hours" in query:
        result["forecast_type"] = "hourly"
    elif "week" in query or "7 day" in query or "weekend" in query:
        result["forecast_type"] = "extended"
    
    # Check for specific asks
    if any(word in query for word in ["temperature", "temp", "hot", "cold", "warm", "degree"]):
        result["specific_asking"].append("temperature")
    if any(word in query for word in ["rain", "raining", "umbrella", "wet"]):
        result["specific_asking"].append("rain")
    if any(word in query for word in ["cloud", "cloudy", "sunny", "clear"]):
        result["specific_asking"].append("clouds")
    if any(word in query for word in ["wind", "windy"]):
        result["specific_asking"].append("wind")
    if any(word in query for word in ["astronomy", "astro", "star", "stargazing", "seeing"]):
        result["detail_level"] = "detailed"
        result["specific_asking"].append("astronomy")
    
    return result


def _fetch_7timer(city: str = "cuttack") -> Optional[Dict]:
    """Fetch weather from 7Timer ASTRO API."""
    try:
        # 7Timer uses coordinates or location codes
        location_map = {
            "cuttack": "12542",  # Cuttack, Odisha
            "delhi": "10705", "mumbai": "10476", "bangalore": "10931",
            "chennai": "11177", "kolkata": "11195", "hyderabad": "11022",
            "pune": "11164", "bhubaneswar": "12495"
        }
        
        loc_code = location_map.get(city.lower(), "12542")
        
        url = f"https://www.7timer.info/bin/astro.php?lon=86.25&lat=20.46&ac=0&unit=metric&output=xml&tzshift=0"
        
        log_info(f"Fetching 7Timer weather for {city}")
        response = requests.get(url, timeout=8)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            init_time = root.find("init").text if root.find("init") is not None else "Unknown"
            
            dataseries = []
            for data in root.findall(".//data"):
                entry = {
                    "timepoint": int(data.find("timepoint").text) if data.find("timepoint") is not None else 0,
                    "cloudcover": int(data.find("cloudcover").text) if data.find("cloudcover") is not None else 0,
                    "seeing": int(data.find("seeing").text) if data.find("seeing") is not None else 0,
                    "transparency": int(data.find("transparency").text) if data.find("transparency") is not None else 0,
                    "lifted_index": int(data.find("lifted_index").text) if data.find("lifted_index") is not None else 0,
                    "rh2m": int(data.find("rh2m").text) if data.find("rh2m") is not None else 0,
                    "wind_dir": data.find("wind10m_direction").text if data.find("wind10m_direction") is not None else "N",
                    "wind_speed": int(data.find("wind10m_speed").text) if data.find("wind10m_speed") is not None else 0,
                    "temp": int(data.find("temp2m").text) if data.find("temp2m") is not None else 0,
                    "prec_type": data.find("prec_type").text if data.find("prec_type") is not None else "none"
                }
                dataseries.append(entry)
            
            return {
                "source": "7Timer",
                "init": init_time,
                "data": dataseries
            }
    except Exception as e:
        log_warning(f"7Timer fetch error: {e}")
    
    return None


def _fetch_wttr(city: str = "cuttack") -> Optional[Dict]:
    """Fetch weather from wttr.in as fallback."""
    try:
        url = f"https://wttr.in/{city}?format=%t|%C|%h|%w|%p"
        log_info(f"Fetching wttr.in weather for {city}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            parts = response.text.strip().split('|')
            if len(parts) >= 4:
                return {
                    "source": "wttr.in",
                    "temp": parts[0].replace('+', ''),
                    "condition": parts[1].strip(),
                    "humidity": parts[2].strip(),
                    "wind": parts[3].strip() if len(parts) > 3 else "N/A",
                    "precipitation": parts[4].strip() if len(parts) > 4 else "N/A"
                }
    except Exception as e:
        log_warning(f"wttr.in fetch error: {e}")
    
    return None


def _format_7timer_response(data: Dict, query_info: Dict) -> str:
    """Format 7Timer data into readable response."""
    if not data.get("data"):
        return "No weather data available."
    
    dataseries = data["data"]
    details = query_info["specific_asking"]
    forecast_type = query_info["forecast_type"]
    
    # Get current/next forecast (first entry is usually +3h from now)
    current = dataseries[0] if dataseries else None
    
    if forecast_type == "hourly" or "astronomy" in details:
        # Return more detailed hourly data
        return _format_hourly_forecast(dataseries, details)
    
    elif forecast_type == "tomorrow":
        # Find tomorrow's data (around 24h)
        tomorrow = next((d for d in dataseries if d["timepoint"] == 24), dataseries[8] if len(dataseries) > 8 else current)
        return _format_day_summary(tomorrow, "Tomorrow")
    
    elif forecast_type == "extended":
        # Summarize the week
        return _format_extended_forecast(dataseries)
    
    else:
        # Current weather summary
        if current:
            return _format_day_summary(current, "Today")
    
    return "Weather data unavailable."


def _format_day_summary(data: Dict, day: str) -> str:
    """Format a single day's summary."""
    temp = data.get("temp", "?")
    cloud = CLOUD_COVER_MAP.get(data.get("cloudcover", 1), "Unknown")
    rain = RAIN_TYPE_MAP.get(data.get("prec_type", "none"), "None")
    wind_dir = WIND_DIR_MAP.get(data.get("wind_dir", "N"), "North")
    wind_speed = data.get("wind_speed", 0)
    
    return f"{day}: {temp}°C, {cloud.lower()}, {rain.lower()}, Wind: {wind_dir} at {wind_speed} km/h"


def _format_hourly_forecast(dataseries: list, details: list) -> str:
    """Format hourly forecast."""
    response_parts = []
    
    # Show next 4 time points (12 hours)
    for entry in dataseries[:4]:
        time_h = entry.get("timepoint", 0)
        if time_h == 0:
            time_str = "Now"
        else:
            time_str = f"+{time_h}h"
        
        temp = entry.get("temp", "?")
        
        if "temperature" in details:
            response_parts.append(f"{time_str}: {temp}°C")
        elif "rain" in details:
            rain = RAIN_TYPE_MAP.get(entry.get("prec_type", "none"), "None")
            response_parts.append(f"{time_str}: {rain}")
        elif "clouds" in details:
            cloud = CLOUD_COVER_MAP.get(entry.get("cloudcover", 1), "Unknown")
            response_parts.append(f"{time_str}: {cloud}")
        elif "wind" in details:
            wind_dir = WIND_DIR_MAP.get(entry.get("wind_dir", "N"), "N")
            wind_speed = entry.get("wind_speed", 0)
            response_parts.append(f"{time_str}: {wind_dir} at {wind_speed} km/h")
        elif "astronomy" in details:
            seeing = SEEING_MAP.get(entry.get("seeing", 6), "Good")
            cloud = CLOUD_COVER_MAP.get(entry.get("cloudcover", 1), "Unknown")
            response_parts.append(f"{time_str}: Seeing {seeing}, {cloud}")
        else:
            cloud = CLOUD_COVER_MAP.get(entry.get("cloudcover", 1), "Unknown")
            response_parts.append(f"{time_str}: {temp}°C, {cloud.lower()}")
    
    return " | ".join(response_parts)


def _format_extended_forecast(dataseries: list) -> str:
    """Format extended 3-day forecast."""
    # Group by day (every 8 timepoints ≈ 24h)
    days = ["Today", "Tomorrow", "Day After"]
    summaries = []
    
    for i, day_name in enumerate(days):
        if i * 8 < len(dataseries):
            day_data = dataseries[i * 8]
            summaries.append(_format_day_summary(day_data, day_name))
    
    return " | ".join(summaries)


def get_weather(query: str) -> str:
    """
    Main weather function - smart weather fetching.
    
    Args:
        query: User's weather query (e.g., "what's the weather in cuttack", "will it rain tomorrow")
    
    Returns:
        Natural language weather response
    """
    log_info(f"Weather query: {query}")
    
    # Parse what the user wants
    query_info = _parse_user_query(query)
    city = query_info["city"]
    
    # Try 7Timer first (more detailed)
    data = _fetch_7timer(city)
    
    # Fallback to wttr.in
    if not data:
        log_info("Falling back to wttr.in")
        wttr_data = _fetch_wttr(city)
        if wttr_data:
            return _format_wttr_response(wttr_data, query_info)
    
    if data:
        return _format_7timer_response(data, query_info)
    
    # Both failed
    return "I'm having trouble fetching weather data right now. Please check your internet connection and try again."


def _format_wttr_response(data: Dict, query_info: Dict) -> str:
    """Format wttr.in data response."""
    temp = data.get("temp", "?")
    condition = data.get("condition", "Unknown")
    humidity = data.get("humidity", "N/A")
    wind = data.get("wind", "N/A")
    
    return f"Current weather in {query_info['city'].title()}: {temp}, {condition}. Humidity: {humidity}, Wind: {wind}"


# Standalone test
if __name__ == "__main__":
    print("Testing weather API...")
    print("\n1. Current weather:")
    print(get_weather("weather"))
    print("\n2. Temperature:")
    print(get_weather("what's the temperature"))
    print("\n3. Rain forecast:")
    print(get_weather("will it rain tomorrow"))
    print("\n4. Astronomy:")
    print(get_weather("astronomy conditions"))
