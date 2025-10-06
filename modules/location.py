# Location.py
 
import openrouteservice
import requests
 
api_key = "5b3ce3597851110001cf6248870c5cfce0e6473bbc1f59b20c97df3b"
client = openrouteservice.Client(key=api_key)
 
def get_coordinates(place_name):
    url = "https://api.openrouteservice.org/geocode/search"
    params = {
        "api_key": api_key,
        "text": place_name,
        "size": 1
    }
 
    res = requests.get(url, params=params)
    data = res.json()
    if 'features' in data and len(data['features']) > 0:
        return data['features'][0]['geometry']['coordinates']
    return None
 
def get_distance_info(start, end):
    start_coords = get_coordinates(start)
    end_coords = get_coordinates(end)
 
    if not start_coords or not end_coords:
        return "Sorry, I couldn't find one or both of those locations."
 
    try:
        route = client.directions(
            coordinates=[start_coords, end_coords],
            profile='driving-car',
            format='geojson'
        )
    except Exception as e:
        print(f"❌ ORS error: {e}")
        return "Sorry, I couldn't find a route between those two places. Try being more specific like using city names."
 
    distance_km = route['features'][0]['properties']['segments'][0]['distance'] / 1000
    duration_min = route['features'][0]['properties']['segments'][0]['duration'] / 60
 
    return f"The distance from {start} to {end} is {distance_km:.2f} kilometers. It will take about {duration_min:.1f} minutes by car."