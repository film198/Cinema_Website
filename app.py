import os, json, time, subprocess, random, datetime, requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By

BASE_PATH = "/home/issam/Desktop/movie/"
WATERFOX_BINARY = os.path.join(BASE_PATH, "waterfox/waterfox")
GECKO_PATH = os.path.join(BASE_PATH, "geckodriver")
MOVIES_FILE = os.path.join(BASE_PATH, 'movies.json')
LINKS_FILE = os.path.join(BASE_PATH, 'links.txt')
IMAGES_DIR = os.path.join(BASE_PATH, 'images')

if not os.path.exists(IMAGES_DIR): os.makedirs(IMAGES_DIR)

def fast_git_push(movie_title):
    try:
        os.chdir(BASE_PATH)
        subprocess.run(["git", "add", ".", "-f"], check=True)
        subprocess.run(["git", "commit", "-m", f"Update {movie_title[:10]}"], capture_output=True)
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        print(f"🚀 Synced: {movie_title}")
    except Exception as e: print(f"⚠️ Git Error: {e}")

def scrape_and_publish(url):
    options = Options()
    options.binary_location = WATERFOX_BINARY
    options.add_argument("--headless")
    driver = None
    try:
        driver = webdriver.Firefox(service=Service(GECKO_PATH), options=options)
        driver.get(url)
        time.sleep(7)
        raw_title = driver.title.split('|')[0].strip()
        
        # تحميل الصورة (لحل مشكلة "أين الصور")
        try:
            img_url = driver.find_element(By.CSS_SELECTOR, "meta[property='og:image']").get_attribute("content")
            img_name = f"img_{int(time.time())}.jpg"
            img_data = requests.get(img_url, timeout=10).content
            with open(os.path.join(IMAGES_DIR, img_name), 'wb') as f: f.write(img_data)
        except: img_name = "default.jpg"

        new_movie = {
            "title": raw_title,
            "url": url,
            "thumb_path": f"images/{img_name}",
            "date": datetime.datetime.now().strftime("%d %b %Y")
        }

        # الحفاظ على الأرشيف كاملاً (بدون حذف)
        movies = []
        if os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
                try: movies = json.load(f)
                except: movies = []
        
        movies.insert(0, new_movie)
        with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=4, ensure_ascii=False) # لا يوجد قَص للمصفوفة هنا

        fast_git_push(raw_title)
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    while True:
        if os.path.exists(LINKS_FILE) and os.stat(LINKS_FILE).st_size > 0:
            with open(LINKS_FILE, 'r') as f: links = f.readlines()
            if links[0].strip() and scrape_and_publish(links[0].strip()):
                with open(LINKS_FILE, 'w') as f: f.writelines(links[1:])
                t = random.randint(3600, 5400)
                print(f"💤 Next in {t//60} min"); time.sleep(t)
        else: time.sleep(600)