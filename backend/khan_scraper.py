from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re

BASE_URL = "https://www.khanacademy.org/math"

MATH_SUBJECTS = [
    "basic-geo",
    "cc-fifth-grade-math",
    "cc-sixth-grade-math",
    "cc-seventh-grade-math",
    "cc-eighth-grade-math",
    "algebra",
    "geometry",
    "algebra2",
    "precalculus",
    "probability",
    "trigonometry",
    "statistics-probability",
    "ap-calculus-ab",
    "ap-calculus-bc",
    "ap-statistics",
    "multivariable-calculus",
    "linear-algebra",
    "differential-equations",
]

# Setup headless Chrome
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = webdriver.Chrome(options=options)

def extract_video_id(iframe_url):
    match = re.search(r"embed/([a-zA-Z0-9_-]+)", iframe_url)
    return match.group(1) if match else None

def collect_videos_for_subject(subject):
    print(f"🔍 Scraping subject: {subject}")
    driver.get(f"{BASE_URL}/{subject}")
    time.sleep(3)

    # Expand all unit sections
    expand_buttons = driver.find_elements(By.CSS_SELECTOR, "button[aria-label='Expand unit']")
    for btn in expand_buttons:
        try:
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(1)
        except:
            continue

    # Collect hrefs to video pages
    video_hrefs = list(set(
        link.get_attribute("href")
        for link in driver.find_elements(By.CSS_SELECTOR, "a[href*='/v/']")
        if link.get_attribute("href")
    ))

    video_data = []

    for href in video_hrefs:
        if "/v/" not in href:
            continue
        title = href.split("/v/")[-1].replace("-", " ").title()
        print(f"🎥 Visiting: {href}")
        driver.get(href)
        time.sleep(2)

        try:
            iframe = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            iframe_url = iframe.get_attribute("src")
            video_id = extract_video_id(iframe_url)

            if video_id:
                video_data.append({
                    "subject": subject,
                    "video_title": title,
                    "video_url": href,
                    "video_id": video_id
                })
                print(f"  ✅ Found video ID: {video_id}")
        except:
            print("  ⚠️ No iframe found.")

    return video_data

def main():
    all_video_data = []

    for subject in MATH_SUBJECTS:
        try:
            subject_videos = collect_videos_for_subject(subject)
            all_video_data.extend(subject_videos)
        except Exception as e:
            print(f"❌ Failed to scrape subject {subject}: {e}")

    driver.quit()

    df = pd.DataFrame(all_video_data)
    df.to_csv("khan_videos.csv", index=False)
    print("\n✅ Scraped all subjects. Saved to khan_videos.csv")

if __name__ == "__main__":
    main()
