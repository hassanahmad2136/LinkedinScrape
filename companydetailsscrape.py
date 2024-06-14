import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from initdriver import get_driver
import pandas as pd
from parseurl import remove_url_parameters

# Load data
data = pd.read_csv("companies_unique.csv")
urls = data["Company Linkedin Link"]

# Set cookie expiration
expiry_date = datetime.now() + timedelta(days=60)
expiry_timestamp = int(time.mktime(expiry_date.timetuple()))

# li_at cookie value
value = 'REPLACE_WITH_COOKIE_VALUE'

# Initialize driver
driver = get_driver()
driver.get("https://www.linkedin.com/")

# Add cookie
li_at_cookie = {
    'name': 'li_at',
    'value': value,
    'domain': '.linkedin.com',
    'expiry': expiry_timestamp,
    'path': '/',
    'secure': True,
    'httpOnly': True
}

driver.add_cookie(li_at_cookie)
driver.refresh()

# Initialize lists
webs = []
talent_roles = []

# Iterate through URLs
for url in urls:
    url = remove_url_parameters(url)
    url = url + "/about"
    driver.execute_script(f"window.location.href='{url}'")
    print(f"Scraping: {url}")
    # Wait for the element to be present
    try:
        web_element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dd a span"))
        )
        web = web_element.text
    except Exception as e:
        web = ""
        print(f"Error: {e}")

    try:
        about_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "span.t-normal.t-black--light.link-without-visited-state.link-without-hover-state"))
        )
        cs = driver.find_elements(By.TAG_NAME, "a")
        for c in cs:
            href = c.get_attribute("href")
            print(href)
            if href and '/search/result' in href and 'people' in href:
                driver.execute_script(f"window.location.href='{href}'")
                break
    except Exception as e:
        print(e)

    links = []
    current_page = 1
    while True:
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.entity-result__primary-subtitle.t-14.t-black.t-normal"))
            )
            persons = driver.find_elements(By.CSS_SELECTOR, "div.entity-result__primary-subtitle.t-14.t-black.t-normal")
            profiles = driver.find_elements(By.CSS_SELECTOR,"span a.app-aware-link")
            for person in range(len(persons)):
                if "talent" in persons[person].text or 'Talent' in persons[person].text:
                    if "search/result" in profiles[person].get_attribute("href"):
                        continue
                    links.append(profiles[person].get_attribute("href"))
                pass
        except Exception as e:
            print(f"Error: {e}")

        current_page += 1
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        except:
            pass
        time.sleep(1)

        try:
            next_button = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'artdeco-pagination__button--next')]"))
            )
            if 'artdeco-button--disabled' in next_button.get_attribute('class'):
                talent_roles.append(links)
                break

            else:
                new_url = href + f"&page={current_page}"

                driver.execute_script(f"window.location.href='{new_url}'")
        except Exception as e:
            print(f"Error: {e}")
            talent_roles.append(links)
            break

    webs.append(web)

# Save results to CSV
df = pd.read_csv("companies_unique.csv")
df['Website Link'] = pd.Series(webs)
df['Profile Links'] = pd.Series(talent_roles)
output_csv_file_path = 'companies_unique.csv'
df.to_csv(output_csv_file_path, index=False)
driver.quit()