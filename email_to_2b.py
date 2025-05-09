import imaplib
import email
from email.header import decode_header
import requests
import json
import time
import hashlib
import random
import string
import base64
from datetime import datetime, timezone


# ==== STMP Credentials ====
EMAIL = ""
PASSWORD = ""
STMP_SERVER = ""

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
Twoblade_INBOX_URL = 'https://twoblade.com/api/emails/new'
Twoblade_INBOX_HEADERS = {
    'accept': '*/*',
    'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    "cookie": f"auth_token={authtoken}",
    'origin': 'https://twoblade.com',
    'referer': 'https://twoblade.com/inbox',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

class HashcashSolver:
    def __init__(self):
        self.bits = 18
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    def __rand_str(self, n=16):
        return ''.join(random.choice(self.chars) for _ in range(n))

    def __format_date(self, date):
        return f"{date.year % 100:02d}{date.month:02d}{date.day:02d}{date.hour:02d}{date.minute:02d}{date.second:02d}"

    def __sha1_hash(self, s):
        return hashlib.sha1(s.encode('utf-8')).hexdigest()

    def __has_leading_zero_bits(self, hex_hash):
        hash_int = int(hex_hash, 16)
        bin_hash = bin(hash_int)[2:].zfill(160)
        return bin_hash.startswith('0' * self.bits)

    def gen_token(self, resource):
        version = 1
        date = self.__format_date(datetime.now(timezone.utc))
        rand = self.__rand_str()
        counter = 0

        while True:
            counter_buf = counter.to_bytes(4, "big")
            counter_b64 = base64.b64encode(counter_buf).decode("utf-8").rstrip("=")
            header = f"{version}:{self.bits}:{date}:{resource}::{rand}:{counter_b64}"
            if self.__has_leading_zero_bits(self.__sha1_hash(header)):
                return header
            counter += 1

def connect_to_stmp():
    mail = imaplib.IMAP4_SSL(STMP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select("inbox")
    return mail

def fetch_new_emails(mail):
    status, messages = mail.search(None, 'UNSEEN')
    if status != "OK":
        return []
    return messages[0].split()

def get_email_content(mail, email_id):
    status, msg_data = mail.fetch(email_id, "(RFC822)")
    if status != "OK":
        return None, None, None
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding or 'utf-8')
            from_ = msg.get("From")
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                        body = part.get_payload(decode=True).decode(errors='replace')
                        break
            else:
                body = msg.get_payload(decode=True).decode(errors='replace')
            return from_.strip(), subject.strip(), body.strip()
    return None, None, None

def send_to_Twoblade_inbox(from_,subject,body):
    print(f"Sending email from {from_} to Twoblade inbox...")
    print(f"Subject: {subject}")
    from__ = f"[FROM] {from_}"
    recipient_email = f"{subject}"
    solver = HashcashSolver()
    hashcash = solver.gen_token(recipient_email)

    data = {
        "from": "mail#twoblade.com",
        "to": recipient_email,
        "subject": from__,
        "body": body,
        "content_type": "text/plain",
        "html_body": None,
        "scheduled_at": None,
        "expires_at": None,
        "self_destruct": False,
        "hashcash": hashcash
    }
    try:
        response = requests.post(Twoblade_INBOX_URL, headers=Twoblade_INBOX_HEADERS, data=json.dumps(data))
        print(f"Response: {response.status_code} - {response.text}")
        return response
    except Exception as e:
        print(f"Failed to send to Twoblade inbox: {e}")
        return None

def main():
    reconnect_interval = 12  # Reconnect every 12 loops (~60 seconds if sleep is 5)
    loop_count = 0
    mail = connect_to_stmp()

    while True:
        try:
            email_ids = fetch_new_emails(mail)
            if email_ids:
                for email_id in email_ids:
                    from_, subject, body = get_email_content(mail, email_id)
                    if from_ and body:
                        response = send_to_Twoblade_inbox(from_, subject, body)
                        if response:
                            print(f"[{datetime.now()}] Sent Status: {response.status_code}")
                        else:
                            print(f"[{datetime.now()}] Failed to send email")
                    else:
                        print(f"[{datetime.now()}] Failed to parse email {email_id}")
            else:
                print(f"[{datetime.now()}] No new emails.")

            loop_count += 1
            if loop_count >= reconnect_interval:
                try:
                    mail.logout()
                except:
                    pass
                mail = connect_to_stmp()
                loop_count = 0

        except Exception as e:
            print(f"[{datetime.now()}] Error: {e}")
            try:
                mail.logout()
            except:
                pass
            time.sleep(5)
            mail = connect_to_stmp()

        time.sleep(5)

if __name__ == "__main__":
    main()
