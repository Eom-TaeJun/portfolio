import os
import random
import time
import pandas as pd
import folium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from PIL import Image

# Set up the path to the WebDriver directly
webdriver_path = "C:/Users/TJ/.wdm/drivers/chromedriver/win64/131.0.6778.85/chromedriver-win32/chromedriver.exe"
webdriver_service = Service(webdriver_path)

def create_map(lat, lon, name, address):
    try:
        # Convert latitude and longitude to float
        lat = float(lat)
        lon = float(lon)

        # Create a map object with satellite imagery
        map_ = folium.Map(location=[lat, lon], zoom_start=15)
        
        # Add satellite tile layer with proper attribution
        folium.TileLayer(
            tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attr='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        ).add_to(map_)

        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Imagery ©2021 TerraMetrics'
        ).add_to(map_)

        # Add a marker for the gas station
        popup_content = f"{name}<br>{address}"
        folium.Marker([lat, lon], popup=popup_content, tooltip=name).add_to(map_)

        # Save the map as an HTML file
        safe_name = ''.join(c for c in name if c.isalnum() or c in (' ', '-', '_'))
        html_file = f'NH_GasStation_{safe_name}.html'
        map_.save(html_file)

        # Open the HTML file in a browser and take a screenshot
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(service=webdriver_service, options=options)
        driver.get('file:///' + os.path.abspath(html_file))
        
        # Wait for the map to load
        time.sleep(2)
        
        # Take a screenshot
        screenshot_path = f'NH_GasStation_{safe_name}.png'
        driver.save_screenshot(screenshot_path)
        driver.quit()

        # Convert the screenshot to JPEG
        image = Image.open(screenshot_path)
        jpeg_path = f'NH_GasStation_{safe_name}.jpg'
        image.convert('RGB').save(jpeg_path, 'JPEG')
        
        # Remove the intermediate files
        os.remove(html_file)
        os.remove(screenshot_path)

        print(f"Map created and saved as JPEG: {jpeg_path}")
        return jpeg_path

    except Exception as e:
        print(f"Error creating map for {name}: {str(e)}")
        return None

try:
    # Load the Excel file
    file_path = "C:/Users/TJ/Downloads/알뜰주유소_위치정보농협.xlsx"
    print("Loading Excel file...")
    df = pd.read_excel(file_path, engine='openpyxl')
    print(f"Data loaded: {len(df)} gas stations found.")

    # Check for required columns
    required_columns = ['name', 'address', 'old_address', 'longitude', 'latitude']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

    # Drop rows where 'address' is NaN
    df = df.dropna(subset=['address'])

    # Filter the data by region
    gyeonggi_df = df[df['address'].str.contains('경기', na=False)]
    seoul_df = df[df['address'].str.contains('서울', na=False)]
    other_df = df[~df['address'].str.contains('경기|서울', na=False)]

    # Sample 5 random entries from each region if possible
    def safe_sample(dataframe, n=5):
        if len(dataframe) >= n:
            return dataframe.sample(n)
        else:
            return dataframe  # If there are less than n rows, return all rows

    gyeonggi_sample = safe_sample(gyeonggi_df)
    seoul_sample = safe_sample(seoul_df)
    other_sample = safe_sample(other_df)

    # Combine the samples into one DataFrame
    final_sample = pd.concat([gyeonggi_sample, seoul_sample, other_sample])

    # Display the selected samples
    print("\nSelected gas stations:")
    for idx, row in final_sample.iterrows():
        print(f"- {row['name']} ({row['address']})")

    print("\nCreating maps...")
    for index, row in final_sample.iterrows():
        try:
            lat = row['latitude']
            lon = row['longitude']
            name = row['name']
            address = row['address']
            print(f"\nProcessing: {name}")
            create_map(lat, lon, name, address)
        except Exception as e:
            print(f"Error processing data for {name}: {str(e)}")

except Exception as e:
    print(f"Error running program: {str(e)}")
