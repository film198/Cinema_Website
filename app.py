import os, json, time, subprocess, random, datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

BASE_PATH = "/home/issam/Desktop/movie/"
MOVIES_FILE = os.path.join(BASE_PATH, 'movies.json')
LINKS_FILE = os.path.join(BASE_PATH, 'links.txt')

def push():
    try:
        os.chdir(BASE_PATH)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "update"], capture_output=True)
        # الرفع سيتم الآن لأننا وضعنا التوكن في الإعدادات
        subprocess.run(["git", "push", "origin", "main", "--force"], check=True)
        print("✅ تم الرفع للموقع بنجاح!")
    except Exception as e:
        print(f"❌ فشل الرفع: {e}")

def run_scraper(url):
    opts = Options()
    opts.add_argument("--headless")
    opts.binary_location = "/home/issam/Desktop/movie/waterfox/waterfox"
    
    driver = None
    try:
        driver = webdriver.Firefox(service=Service("/home/issam/Desktop/movie/geckodriver"), options=opts)
        driver.get(url)
        time.sleep(7)
        title = driver.title.split('|')[0].strip()

        # الأرشفة الكاملة
        movies = []
        if os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, 'r', encoding='utf-8') as f:
                try: movies = json.load(f)
                except: movies = []
        
        # إضافة الفيلم الجديد في البداية وعدم حذف البقية
        movies.insert(0, {
            "title": title,
            "url": url,
            "thumb_path": "images/default.jpg",
            "date": datetime.datetime.now().strftime("%d %b %Y")
        })
        
        with open(MOVIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(movies, f, indent=4, ensure_ascii=False)

        push()
        return True
    except Exception as e:
        print(f"❌ خطأ: {e}")
        return False
    finally:
        if driver: driver.quit()

if __name__ == "__main__":
    print("🎬 البوت يعمل الآن... سيتم الرفع كل ساعة إلى ساعة ونصف")
    while True:
        if os.path.exists(LINKS_FILE) and os.stat(LINKS_FILE).st_size > 0:
            with open(LINKS_FILE, 'r') as f: links = f.readlines()
            if run_scraper(links[0].strip()):
                with open(LINKS_FILE, 'w') as f: f.writelines(links[1:])
                wait = random.randint(3600, 5400) # ساعة إلى ساعة ونصف
                print(f"💤 الانتظار القادم: {wait//60} دقيقة")
                time.sleep(wait)
        else:
            time.sleep(600)