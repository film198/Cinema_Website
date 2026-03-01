import os
import json
import time
import subprocess
import random
import datetime
import requests
from bs4 import BeautifulSoup

# ==================================================
# الإعدادات
# ==================================================

BASE_PATH = "/home/issam/Desktop/movie/"
MOVIES_FILE = os.path.join(BASE_PATH, "movies.json")
LINKS_FILE = os.path.join(BASE_PATH, "links.txt")
IMAGES_FOLDER = os.path.join(BASE_PATH, "images")

GIT_REMOTE = "git@github.com:film198/Cinema_Website.git"

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

os.makedirs(IMAGES_FOLDER, exist_ok=True)


# ==================================================
# رفع الملفات عبر SSH
# ==================================================

def push():
    try:
        os.chdir(BASE_PATH)

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "update"], capture_output=True)

        subprocess.run(
            ["git", "push", GIT_REMOTE, "main", "--force"],
            check=True
        )

        print("✅ تم الرفع بنجاح عبر SSH")

    except Exception as e:
        print("❌ خطأ أثناء الرفع:", e)


# ==================================================
# تحميل صورة من TMDB مع التحقق
# ==================================================

def download_image(poster_path):

    if not poster_path:
        return "images/default.jpg"

    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

    try:
        img_data = requests.get(image_url, timeout=10)

        if (
            img_data.status_code == 200
            and "image" in img_data.headers.get("Content-Type", "")
            and len(img_data.content) > 2000
        ):

            img_name = f"{int(time.time())}.jpg"
            img_path = os.path.join(IMAGES_FOLDER, img_name)

            with open(img_path, "wb") as f:
                f.write(img_data.content)

            print("🖼 تم تحميل صورة صحيحة")

            return f"images/{img_name}"

        else:
            print("⚠️ الصورة غير صالحة")

            return "images/default.jpg"

    except:
        return "images/default.jpg"


# ==================================================
# معالجة فيلم واحد
# ==================================================

def run_scraper(url):

    if not TMDB_API_KEY:
        print("❌ TMDB_API_KEY غير موجود")
        return False

    try:
        print("🎬 معالجة الفيلم:", url)

        # ==================================================
        # استخراج عنوان الفيلم من الصفحة
        # ==================================================

        page = requests.get(url, timeout=10)

        if page.status_code != 200:
            print("❌ لا يمكن فتح الرابط")
            return False

        soup = BeautifulSoup(page.text, "html.parser")

        title_tag = soup.find("title")

        if title_tag:
            movie_title = title_tag.text.split("|")[0].strip()
        else:
            movie_title = url.split("/")[-1].replace("-", " ")

        print("🎥 العنوان المكتشف:", movie_title)

        # ==================================================
        # البحث في TMDB
        # ==================================================

        search = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": movie_title
            },
            timeout=10
        )

        data = search.json()

        thumb_path = "images/default.jpg"

        if data.get("results"):

            movie = data["results"][0]
            poster_path = movie.get("poster_path")

            thumb_path = download_image(poster_path)

        # ==================================================
        # تحديث قاعدة البيانات
        # ==================================================

        movies = []

        if os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                try:
                    movies = json.load(f)
                except:
                    movies = []

        movies.insert(0, {
            "title": movie_title,
            "url": url,
            "thumb_path": thumb_path,
            "date": datetime.datetime.now().strftime("%d %b %Y")
        })

        with open(MOVIES_FILE, "w", encoding="utf-8") as f:
            json.dump(movies, f, indent=4, ensure_ascii=False)

        push()

        return True

    except Exception as e:
        print("❌ خطأ:", e)
        return False


# ==================================================
# التشغيل المستمر
# ==================================================

if __name__ == "__main__":

    print("🎬 البوت يعمل الآن — النسخة النهائية")

    while True:

        if os.path.exists(LINKS_FILE) and os.stat(LINKS_FILE).st_size > 0:

            with open(LINKS_FILE, "r") as f:
                links = f.readlines()

            if run_scraper(links[0].strip()):

                # حذف الرابط الذي تمت معالجته
                with open(LINKS_FILE, "w") as f:
                    f.writelines(links[1:])

                wait = random.randint(3600, 5400)

                print(f"⏳ الانتظار القادم: {wait // 60} دقيقة")

                time.sleep(wait)

        else:
            time.sleep(600)