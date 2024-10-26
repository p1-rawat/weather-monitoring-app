import mysql.connector

def insert_weather_data(city, current_temp, climate_conditions, min_temp, max_temp, timestamp, humidity, wind_speed):
    try:
        # Connect to the MySQL database
        conn = mysql.connector.connect(
            host="localhost",
            user="root",   # Replace with your MySQL username
            password="0503",  # Replace with your MySQL password
            database="weather_data"  # Ensure this matches the database you created
        )
        cursor = conn.cursor()

        sql = """
        INSERT INTO city_weather (city, current_temp, climate_conditions, min_temp, max_temp, timestamp, humidity, wind_speed)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (city, current_temp, climate_conditions, min_temp, max_temp, timestamp, humidity, wind_speed)
        
        cursor.execute(sql, values)
        conn.commit()

        print(f"Data for {city} inserted successfully.")
    
    except mysql.connector.Error as err:
        print(f"Error: {err}")
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

