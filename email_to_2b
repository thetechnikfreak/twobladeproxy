import imaplib
import email
from email.header import decode_header
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# ==== Gmail Credentials ====
GMAIL_USER = ""
GMAIL_PASS = ""

# ==== Selenium Message Credentials ====
USERNAME = ""
PASSWORD = ""

# ==== Set Up Selenium Driver ====
driver = webdriver.Chrome()

def login_twoblade():
    driver.get("https://twoblade.com/inbox")
    time.sleep(1)
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD + Keys.RETURN)
    time.sleep(1)

def compose_message():
    compose_button = driver.find_element(By.XPATH, "//button[.//span[text()='Compose']]")
    compose_button.click()
    time.sleep(1)

def fill_message_fields(to, subject, body):
    driver.find_element(By.ID, "to").send_keys(to)
    driver.find_element(By.ID, "subject").send_keys(subject)
    driver.find_element(By.ID, "body").send_keys(body)
    time.sleep(1)

def send_message():
    send_button = driver.find_element(By.XPATH, "//button[.//text()[contains(., 'Send')]]")
    send_button.click()
    time.sleep(5)

def fetch_new_emails():
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(GMAIL_USER, GMAIL_PASS)
    imap.select("inbox")

    status, messages = imap.search(None, '(UNSEEN)')
    email_ids = messages[0].split()

    for mail_id in email_ids:
        _, msg_data = imap.fetch(mail_id, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        subject, encoding = decode_header(msg["Subject"])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding if encoding else "utf-8")

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain" and not part.get("Content-Disposition"):
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset)
                    break
        else:
            charset = msg.get_content_charset() or "utf-8"
            body = msg.get_payload(decode=True).decode(charset)

        print(f"Sending message to: {subject}")
        compose_message()
        fill_message_fields(subject, "From the Real Part of Mail", body)
        send_message()

    imap.logout()

# ==== Main Flow ====
login_twoblade()
while True:
    fetch_new_emails()
    time.sleep(5)  # Check for new emails every 30 seconds
