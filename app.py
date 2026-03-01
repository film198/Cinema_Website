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
# 🔐 التوكن من المتغير البيئي
# ==============================

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    print("⚠️ لم يتم العثور على التوكن في المتغير البيئي")
else:
    print("✅ تم تحميل التوكن بنجاح")


# ==============================
# 📂 المسارات
# ==============================

BASE_PATH = "/home/issam/Desktop/movie/"
MOVIES_FILE = os.path.join(BASE_PATH, "movies.json")
LINKS_FILE = os.path.join(BASE_PATH, "links.txt")


# ==============================
# 🚀 دالة الرفع إلى GitHub
# ==============================

def push():
    try:
        os.chdir(BASE_PATH)

        subprocess.run(["git", "add", "."], check=True)

        subprocess.run(
            ["git", "commit", "-m", "update"],
            check=False
        )

        if GITHUB_TOKEN:
            subprocess.run(
                [
                    "git",
                    "push",
                    f"https://{GITHUB_TOKEN}@github.com/film198/Cinema_Website.git",
                    "main",
                    "--force"
                ],
                check=True
            )

            print("✅ تم الرفع للموقع بنجاح!")
        else:
            print("❌ لا يوجد توكن — لا يمكن الرفع")

    except Exception as e:
        print("❌ فشل الرفع:", e)


# ==============================
# 🤖 سكرايبر جلب عنوان الفيلم
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

        # ==============================
        # 📦 تحميل الأفلام القديمة
        # ==============================

        movies = []

        if os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                try:
                    movies = json.load(f)
                except:
                    movies = []

        # ==============================
        # ➕ إضافة الفيلم الجديد
        # ==============================

        movies.insert(0, {
            "title": title,
            "url": url,
            "thumb_path": "images/default.jpg",
            "date": datetime.datetime.now().strftime("%d %b %Y")
        })

        with open(MOVIES_FILE, "w", encoding="utf-8") as f:
            json.dump(movies, f, indent=4, ensure_ascii=False)

        # ==============================
        # 🚀 رفع التغييرات
        # ==============================

        push()

        return True

    except Exception as e:
        print("❌ خطأ في السكرايبر:", e)
        return False

    finally:
        if driver:
            driver.quit()


# ==============================
# 🔄 التشغيل المستمر
# ==============================

if __name__ == "__main__":

    print("🎬 البوت يعمل الآن... سيتم الرفع كل ساعة إلى ساعة ونصف")

    while True:

        if os.path.exists(LINKS_FILE) and os.stat(LINKS_FILE).st_size > 0:

            with open(LINKS_FILE, "r") as f:
                links = f.readlines()

            if len(links) > 0:

                if run_scraper(links[0].strip()):

                    # حذف أول رابط بعد معالجته
                    with open(LINKS_FILE, "w") as f:
                        f.writelines(links[1:])

                    wait = random.randint(3600, 5400)

                    print(f"💤 الانتظار القادم: {wait // 60} دقيقة")

                    time.sleep(wait)

        else:
            time.sleep(600)