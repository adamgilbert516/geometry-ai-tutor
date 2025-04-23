
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

# Collect YouTube video matches
youtube_data = []

# Start browser
driver = webdriver.Chrome(options=chrome_options)

# Optional: limit number of topics
# topics = topics[0:50]

for topic in topics:
    print(f"🔎 Searching YouTube for: {topic}")
    query = topic.replace(" ", "+")
    url = f"https://www.youtube.com/results?search_query={query}"

    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "video-title"))
        )
    except:
        print(f"⚠️ No results found or timeout for: {topic}")
        continue

    # Find all video results
    videos = driver.find_elements(By.ID, "video-title")
    seen_ids = set()
    count = 0

    for video in videos:
        if count >= 1:
            break

        href = video.get_attribute("href")
        title = video.get_attribute("title") or video.text.strip()

        if href and "watch?v=" in href:
            video_id = href.split("watch?v=")[-1].split("&")[0]
            if video_id not in seen_ids:
                seen_ids.add(video_id)
                count += 1
                print(f"  🎬 {title} — {video_id}")
                youtube_data.append({
                    "Topic": topic,
                    "VideoID": video_id,
                    "Title": title
                })

    sleep(2)  # Avoid getting blocked

# Quit browser
driver.quit()

# Save to CSV
df = pd.DataFrame(youtube_data)
df.to_csv("youtube_codes.csv", index=False)
print("\n✅ Saved as youtube_codes.csv")
