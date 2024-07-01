import time
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from initdriver import get_driver
import pandas as pd
from parseurl import remove_url_parameters, originalSubdomain

# Load data
data = pd.read_csv("companies_unique.csv")
urls = data["Company Linkedin Link"]

# Set cookie expiration
expiry_date = datetime.now() + timedelta(days=60)
expiry_timestamp = int(time.mktime(expiry_date.timetuple()))

# li_at cookie value
value = "REPLACE_WITH_COOKIE"
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
    url_about = url + "/about"
    driver.execute_script(f"window.location.href='{url_about}'")
    print(f"Scraping: {url}")
    # Wait for the element to be present
    try:
        web_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "dd a span"))
        )
        web = web_element.text
    except Exception as e:
        web = ""
        print(f"Error1: {e}")
        continue
    time.sleep(1)
    url_people = url+"/people?keywords=talent"
    url_people = originalSubdomain(url_people)
    driver.execute_script(f"window.location.href='{url_people}'")
    links = []
    time.sleep(4)
    if "talent" not in driver.current_url:
        try:
            value = "Search employees by title, keyword or school"
            input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//input[@placeholder='{value}']")
)
            )
            driver.execute_script("arguments[0].scrollIntoView()", input)
            time.sleep(1)
            input.send_keys("talent")
            time.sleep(1)
            input.send_keys(Keys.ENTER)
            value = "Keyword search already applied"
            web_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//input[@placeholder='{value}']")
)
            )
        except Exception as e:
            print(e)
            continue
    try:
        web_element = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.grid.grid__col--lg-8.block.org-people-profile-card__profile-card-spacing"))
        )
    except Exception as e:
        print("No members found")
        continue
    li = 0
    while 1:
        time.sleep(2)
        cards = driver.find_elements(By.CSS_SELECTOR,"li.grid.grid__col--lg-8.block.org-people-profile-card__profile-card-spacing")
        new_cards = cards[li:]
        if li == len(cards):
            break
        for card in new_cards:
            li+=1
            driver.execute_script("arguments[0].scrollIntoView()",card)
            time.sleep(0.1)
            role = card.find_element(By.CSS_SELECTOR,"div.ember-view.lt-line-clamp.lt-line-clamp--multi-line")
            try:
                link = card.find_element(By.TAG_NAME,"a").get_attribute("href")
            except:
                continue
            if "talent" in role.text.lower():
                print(link)
                links.append(link)
        button = driver.find_elements(By.XPATH,
                                      "//*[self::div or self::button or self::span][contains(text(), 'See more')]")
        if len(button) != 0:
            driver.execute_script("arguments[0].click();", button[0])
            time.sleep(1)
    talent_roles.append(links)
    webs.append(web)

# Save results to CSV
df = pd.read_csv("companies_unique.csv")
df['Website Link'] = pd.Series(webs)
output_csv_file_path = 'companies_unique.csv'
max_len = max(len(sublist) for sublist in talent_roles)

column_names = [f'Column {i+4}' for i in range(max_len)]

talent_roles_df = pd.DataFrame(talent_roles, columns=column_names)

df = pd.concat([df, talent_roles_df], axis=1)

df.to_csv(output_csv_file_path, index=False)
driver.quit()
