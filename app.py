import os
import json
import time
import subprocess
import requests
import datetime

# ==================================================
# الإعدادات
# ==================================================

BASE_PATH = "/home/issam/Desktop/movie/"
MOVIES_FILE = os.path.join(BASE_PATH, "movies.json")
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
        subprocess.run(["git", "commit", "-m", "auto update"], capture_output=True)

        subprocess.run(
            ["git", "push", GIT_REMOTE, "main", "--force"],
            check=True
        )

        print("✅ تم الرفع بنجاح")

    except Exception as e:
        print("❌ خطأ أثناء الرفع:", e)


# ==================================================
# تحميل صورة الفيلم
# ==================================================

def download_image(poster_path):

    if not poster_path:
        return "images/default.jpg"

    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"

    try:
        img = requests.get(image_url, timeout=10)

        if (
            img.status_code == 200
            and "image" in img.headers.get("Content-Type", "")
            and len(img.content) > 2000
        ):

            img_name = f"{int(time.time())}.jpg"
            img_path = os.path.join(IMAGES_FOLDER, img_name)

            with open(img_path, "wb") as f:
                f.write(img.content)

            print("🖼 صورة تم تحميلها")

            return f"images/{img_name}"

    except:
        pass

    return "images/default.jpg"


# ==================================================
# جلب الأفلام من TMDB تلقائياً
# ==================================================

def fetch_movies():

    print("🔎 جلب أفلام جديدة من TMDB...")

    url = "https://api.themoviedb.org/3/movie/now_playing"

    response = requests.get(
        url,
        params={
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "page": 1
        },
        timeout=10
    )

    data = response.json()

    new_movies = []

    if not os.path.exists(MOVIES_FILE):
        movies_db = []
    else:
        with open(MOVIES_FILE, "r", encoding="utf-8") as f:
            try:
                movies_db = json.load(f)
            except:
                movies_db = []

    existing_titles = {movie["title"] for movie in movies_db}

    if data.get("results"):

        for movie in data["results"]:

            title = movie.get("title")

            if title in existing_titles:
                continue

            poster_path = movie.get("poster_path")
            thumb = download_image(poster_path)

            new_movies.append({
                "title": title,
                "url": "#",
                "thumb_path": thumb,
                "date": datetime.datetime.now().strftime("%d %b %Y")
            })

    if new_movies:
        movies_db = new_movies + movies_db

        with open(MOVIES_FILE, "w", encoding="utf-8") as f:
            json.dump(movies_db, f, indent=4, ensure_ascii=False)

        print(f"🔥 تمت إضافة {len(new_movies)} فيلم جديد")

        push()
    else:
        print("⚡ لا توجد أفلام جديدة")


# ==================================================
# التشغيل التلقائي
# ==================================================

if __name__ == "__main__":

    if not TMDB_API_KEY:
        print("❌ يجب تعيين TMDB_API_KEY")
        exit()

    print("🎬 النظام التلقائي يعمل الآن...")

    while True:

        fetch_movies()

        wait = 3600  # ساعة

        print("⏳ انتظار ساعة قبل التحديث القادم")

        time.sleep(wait)