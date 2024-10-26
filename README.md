# Weather Monitoring App

## Getting Started

This is a weather monitoring application that retrieves and displays weather data for various cities. Follow the instructions below to set up the application on your local system.

### Prerequisites

- Python 3.x
- MySQL Server

### Open your terminal and run the following command:

pip install -r requirements.txt

### Open MySQL and run the following queries to create the necessary database and table:

CREATE DATABASE weather_data;

USE weather_data;

CREATE TABLE city_weather (
    id INT AUTO_INCREMENT PRIMARY KEY,
    city VARCHAR(50),
    current_temp DECIMAL(5,2),
    climate_conditions VARCHAR(50),
    min_temp DECIMAL(5,2),
    max_temp DECIMAL(5,2),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    humidity INT,
    wind_speed DECIMAL(5,2)
);

### Navigate to database.py and update the following with your MySQL username and password:

USERNAME = 'your_username'
PASSWORD = 'your_password'

### To run the application, use the terminal to execute the following command:

python weatherApp.py

