import requests
 
api_key = "5d64f48fa3aa48b8812161232251007"
 
def get_weather(city):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    response = requests.get(url)
    data = response.json()
 
    try:
        temp = data['current']['temp_c']
        location = data['location']['name']
        return f"The current temperature in {location} is {temp} degrees Celsius."
    except KeyError:
        return "Sorry, I couldn't retrieve the weather. Please check the city name."