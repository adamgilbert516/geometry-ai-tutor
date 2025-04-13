from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re
from time import sleep
from geogebra_topics import topics

# Configure headless Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Define your list of geometry topics (start small for testing)
#topics = [
#    "triangle classification",
#   "isosceles triangle",
#   "pythagorean theorem"
#]

# Collect materials
geogebra_data = []

# Start browser
driver = webdriver.Chrome(options=chrome_options)

# topics = topics[0:50]

for topic in topics:
    print(f"\n🔎 Searching GeoGebra for: {topic}")
    url = f"https://www.geogebra.org/search/{topic.replace(' ', '%20')}"
    driver.get(url)

    try:
        # Wait for materials to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/m/"]'))
        )
    except:
        print(f"⚠️ Timeout or no results found for: {topic}")
        continue

    cards = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/m/"]')
    print(f"✅ Found {len(cards)} material links")

    seen_ids = set()
    count = 0

    for card in cards:
        if count >= 10:
            break

        href = card.get_attribute("href")
        title = card.get_attribute("title") or card.text.strip()

        match = re.search(r'/m/([a-zA-Z0-9]+)', href)
        if match:
            material_id = match.group(1)
            if material_id not in seen_ids:
                seen_ids.add(material_id)
                count += 1
                print(f"  ↪ {title} — {material_id}")
                geogebra_data.append({
                    "Topic": topic,
                    "MaterialID": material_id,
                    "Title": title
                })
    sleep(2) # Avoid overwhelming the server

# Quit browser
driver.quit()

# Save to CSV
df = pd.DataFrame(geogebra_data)
df.to_csv("geogebra_materials.csv", index=False)
print("\n✅ Saved as geogebra_materials.csv")
