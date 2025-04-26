# OpenWeather by citizen
import requests
from colorama import init, Fore, Style
import json

# Codes for weather status
WEATHER_CODES = {
    0:"Clear sky",
    1:"Mainly clear", 2:"Partly cloudy", 3:"Overcast",
    45:"Foggy", 46:"Depositing rime fog",
    51:"Light drizzle", 53:"Moderate drizzle", 55:"Dense drizzle",
    61:"Slight rain", 63:"Moderate rain", 65:"Heavy rain",
    66:"Light freezing rain", 67: "Heavy freezing rain",
    71:"Slight snow fall", 73:"Moderate snow fall", 75:"Intense snow fall",
    77:"Snow grains",
    80:"Slight rain shower", 81:"Moderate rain shower", 82:"Violent rain shower",
    85:"Slight snow shower", 86:"Heavy snow shower",
    95:"Thunderstorm",
    96:"Thunderstorm with slight hail", 99:"Thunderstorm with heavy hail"
}

# Codes for defining if it's day or night
DAYNIGHT = {0: 'Day', 1: 'Night'}

# ---------- Main program ---------- #
class WeatherApp:

    # ----- Defining variables for WeatherApp ----- #
    def __init__(self, config_file='config.json'):
        self.load_config(config_file)
        self.favorites = self.config.get('favorites', [])

        
    # ----- Load config.json ----- #
    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            self.config = json.load(file)
            self.API_URL = self.config['api_url']
            self.LOCATIONS = self.config['default_locations']
            self.LOWLOCATIONS = {city.lower(): city for city in self.LOCATIONS.keys()}

            
    # ----- Save favorite locations  ----- #
    def save_favorites(self):
        self.config['favorites'] = self.favorites
        with open('config.json', 'w') as file:
            json.dump(self.config, file, indent=4)


    # ----- Menu options  ----- #
    def display_menu(self):
        print("Welcome to the OpenWeather")
        print("="*30)
        print("1. Check weather of a location")
        print("2. Add a location to list")
        print("3. Favorite a location")
        print("4. Version and credits")
        print("5. Exit")
        print("="*30)


    # ----- All inputs available here. ----- #
    def run(self):
        init(autoreset = True)
        while True:
            self.display_menu()
            opt = input("Enter a number between (1-5): ")

            # --- Select city --- #
            if opt == "1":
                print("1. Favorited cities\n2. All cities in the app")
                rep = input("Enter your choosing (1 or 2): ")
                
                # Select from favorites
                if rep == "1":
                    fcity = self.select_fcity()
                    if fcity and fcity in self.LOWLOCATIONS:
                        wapi = WeatherAPI(self.LOWLOCATIONS[fcity], self.LOCATIONS, self.API_URL)
                        wapi.fetch_data()
                        wapi.display_daily_weather()
                        wapi.display_current_temperature()

                # Select from list        
                elif rep == "2":
                    city = self.select_city()
                    if city in self.LOWLOCATIONS:
                        wapi = WeatherAPI(self.LOWLOCATIONS[city], self.LOCATIONS, self.API_URL)
                        wapi.fetch_data()
                        wapi.display_daily_weather()
                        wapi.display_current_temperature()
                    else:
                        print("Invalid city name. Please try again.\n")

            # --- Add city to list  --- #
            elif opt == "2":
                self.add_city()

            # --- Favorite a city from list --- #
            elif opt == "3":
                self.favorite_city()

            # --- Version control and credits  --- #
            elif opt == "4":
                print("#v0.1a# by citizen:\n- Github: https://github.com/TheCitizenOne\n- Lemmy: https://lemmy.world/u/the_citizen\nPlease write your thoughts and suggestions.\n")

            # --- Exit from program  --- #
            elif opt == "5":
                print("Quitting...")
                break
            
            else:
                print("Invalid option. Please enter a number between 1 and 5.\n")


    # ----- City selection from list  ----- #
    def select_city(self):
        print("#", "Available cities:")
        
        for city in self.LOCATIONS.keys():
            print(f"- {city}")
        city = input("Enter the city name: ").strip().lower()
        return city


    # ----- City selection from favorites ----- #
    def select_fcity(self):
        if self.favorites:
            print("#", "Favorited cities:")
            
            for city in self.favorites:
                print(f"- {city}")
            fcity = input("Enter the city name: ").strip().lower()
            return fcity
        
        else:
            print("You have no favorite cities yet.\n")
            return None


    # ----- Adding city to list ----- #
    def add_city(self):
        self.city = input("Enter the name of city: ")
        
        if self.city.lower() in self.LOCATIONS:
            print(f"{self.city} is already in the list of locations.\n")
        try:
            self.lat = float(input("Write the latitude of the city: "))
            self.lon = float(input("Write the longitude of the city: "))
            
        except ValueError:
            print("Invalid input. Please enter numeric values for latitude and longitude.")
            return

        if self.city:
            self.LOCATIONS[self.city] = {'lat': self.lat, 'lon': self.lon}
            self.LOWLOCATIONS[self.city.lower()] = self.city
            
            print(f"{self.city} added to locations.")
            print(self.LOCATIONS)


    # ----- Favorite a city ----- #
    def favorite_city(self):
        city = input("Enter the name of the city to favorite: ").strip()
        city_lower = city.lower()
        
        if city_lower in self.LOWLOCATIONS:
            if city not in self.favorites:
                self.favorites.append(city)
                self.save_favorites()
                print(f"{city} has been added to your favorites.\n")
            else:
                print(f"{city} is already in your favorites.\n")
                
        else:
            print("City not found. Please add the city first.\n")

            
