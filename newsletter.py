import json

FILE = "emails.json"

def get_emails():
    try:
        with open(FILE,"r") as f:
            return json.load(f)
    except:
        return []

def add_email(email):
    emails = get_emails()

    if email not in emails:
        emails.append(email)

        with open(FILE,"w") as f:
            json.dump(emails,f,indent=4)

        print("✅ Email added")
    else:
        print("⚠ Already exists")

if __name__ == "__main__":
    print(get_emails())