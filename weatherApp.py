from tkinter import *
from tkinter import ttk
import requests
import datetime
from database import insert_weather_data  # Import the function to insert data into the MySQL database
import matplotlib.pyplot as plt 
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg 

INTERVAL = 300000  # 300000 ms = 5 minutes

cities = ["Delhi", "Mumbai", "Chennai", "Bangalore", "Kolkata", "Hyderabad"]  
alert_count = {city: 0 for city in cities}  
last_alert_time = {city: None for city in cities} 

temperature_data = []
timestamp_data = [] 

def reset_alert_counts():
    """Reset alert counts at the end of the day."""
    current_time = datetime.datetime.now()
    if current_time.hour == 0 and current_time.minute == 0: 
        for city in cities:
            alert_count[city] = 0 

def plot_temperature_graph():
    """Plot the temperature graph below the temperature threshold and weather conditions."""
    fig, ax = plt.subplots(figsize=(8, 4))  
    ax.clear() 
    
    now = datetime.datetime.now()
    six_hours_ago = now - datetime.timedelta(hours=6)

    filtered_temps = []
    filtered_times = []
    
    for i in range(len(timestamp_data)):
        if timestamp_data[i] >= six_hours_ago:
            filtered_temps.append(temperature_data[i])
            filtered_times.append(timestamp_data[i].timestamp()) 

    ax.plot(filtered_times, filtered_temps, label='Temperature (°C)', marker='o')
    ax.axhline(y=float(temp_threshold_entry.get() or 25), color='r', linestyle='--', label='Temperature Threshold')  # Add threshold line
    ax.set_title('Temperature Over Last 6 Hours')
    ax.set_xlabel('Time')
    ax.set_ylabel('Temperature (°C)')
    ax.set_ylim(0, 60) 
    ax.legend()
    ax.grid()
    
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: datetime.datetime.fromtimestamp(x).strftime('%H:%M')))
    
    fig.autofmt_xdate()  

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().place(x=400, y=185, width=600, height=300)  # Adjust position to move up by 75 pixels

def getData(event=None): 
    city = cityName.get()
    if city == "Select the city":
        return

    data = requests.get("https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=84be0fe094690fcd40deb780b365aaff").json()
    
    if data.get("cod") != 200:
        alert_label.config(text=f"Error fetching data for {city}: {data.get('message', 'Unknown error')}", fg="red", bg="purple")
        return

    climateName.config(text=data["weather"][0]["main"])
    
    # Current Temperature
    current_temp = round(data['main']['temp'] - 273.15, 2)  # Convert Kelvin to Celsius
    current_temp_value.config(text=f"{current_temp}°C")
    
    # Feels Like
    feelsLikevalue.config(text=f"{round(data['main']['feels_like'] - 273.15, 2)}°C")  # Convert Kelvin to Celsius
    
    # Time
    unix_timestamp = data["dt"]
    update_time = datetime.datetime.fromtimestamp(unix_timestamp)
    formatted_time = update_time.strftime("%Y-%m-%d %H:%M:%S")
    time_value.config(text=formatted_time)
    
    # Maximum Temperature
    max_temp = round(data['main']['temp_max'] - 273.15, 2)  # Convert Kelvin to Celsius
    maxTempvalue.config(text=f"{max_temp}°C")
    
    # Minimum Temperature
    min_temp = round(data['main']['temp_min'] - 273.15, 2)  # Convert Kelvin to Celsius
    minTempValue.config(text=f"{min_temp}°C")
    
    # Humidity
    humidity = data['main']['humidity']  # Humidity in percentage
    humidity_value.config(text=f"{humidity}%")
    
    # Wind Speed
    wind_speed = data['wind']['speed']  # Wind speed in m/s
    wind_value.config(text=f"{wind_speed} m/s")
    
    # Check for temperature and climate alerts
    temp_threshold = float(temp_threshold_entry.get() or 25)  # Default to 25°C if no input
    selected_climate = climate_threshold.get()
    
    # Track alerts for the city
    if current_temp > temp_threshold:
        if alert_count[city] < 2:  # Only trigger if count is less than 2
            alert_label.config(text=f"Alert: The temperature in {city} exceeds {temp_threshold}°C!", fg="red", bg="purple")
            alert_count[city] += 1  # Increment alert count for the city
            last_alert_time[city] = datetime.datetime.now()  # Set the last alert time
    elif data["weather"][0]["main"] == selected_climate:
        if alert_count[city] < 2:  # Only trigger if count is less than 2
            alert_label.config(text=f"Alert: The weather in {city} is {selected_climate}!", fg="red", bg="purple")
            alert_count[city] += 1  # Increment alert count for the city
            last_alert_time[city] = datetime.datetime.now()  # Set the last alert time
    else:
        alert_label.config(text="", bg="purple")  # Clear alert if conditions are normal

    # *** Insert data into MySQL Database ***
    insert_weather_data(city, current_temp, data["weather"][0]["main"], min_temp, max_temp, formatted_time, humidity, wind_speed)

    # Store the temperature and timestamp for plotting
    temperature_data.append(current_temp)
    timestamp_data.append(datetime.datetime.now())  
    plot_temperature_graph() 

