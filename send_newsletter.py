import smtplib
import json
from email.mime.text import MIMEText

EMAIL = "yourgmail@gmail.com"
PASSWORD = "your_app_password"

def get_emails():
    try:
        with open("emails.json","r") as f:
            return json.load(f)
    except:
        return []

def send_email(to_email):

    msg = MIMEText("🎬 New Movies Added!\nVisit our website now!")
    msg["Subject"] = "Cinema 198 Update"
    msg["From"] = EMAIL
    msg["To"] = to_email

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()
    server.login(EMAIL,PASSWORD)
    server.sendmail(EMAIL,to_email,msg.as_string())
    server.quit()

emails = get_emails()

for email in emails:
    try:
        send_email(email)
        print("📩 Sent to:", email)
    except:
        print("❌ Failed:", email)

print("✅ Newsletter sent!")