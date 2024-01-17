import csv
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up the WebDriver
driver = webdriver.Chrome()

# Set the URL of the first page
homeopathy_url = 'https://www.1mg.com/categories/homeopathy-57?filter=true&pageNumber=1'
driver.get(url=homeopathy_url)

# Making soup
soup = BeautifulSoup(driver.page_source, "html.parser")

total_number_of_pages = 250
medicines_per_page = 40

# Remove dropdown
close_popup_button = driver.find_element(By.CLASS_NAME, 'UpdateCityModal__cancel-btn___2jWwS')
close_popup_button.click()
time.sleep(2)

# Create a list to store all the data
all_medicines_data = []

# Iterate through the pages
for page_number in range(1, total_number_of_pages + 1):
    homeopathy_url = f'https://www.1mg.com/categories/homeopathy-57?filter=true&pageNumber={page_number}'
    driver.get(url=homeopathy_url)

    # Wait for some time to ensure the page is fully loaded
    time.sleep(2)

    # Making soup
    soup = BeautifulSoup(driver.page_source, "html.parser")

    blocks = soup.find_all("div", {"class": "style__product-box___liepi"})

    for i in blocks:

        name_of_medicine = i.find('div', {'class': 'style__pro-title___2QwJy'}).text

        size_text = i.find('div', {'class': 'style__pack-size___2JQG7'}).text
        # Define a regular expression to extract the volume information
        volume_pattern = re.compile(r'\b(\d+\s*(?:ml|gm|tablets))\b', re.IGNORECASE)
        # Find all matches in the text
        matches = volume_pattern.findall(size_text)
        # Print the volumes
        for size in matches:
            size

        MRP_element = i.find("span", {"class": "style__discount-price___25Bya"})
        MRP = MRP_element.text.strip() if MRP_element else ''

        sale_price_element = i.find("div", {"class": "style__price-tag___cOxYc"})
        sale_price = sale_price_element.text.strip() if sale_price_element else ''

        url_element = i.find('a', {'class': 'style__product-link___UB_67'})
        url = f'https://www.1mg.com{url_element.get("href")}'

        # Store data in the list
        all_medicines_data.append([name_of_medicine, size, MRP, sale_price, url])

# Create a CSV file and store all the data
csv_file_path = 'all_medicines_data.csv'

with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
    # Create a CSV writer
    csv_writer = csv.writer(csvfile)

    # Write header row
    csv_writer.writerow(['Name', 'Size_of_the_bottle', 'MRP_of_the_bottle', 'Price_of_the_bottle', '1Mg_URL'])

    # Write all the data to the CSV file
    csv_writer.writerows(all_medicines_data)

# Get user input for the desired number of medicines
desired_medicines = int(
    input(f"How many medicines' details do you want (max {total_number_of_pages * medicines_per_page})? "))

# Create a new CSV file with the desired amount of data

new_csv_file_path = f'new_medicines_data_{desired_medicines}.csv'

with open(csv_file_path, 'r', encoding='utf-8') as input_csvfile, \
        open(new_csv_file_path, 'w', newline='', encoding='utf-8') as output_csvfile:
    # Create CSV reader and writer
    csv_reader = csv.reader(input_csvfile)
    csv_writer = csv.writer(output_csvfile)

    # Write header row
    csv_writer.writerow(next(csv_reader))

    # Write the desired amount of data to the new CSV file
    for _ in range(desired_medicines):
        csv_writer.writerow(next(csv_reader))

# Close the WebDriver
driver.quit()

# Print a message indicating the process is complete
print(f"Data has been read from '{csv_file_path}' and written to '{new_csv_file_path}'.")