def fetchWeatherForAllCities():
    for city in cities:
        data = requests.get("https://api.openweathermap.org/data/2.5/weather?q=" + city + "&appid=84be0fe094690fcd40deb780b365aaff").json()

        # Check if response is successful
        if data.get("cod") != 200:
            print(f"Error fetching data for {city}: {data.get('message', 'Unknown error')}")
            continue

        # Current Temperature
        current_temp = round(data['main']['temp'] - 273.15, 2)  # Convert Kelvin to Celsius
        
        # Maximum Temperature
        max_temp = round(data['main']['temp_max'] - 273.15, 2)  # Convert Kelvin to Celsius
        
        # Minimum Temperature
        min_temp = round(data['main']['temp_min'] - 273.15, 2)  # Convert Kelvin to Celsius
        
        # Humidity
        humidity = data['main']['humidity']  # Humidity in percentage
        
        # Wind Speed
        wind_speed = data['wind']['speed']  # Wind speed in m/s
        
        # Insert data into MySQL Database
        unix_timestamp = data["dt"]
        update_time = datetime.datetime.fromtimestamp(unix_timestamp)
        formatted_time = update_time.strftime("%Y-%m-%d %H:%M:%S")

        insert_weather_data(city, current_temp, data["weather"][0]["main"], min_temp, max_temp, formatted_time, humidity, wind_speed)

    win.after(INTERVAL, fetchWeatherForAllCities)

def setInterval(interval):
    global INTERVAL
    INTERVAL = interval * 60000 

win = Tk()
win.title("Weather App")
win.config(bg="purple")
win.geometry("1025x515") 

# Alert Label at the top center
alert_label = Label(win, text="", font=("Arial", 15), fg="red", bg="purple")
alert_label.place(relx=0.5, y=15, anchor='center') 

labelName = Label(win, text="Weather App", font=("Roboto", 25, "bold"))
labelName.place(x=200, y=30, height=50, width=310)

cityName = StringVar(value="Select the city")
com = ttk.Combobox(win, text="Select City", values=["Select the city"] + cities, font=("Arial", 20), justify="center", textvariable=cityName, state="readonly")
com.place(x=25, y=105, height=40, width=310)

com.bind("<<ComboboxSelected>>", getData)

# Weather Climate
climate = Label(win, text="Weather Climate: ", font=("Arial", 12), anchor='e', justify='right')
climate.place(x=25, y=180, height=30, width=150)  # Set y coordinate directly to 180

climateName = Label(win, text="", font=("Arial", 12))
climateName.place(x=185, y=180, height=30, width=150)  # Set y coordinate directly to 180

# Current Temperature
current_temp = Label(win, text="Current Temp: ", font=("Arial", 12), anchor='e', justify='right')
current_temp.place(x=25, y=220, height=30, width=150)  # Set y coordinate directly to 220

current_temp_value = Label(win, text="", font=("Arial", 12))
current_temp_value.place(x=185, y=220, height=30, width=150)  # Set y coordinate directly to 220

# Feels Like
feelsLike = Label(win, text="Feels Like: ", font=("Arial", 12), anchor='e', justify='right')
feelsLike.place(x=25, y=260, height=30, width=150)  # Set y coordinate directly to 260

feelsLikevalue = Label(win, text="°C", font=("Arial", 12))
feelsLikevalue.place(x=185, y=260, height=30, width=150)  # Set y coordinate directly to 260

# Time
time_label = Label(win, text="Time (Updated): ", font=("Arial", 12), anchor='e', justify='right')
time_label.place(x=25, y=300, height=30, width=150)  # Set y coordinate directly to 300

time_value = Label(win, text="", font=("Arial", 12))
time_value.place(x=185, y=300, height=30, width=150)  # Set y coordinate directly to 300

# Maximum Temperature
maxTemp = Label(win, text="Max Temp: ", font=("Arial", 12), anchor='e', justify='right')
maxTemp.place(x=25, y=340, height=30, width=150)  # Set y coordinate directly to 340

maxTempvalue = Label(win, text="°C", font=("Arial", 12))
maxTempvalue.place(x=185, y=340, height=30, width=150)  # Set y coordinate directly to 340

# Minimum Temperature
minTemp = Label(win, text="Min Temp: ", font=("Arial", 12), anchor='e', justify='right')
minTemp.place(x=25, y=380, height=30, width=150)  # Set y coordinate directly to 380

minTempValue = Label(win, text="°C", font=("Arial", 12))
minTempValue.place(x=185, y=380, height=30, width=150)  # Set y coordinate directly to 380

# Humidity
humidity_label = Label(win, text="Humidity: ", font=("Arial", 12), anchor='e', justify='right')
humidity_label.place(x=25, y=420, height=30, width=150)

humidity_value = Label(win, text="%", font=("Arial", 12))
humidity_value.place(x=185, y=420, height=30, width=150)

# Wind Speed
wind_label = Label(win, text="Wind Speed: ", font=("Arial", 12), anchor='e', justify='right')
wind_label.place(x=25, y=460, height=30, width=150)

wind_value = Label(win, text="m/s", font=("Arial", 12))
wind_value.place(x=185, y=460, height=30, width=150)

# Threshold Inputs
Label(win, text="Temperature Threshold (°C):", font=("Arial", 12)).place(x=400, y=105) 
temp_threshold_entry = Entry(win, font=("Arial", 12))
temp_threshold_entry.place(x=630, y=105, width=100)  

weather_condition_label = Label(win, text="Weather Condition:", font=("Arial", 12))
weather_condition_label.place(x=400, y=145, width=200) 

climate_threshold = StringVar(value="Clear")
climate_com = ttk.Combobox(win, text="Select Condition", values=["Clear", "Clouds", "Rain", "Drizzle", "Thunderstorm"], font=("Arial", 12), textvariable=climate_threshold, state="readonly")
climate_com.place(x=630, y=145, width=100)

win.after(0, getData)

fetchWeatherForAllCities()

win.after(60000, reset_alert_counts) 

win.mainloop()
