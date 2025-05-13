from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Selenium setup
options = Options()
options.add_argument("--headless")  # Comment this line to watch the browser
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Target URL for Jan 2010 Supreme Court cases
base_url = "https://indiankanoon.org"
search_url = "https://indiankanoon.org/search/?formInput=doctypes:supremecourt%20fromdate:1-5-2011%20todate:%2031-5-2011"
driver.get(search_url)
time.sleep(2)

# Store case data
case_data = []

# Scrape multiple pages
while True:
    time.sleep(2)
    results = driver.find_elements(By.CLASS_NAME, "result_title")

    if not results:
        print("No results found.")
        break

    for result in results:
        try:
            link = result.find_element(By.TAG_NAME, "a")
            title = link.text.strip()
            case_url = link.get_attribute("href")

            # Date is in the sibling div
            try:
                date_el = result.find_element(By.XPATH, "following-sibling::div[1]")
                date = date_el.text.strip().split(" - ")[-1]
            except:
                date = "N/A"

            # Open case page
            driver.execute_script("window.open(arguments[0]);", case_url)
            driver.switch_to.window(driver.window_handles[1])
            time.sleep(2)

            # Get full judgment
            try:
                content = driver.find_element(By.ID, "documentContent").text.strip()
            except:
                content = "No content found."

            case_data.append({
                "title": title,
                "url": case_url,
                "date": date,
                "description": content
            })

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        except Exception as e:
            print(f"Error: {e}")
            continue

    # Try to go to next page
    try:
        next_button = driver.find_element(By.LINK_TEXT, "Next")
        next_button.click()
    except NoSuchElementException:
        break

driver.quit()

# Save to CSV
with open("supreme_court_may2011_cases.csv", "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=["title", "url", "date", "description"])
    writer.writeheader()
    writer.writerows(case_data)

print("✅ Finished. Data saved to 'supreme_court_may2011_cases.csv'")
