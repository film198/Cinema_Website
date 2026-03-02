import os
import json
import time
import datetime
import requests
import subprocess

# ==============================
# 🔐 الإعدادات
# ==============================

BASE_PATH = "/home/issam/Desktop/movie"
MOVIES_FILE = os.path.join(BASE_PATH, "movies.json")
IMAGES_PATH = os.path.join(BASE_PATH, "images")

TMDB_API_KEY = "c5177fea41bb46c2fb80e81d55473182"

# ==============================
# 🎬 جلب أفلام من TMDB
# ==============================

def fetch_movies():
    print("🔎 جلب أفلام من TMDB...")

    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"

    try:
        res = requests.get(url)
        if res.status_code != 200:
            print("❌ خطأ في TMDB")
            return []

        return res.json().get("results", [])[:10]

    except Exception as e:
        print("❌ استثناء:", e)
        return []

# ==============================
# 🖼 تحميل صورة الفيلم محليًا
# ==============================

def download_image(poster_path, tmdb_id):

    if not poster_path:
        return "images/default.jpg"

    if not os.path.exists(IMAGES_PATH):
        os.makedirs(IMAGES_PATH)

    image_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    local_filename = f"{tmdb_id}.jpg"
    local_path = os.path.join(IMAGES_PATH, local_filename)

    if os.path.exists(local_path):
        return f"images/{local_filename}"

    try:
        img_data = requests.get(image_url).content
        with open(local_path, "wb") as handler:
            handler.write(img_data)

        print("🖼 تم تحميل الصورة:", local_filename)
        return f"images/{local_filename}"

    except:
        print("❌ فشل تحميل الصورة")
        return "images/default.jpg"

# ==============================
# 💾 حفظ الأفلام بدون تكرار
# ==============================

def save_movies(movies):

    data = []

    if os.path.exists(MOVIES_FILE):
        try:
            with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []

    existing_ids = {movie["tmdb_id"] for movie in data if "tmdb_id" in movie}

    for movie in movies:

        title = movie.get("title")
        tmdb_id = movie.get("id")
        poster = movie.get("poster_path")

        if not title or not tmdb_id:
            continue

        if tmdb_id in existing_ids:
            continue  # منع التكرار

        thumb_path = download_image(poster, tmdb_id)

        popularity = movie.get("popularity", 0)

        if popularity > 500:
            category = "Popular"
        elif movie.get("vote_average", 0) > 7:
            category = "Top Rated"
        else:
            category = "Upcoming"

        movie_data = {
            "title": title,
            "tmdb_id": tmdb_id,
            "thumb_path": thumb_path,
            "watch_url": f"watch.html?id={tmdb_id}",
            "category": category,
            "date": datetime.datetime.now().strftime("%d %b %Y")
        }

        data.insert(0, movie_data)
        print("✅ تمت إضافة:", title)

    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================
# 🚀 رفع إلى GitHub (آمن)
# ==============================

def push():

    try:
        os.chdir(BASE_PATH)

        subprocess.run(["git", "add", "."], check=True)

        result = subprocess.run(
            ["git", "commit", "-m", "auto update"],
            capture_output=True,
            text=True
        )

        if "nothing to commit" in result.stdout:
            print("⚡ لا توجد تغييرات")
            return

        subprocess.run(["git", "push", "origin", "main"], check=True)

        print("🚀 تم الرفع بنجاح")

    except Exception as e:
        print("❌ فشل الرفع:", e)

# ==============================
# 🔥 تشغيل تلقائي
# ==============================

if __name__ == "__main__":

    print("🎬 النظام يعمل...")

    while True:

        movies = fetch_movies()

        if movies:
            save_movies(movies)
            push()
            print("⏳ انتظار ساعة...")
            time.sleep(3600)

        else:
            print("⛔ لا توجد بيانات")
            time.sleep(600)