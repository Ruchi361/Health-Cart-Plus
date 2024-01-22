from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import csv
import time

# Function to fetch additional information from a given URL
def fetch_additional_info(url):
    # Set up the WebDriver
    driver = webdriver.Chrome()
    driver.get(url)

    try:
        # Wait for the close button to be clickable (if it's present)
        close_popup_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'UpdateCityModal__cancel-btn___2jWwS'))
        )
        close_popup_button.click()
        time.sleep(3)  # Allow dynamic content to load
    except (TimeoutException, NoSuchElementException):
        # Handle the case when the close button is not present or not clickable
        print("Popup close button not found or not clickable. Continuing without closing the popup.")

    # Extract information using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Extracting the Name, Brand Name, Rating, Number of Rating, Key Benefits, Key Ingredients
    name_of_medicine_element = soup.find('h1', {'class': 'ProductTitle__product-title___3QMYH'})
    name_of_medicine = name_of_medicine_element.text.strip() if name_of_medicine_element else 'NA'

    brand_name_element = soup.find('div', {'class': 'ProductTitle__marketer___7Wsj9'})
    brand_name = brand_name_element.text.strip() if brand_name_element else 'NA'

    rating_element = soup.find('div', {'class': 'RatingDisplay__ratings-container___3oUuo'})
    rating = rating_element.text.strip() if rating_element else 'NA'

    num_rating_element = soup.find('span', {'class': 'RatingDisplay__ratings-header___ZNj5b'})
    num_rating = num_rating_element.text.strip() if num_rating_element else 'NA'

    key_benefits_element = soup.find('div', {'class': 'ProductHighlights__product-highlights___2jAF5'})
    key_benefits_items = key_benefits_element.find_all('li') if key_benefits_element else []
    key_benefits_data = [item.text.strip() for item in key_benefits_items] if key_benefits_items else 'NA'
    key_benefits = '\n'.join(f'{index + 1}. {element}' for index, element in enumerate(key_benefits_data, start=0)) if key_benefits_data != 'NA' else 'NA'

    key_ingredients = extract_key_ingredients(soup)

    # Close the WebDriver
    driver.quit()

    return name_of_medicine, brand_name, rating, num_rating, key_benefits, key_ingredients

def extract_key_ingredients(soup):
    key_ingredients_start_tag = soup.find(['strong', 'b'], text=['Key Ingredients:', 'Key Ingredients'])
    if key_ingredients_start_tag:
        key_ingredients = []
        next_tag = key_ingredients_start_tag.find_next(['br', 'strong', 'b', 'ul'])
        while next_tag and next_tag.name != 'strong' and next_tag.name != 'b':
            if next_tag.name == 'br':
                key_ingredients.append(next_tag.find_next(text=True).strip())
            elif next_tag.name == 'ul':
                key_ingredients.extend([li.get_text(strip=True) for li in next_tag.find_all('li')])
            next_tag = next_tag.find_next(['br', 'strong', 'b', 'ul'])
        return key_ingredients
    return []

# Specify the path to your CSV files
csv_file_path_input = 'medicine_name_data_1200.csv'
csv_file_path_output = 'medicine_details.csv'

# Create a list to store the fetched information
all_additional_info = []

# Read data from the CSV file and extract '1Mg_URL'
with open(csv_file_path_input, 'r', encoding='utf-8') as csvfile:
    csv_reader = csv.DictReader(csvfile)
    for row in csv_reader:
        url = row['1Mg_URL']
        name, brand, rating, num_rating, key_benefits, key_ingredients = fetch_additional_info(url)
        all_additional_info.append({
            'Name': name,
            'Brand_Name': brand,
            'Rating': rating,
            'Number_of_rating': num_rating,
            'Key Benefits': key_benefits,
            'Key Ingredients': key_ingredients
        })

# Create a new CSV file and write all the data
with open(csv_file_path_output, 'w', newline='', encoding='utf-8') as csvfile:
    # Create a CSV writer
    csv_writer = csv.writer(csvfile)

    # Write header row
    header = ['Name', 'Brand_Name', 'Rating', 'Number_of_rating', 'Key Benefits', 'Key Ingredients']
    csv_writer.writerow(header)

    # Write all the data to the CSV file
    for info in all_additional_info:
        csv_writer.writerow([
            info['Name'],
            info['Brand_Name'],
            info['Rating'],
            info['Number_of_rating'],
            info['Key Benefits'],
            info['Key Ingredients']
        ])
