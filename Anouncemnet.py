import requests
import xml.etree.ElementTree as ET
import time
from datetime import datetime
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

FEED_URL = "https://nsearchives.nseindia.com/content/RSS/Online_announcements.xml"
FEED_NAME = "announcement"
seen_links = set()

BOT_TOKEN = '8165623622:AAGIPRrU5rdX4EmNUFT_IDvHDGjuMpWQAI0'
CHAT_ID = '5501599635'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"[Telegram Error] {e}")

def fetch_rss_feed():
    try:
        response = requests.get(FEED_URL, headers=headers, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"[Error] Fetch failed: {e}")
        return None

def extract_attachment_link(description):
    if ".pdf" in description:
        start = description.find("https://")
        end = description.find(".pdf") + 4
        return description[start:end]
    return "N/A"

def parse_and_display(xml):
    root = ET.fromstring(xml)
    items = root.findall(".//item")

    for item in items:
        title = item.findtext("title", default="N/A").strip()
        link = item.findtext("link", default="N/A").strip()
        description = item.findtext("description", default="").strip()

        if link in seen_links:
            continue
        seen_links.add(link)

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        attachment = extract_attachment_link(description)

        print("=" * 70)
        print(f"🕒 Announcement at : {now} IST")
        print(f"🏢 Stock name      : {title}")
        print(f"📝 Description     :\n{description}")
        print(f"🔗 Update link     : {link}")
        print(f"📎 Attachment link : {attachment}")
        print(f"🧾 NSE Feed        : {FEED_NAME}")
        print(f"📘 Other Info      : _")
        print(f"[{FEED_NAME}]\n")

        message = (
            f"<b>{FEED_NAME} Alert</b>\n"
            f"🕒 <b>Time</b>: {now} IST\n"
            f"🏢 <b>Stock</b>: {title}\n"
            f"📝 <b>Description</b>: {description or 'N/A'}\n"
            f"🔗 <b>Link</b>: {link}\n"
            f"📎 <b>Attachment</b>: {attachment}"
        )
        send_telegram_message(message)

def watch():
    print("📡 Live monitoring NSE RSS feed...\n")
    while True:
        xml = fetch_rss_feed()
        if xml:
            parse_and_display(xml)
        time.sleep(120)

# Dummy web server to keep Railway active
def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=watch, daemon=True).start()
    run_dummy_server()
