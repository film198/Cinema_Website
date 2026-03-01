import os
import json
import time
import subprocess
import random
import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service


# ==============================
# الإعدادات
# ==============================

BASE_PATH = "/home/issam/Desktop/movie/"
MOVIES_FILE = os.path.join(BASE_PATH, "movies.json")
LINKS_FILE = os.path.join(BASE_PATH, "links.txt")
IMAGES_FOLDER = os.path.join(BASE_PATH, "images")

# 🔥 استخدم SSH فقط
GIT_REMOTE = "git@github.com:film198/Cinema_Website.git"


# ==============================
# إنشاء مجلد الصور لو غير موجود
# ==============================

os.makedirs(IMAGES_FOLDER, exist_ok=True)


# ==============================
# رفع الملفات إلى GitHub
# ==============================

def push():
    try:
        os.chdir(BASE_PATH)

        subprocess.run(["git", "add", "."], check=True)

        subprocess.run(
            ["git", "commit", "-m", "update"],
            capture_output=True
        )

        subprocess.run(
            ["git", "push", GIT_REMOTE, "main", "--force"],
            check=True
        )

        print("✅ تم الرفع بنجاح عبر SSH")

    except Exception as e:
        print("❌ خطأ في الرفع:", e)


# ==============================
# تحميل البيانات + الصورة
# ==============================

def run_scraper(url):

    opts = Options()
    opts.add_argument("--headless")
    opts.binary_location = "/home/issam/Desktop/movie/waterfox/waterfox"

    driver = None

    try:
        driver = webdriver.Firefox(
            service=Service("/home/issam/Desktop/movie/geckodriver"),
            options=opts
        )

        driver.get(url)
        time.sleep(7)

        title = driver.title.split("|")[0].strip()

        # ==========================
        # تحميل أول صورة من الصفحة
        # ==========================

        try:
            img_element = driver.find_element("tag name", "img")
            img_url = img_element.get_attribute("src")

            img_name = f"{int(time.time())}.jpg"
            img_path = os.path.join(IMAGES_FOLDER, img_name)

            os.system(f"wget -q -O {img_path} {img_url}")

            thumb_path = f"images/{img_name}"

            print("🖼 تم تحميل الصورة:", img_name)

        except:
            thumb_path = "images/default.jpg"
            print("⚠️ لم يتم العثور على صورة — استخدام الصورة الافتراضية")

        # ==========================
        # تحديث movies.json
        # ==========================

        movies = []

        if os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                try:
                    movies = json.load(f)
                except:
                    movies = []

        movies.insert(0, {
            "title": title,
            "url": url,
            "thumb_path": thumb_path,
            "date": datetime.datetime.now().strftime("%d %b %Y")
        })

        with open(MOVIES_FILE, "w", encoding="utf-8") as f:
            json.dump(movies, f, indent=4, ensure_ascii=False)

        push()

        return True

    except Exception as e:
        print("❌ خطأ أثناء جلب الفيلم:", e)
        return False

    finally:
        if driver:
            driver.quit()


# ==============================
# التشغيل المستمر
# ==============================

if __name__ == "__main__":

    print("🎬 البوت يعمل الآن — رفع تلقائي مفعل")

    while True:

        if os.path.exists(LINKS_FILE) and os.stat(LINKS_FILE).st_size > 0:

            with open(LINKS_FILE, "r") as f:
                links = f.readlines()

            if run_scraper(links[0].strip()):

                # حذف الرابط الذي تم معالجته
                with open(LINKS_FILE, "w") as f:
                    f.writelines(links[1:])

                wait = random.randint(3600, 5400)

                print(f"⏳ الانتظار القادم: {wait // 60} دقيقة")

                time.sleep(wait)

        else:
            time.sleep(600)