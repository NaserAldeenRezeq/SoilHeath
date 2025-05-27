from typing import Any, Dict, Tuple


def split_soil_elements(query: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extracts soil and weather elements from a structured query string.

    Args:
        query (str): Formatted string containing [SoilData] and [WeatherData].

    Returns:
        Tuple[Dict[str, Any], Dict[str, Any]]: Two dictionaries for soil and weather data.
    """
    soil_data: Dict[str, str] = {}
    weather_data: Dict[str, str] = {}
    current_section = None

    lines = query.strip().splitlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        if line.startswith("[") and "]" in line:
            section_end = line.find("]") + 1
            section_name = line[1:section_end - 1]
            current_section = section_name

            inline_data = line[section_end:].strip()
            if inline_data:
                entries = [e.strip() for e in inline_data.split(",") if e.strip()]
                for entry in entries:
                    if ": " in entry:
                        key, value = entry.split(": ", 1)
                        if current_section == "SoilData":
                            soil_data[key.strip()] = value.strip()
                        elif current_section == "WeatherData":
                            weather_data[key.strip()] = value.strip()
        elif current_section:
            entries = [e.strip() for e in line.split(",") if e.strip()]
            for entry in entries:
                if ": " in entry:
                    key, value = entry.split(": ", 1)
                    if current_section == "SoilData":
                        soil_data[key.strip()] = value.strip()
                    elif current_section == "WeatherData":
                        weather_data[key.strip()] = value.strip()

    return soil_data, weather_data


if __name__ == "__main__":
    query = """[SoilData] Soil PH: 6.5,
                               Nitrogen: High, Phosphorus: Medium, Potassium: Low, Soil Texture: Loamy,
                               Soil Moisture: Moderate, Organic Matter: Rich 
                               [WeatherData] Temperature: 22°C, Humidity: 60%, Wind Speed: 10 km/h, Precipitation: 2 mm"""

    soil, weather = split_soil_elements(query)

    print("Soil Data:")
    for key, value in soil.items():
        print(f"  {key}: {value}")

    print("\nWeather Data:")
    for key, value in weather.items():
        print(f"  {key}: {value}")