# ---------- API Networking ---------- #      
class WeatherAPI:
    
    # ----- Defining variables for WeatherAPI ----- #
    def __init__(self, location, locations, api_url):
        if location in locations:
            self.location = location
            self.lat = locations[location]['lat']
            self.lon = locations[location]['lon']
            self.API_URL = api_url
            self.current_data = None
            self.daily_data = None
            
        else:
            raise ValueError(f"Location '{location}' not found in LOCATIONS.\n")

        
    # ----- Fetching data of a location from api -----#
    def fetch_data(self):
        try:
            response = requests.get(f"{self.API_URL}?latitude={self.lat}&longitude={self.lon}&current=temperature_2m,apparent_temperature,relative_humidity_2m,is_day&daily=weather_code")
            
            response.raise_for_status()
            result = response.json()

            if "current" in result and "daily" in result:
                self.current_data = result['current']
                self.daily_data = result['daily']
            else:
                print(f"{Fore.YELLOW}Result{Style.RESET_ALL}: Weather data not found in the response.\n")

        except requests.exceptions.HTTPError as http_err:
            print(f"{Fore.RED}HTTP error occured:{Style.RESET_ALL} {http_err}")
            
        except requests.exceptions.ConnectionError as conn_err:
            print(f"{Fore.RED}Connection error occurred:{Style.RESET_ALL} {conn_err}")
            
        except requests.exceptions.Timeout as timeout_err:
            print(f"{Fore.RED}Timeout error occurred:{Style.RESET_ALL} {timeout_err}")
            
        except requests.exceptions.RequestException as req_err:
            print(f"{Fore.RED}An error occurred:{Style.RESET_ALL} {req_err}")

            
    # ----- Display 'current' temperature of a location ----- #
    def display_current_temperature(self):
        if self.current_data:
            current_temp = self.current_data.get('temperature_2m')
            apparent_temp = self.current_data.get('apparent_temperature')
            humidity = self.current_data.get('relative_humidity_2m')
            daynight = self.current_data.get('is_day')
            
            print(f"Current temperature in {self.location}: {current_temp}°C")
            print(f"Feels like: {apparent_temp}°C")
            print(f"Relative humidity: {humidity}%")
            print(f"Day or night: {DAYNIGHT[daynight]}")
            print()
            
        else:
            print(Fore.YELLOW + "Result:" + Style.RESET_ALL + "No temperature information is found.")
            print()


    # ----- Display 'daily' weather of a location  ----- #
    def display_daily_weather(self):
        if self.daily_data:
            wcodes = self.daily_data.get('weather_code')
            wdates = self.daily_data.get('time')
            
            print()
            print("-"*10, "Weekly Report", "-"*10)

            for i, (wcode, wdate) in enumerate(zip(wcodes, wdates)):
                weather_description = WEATHER_CODES.get(wcode, "Unknown weather code")
                if i == 0:
                    print(f"Today ({wdate}): {weather_description}")
                elif i == 1:
                    print(f"Tomorrow ({wdate}): {weather_description}")
                else:
                    print(f"{i} days later ({wdate}): {weather_description}")
            print()
            
        else:
            print(Fore.YELLOW + "Result:" + Style.RESET_ALL + "No weather information is found.")
            print()            

            
# ----- Init program ----- #
if __name__ == "__main__":
    app = WeatherApp()
    app.run()
