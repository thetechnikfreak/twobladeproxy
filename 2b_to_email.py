import requests
import time
import smtplib
from email.message import EmailMessage
import re

# ---------- CONFIGURATION ----------
WEB_INBOX_URL = "https://twoblade.com/inbox/__data.json?x-sveltekit-invalidated=11"

# SMTP CONFIG
SMTP_SERVER = ""
SMTP_PORT = ""
SMTP_USER = ""
SMTP_PASS = ""

# ==== Twoblade Credentials ====
username = ""
password = ""

# ---------- PROGRAM ----------
HEADERSLOGIN = {
    "accept": "application/json",
    "accept-language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
    "content-type": "application/x-www-form-urlencoded",
    "origin": "https://twoblade.com",
    "priority": "u=1, i",
    "referer": "https://twoblade.com/login",
    "sec-ch-ua": '"Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-sveltekit-action": "true"
}
session = requests.Session()
payload = {"username": username, "password": password}
r = session.post("https://twoblade.com/login", data=payload, headers=HEADERSLOGIN)
authtoken = r.cookies.get("auth_token")
print("GOT AUTH TOKEN")
last_seen_id = None
HEADERS = {
    "accept": "*/*",
    "cookie": f"auth_token={authtoken}",
    "user-agent": "Mozilla/5.0 ..."
}
def check_new_email():
    global last_seen_id
    try:
        response = requests.get(WEB_INBOX_URL, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        email_node = data["nodes"][1]["data"]
        field_map = email_node[2]

        email_id = email_node[field_map["id"]]
        subject = email_node[field_map["subject"]]
        body = email_node[field_map["body"]]
        from_address = email_node[field_map["from_address"]]
        sent_at_data = email_node[field_map["sent_at"]]
        sent_at = sent_at_data[1] if isinstance(sent_at_data, list) else "Unknown"

        if last_seen_id != email_id:
            last_seen_id = email_id
            print(f"📧 New mail received from {from_address} — forwarding...")

            # Extract the email address from the subject (if it's present)
            recipient_email = extract_email_from_subject(subject)
            if recipient_email:
                send_via_smtp(from_address, recipient_email, subject, body, sent_at)
            else:
                print("❌ No email address found in the subject.")
        else:
            print("No new mail.")
    except Exception as e:
        print(f"❌ Error checking email: {e}")

def extract_email_from_subject(subject):
    """Extract an email address from the subject using regex."""
    email_regex = r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    match = re.search(email_regex, subject)
    if match:
        return match.group(0)
    return None

def send_via_smtp(from_address, to_address, subject, body, sent_at):
    try:
        msg = EmailMessage()
        msg["From"] = from_address
        msg["To"] = to_address
        msg["Subject"] = f"[From] {from_address or 'No Subject'}"
        msg.set_content(f"{body}")

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)

        print("✅ Email forwarded to:", to_address)
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# ---------- LOOP ----------
if __name__ == "__main__":
    while True:
        check_new_email()
        time.sleep(1)  # Check every 30 seconds
