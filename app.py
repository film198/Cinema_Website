import os
import json
import time
import random
import datetime
import requests
import subprocess

# ==============================
# 🔐 الإعدادات
# ==============================

BASE_PATH = "/home/issam/Desktop/movie"
MOVIES_FILE = os.path.join(BASE_PATH, "movies.json")
GITHUB_REPO = "git@github.com:film198/Cinema_Website.git"

TMDB_API_KEY = "c5177fea41bb46c2fb80e81d55473182"

# ==============================
# 🎬 جلب أفلام من TMDB
# ==============================

def fetch_movies():
    print("🔎 جلب أفلام جديدة من TMDB...")

    url = f"https://api.themoviedb.org/3/movie/popular?api_key={TMDB_API_KEY}&language=en-US&page=1"

    try:
        res = requests.get(url)
        if res.status_code != 200:
            print("❌ خطأ في الاتصال بـ TMDB")
            return []

        return res.json().get("results", [])[:20]

    except Exception as e:
        print("❌ استثناء:", e)
        return []

# ==============================
# 💾 حفظ الأفلام مع نظام أقسام ذكي
# ==============================

def save_movies(movies):

    data = []

    if os.path.exists(MOVIES_FILE):
        try:
            with open(MOVIES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except:
            data = []

    for movie in movies:

        title = movie.get("title")
        tmdb_id = movie.get("id")
        poster = movie.get("poster_path")

        if not title or not tmdb_id:
            continue

        poster_url = ""
        if poster:
            poster_url = f"https://image.tmdb.org/t/p/w500{poster}"

        # 🔥 نظام أقسام ذكي
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
            "thumb_path": poster_url,
            "watch_url": f"watch.html?id={tmdb_id}",
            "category": category,
            "date": datetime.datetime.now().strftime("%d %b %Y")
        }

        data.insert(0, movie_data)
        print("🖼 تمت إضافة:", title)

    with open(MOVIES_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==============================
# 🚀 رفع تلقائي إلى GitHub عبر SSH
# ==============================

def push():

    try:
        os.chdir(BASE_PATH)

        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "auto update"], capture_output=True)

        subprocess.run(["git", "push", "--force", "origin", "main"], check=True)

        print("✅ تم الرفع بنجاح عبر SSH")

    except Exception as e:
        print("❌ فشل الرفع:", e)

# ==============================
# 🔥 تشغيل تلقائي مستمر
# ==============================

if __name__ == "__main__":

    print("🎬 النظام الاحترافي يعمل الآن...")

    while True:

        movies = fetch_movies()

        if movies:
            save_movies(movies)
            push()

            print("⏳ انتظار ساعة قبل التحديث القادم")
            time.sleep(3600)

        else:
            print("⛔ لم يتم جلب بيانات")
            time.sleep(600)