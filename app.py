import os
import json
import time
import subprocess
import random
import datetime
import requests


# ==============================
# الإعدادات
# ==============================

BASE_PATH = "/home/issam/Desktop/movie/"
MOVIES_FILE = os.path.join(BASE_PATH, "movies.json")
LINKS_FILE = os.path.join(BASE_PATH, "links.txt")
IMAGES_FOLDER = os.path.join(BASE_PATH, "images")

GIT_REMOTE = "git@github.com:film198/Cinema_Website.git"

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

os.makedirs(IMAGES_FOLDER, exist_ok=True)


# ==============================
# رفع الملفات عبر SSH
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
        print("❌ خطأ أثناء الرفع:", e)


# ==============================
# جلب الفيلم + الصورة من TMDB
# ==============================

def run_scraper(url):

    if not TMDB_API_KEY:
        print("❌ لم يتم تعيين TMDB_API_KEY")
        return False

    try:
        movie_name = url.split("/")[-1].replace("-", " ")

        print("🎬 البحث عن:", movie_name)

        response = requests.get(
            "https://api.themoviedb.org/3/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "query": movie_name
            },
            timeout=10
        )

        data = response.json()

        thumb_path = "images/default.jpg"

        if data.get("results"):

            movie = data["results"][0]
            poster_path = movie.get("poster_path")

            if poster_path:

                image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

                img_name = f"{int(time.time())}.jpg"
                img_path = os.path.join(IMAGES_FOLDER, img_name)

                img_response = requests.get(image_url, timeout=10)

                content_type = img_response.headers.get("Content-Type", "")

                # 🔥 التحقق أن الرابط صورة فعلية
                if (
                    img_response.status_code == 200
                    and "image" in content_type
                    and len(img_response.content) > 2000
                ):

                    with open(img_path, "wb") as f:
                        f.write(img_response.content)

                    thumb_path = f"images/{img_name}"

                    print("🖼 تم تحميل صورة صحيحة من TMDB")

                else:
                    print("⚠️ الصورة غير صالحة أو تالفة")

        # ==============================
        # تحديث قاعدة البيانات
        # ==============================

        movies = []

        if os.path.exists(MOVIES_FILE):
            with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                try:
                    movies = json.load(f)
                except:
                    movies = []

        movies.insert(0, {
            "title": movie_name.title(),
            "url": url,
            "thumb_path": thumb_path,
            "date": datetime.datetime.now().strftime("%d %b %Y")
        })

        with open(MOVIES_FILE, "w", encoding="utf-8") as f:
            json.dump(movies, f, indent=4, ensure_ascii=False)

        push()

        return True

    except Exception as e:
        print("❌ خطأ أثناء معالجة الفيلم:", e)
        return False


# ==============================
# التشغيل المستمر
# ==============================

if __name__ == "__main__":

    print("🎬 البوت يعمل الآن — نظام TMDB مصحح")

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