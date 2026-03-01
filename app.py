import os, json, time, subprocess, random
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service

# ... (الإعدادات الأساسية كما هي) ...

def scrape_movie(url):
    clean_env()
    options = Options()
    options.binary_location = WATERFOX_BINARY
    options.add_argument("--headless")
    # إيقاف تحميل الصور أثناء السحب لتوفير الإنترنت والمعالج
    options.set_preference("permissions.default.image", 2) 
    
    driver = webdriver.Firefox(service=Service(GECKO_PATH), options=options)
    driver.set_page_load_timeout(20) # لا تنتظر أكثر من 20 ثانية أبداً
    
    try:
        driver.get(url)
        # سحب العنوان فقط بسرعة
        title = driver.title.split('|')[0].strip()
        
        movie_data = {
            "title": title,
            "url": url,
            "thumb_path": "https://via.placeholder.com/500x750?text=Cinema+198" # صورة مؤقتة سريعة
        }
        
        if save_to_json(movie_data):
            # الرفع الآن سيكون لمحاً بالبصر بعد تنظيف Git
            subprocess.run(["git", "add", "movies.json"], check=True)
            subprocess.run(["git", "commit", "-m", "Fast Update"], capture_output=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            return True
    except: return False
    finally: driver.quit()