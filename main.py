import os
import requests
import feedparser

RSS_URL   = os.environ['FB_RSS_URL']
TG_TOKEN  = os.environ['TELEGRAM_TOKEN']
TG_CHAT   = os.environ['TELEGRAM_CHAT_ID']
LAST_FILE = 'last_post_id.txt'

last_id = None
if os.path.exists(LAST_FILE):
    content = open(LAST_FILE).read().strip()
    if content:
        last_id = content

feed    = feedparser.parse(RSS_URL)
entries = feed.entries

if not entries:
    print("لا يوجد بوستات جديدة")
    exit()

new_entries = []
for entry in entries:
    if last_id and entry.id == last_id:
        break
    new_entries.append(entry)

print(f"بوستات جديدة: {len(new_entries)}")

for entry in reversed(new_entries):
    title = entry.get("title", "📌 بوست جديد")
    link  = entry.get("link", "")
    image = None

    if hasattr(entry, "media_content") and entry.media_content:
        image = entry.media_content[0].get("url")
    elif hasattr(entry, "enclosures") and entry.enclosures:
        image = entry.enclosures[0].get("href")

    message = f"📘 <b>ماجيكانو - Magicano</b>\n\n{title}\n\n🔗 {link}"

    if image:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto",
            data={"chat_id": TG_CHAT, "photo": image, "caption": message, "parse_mode": "HTML"}
        )
    else:
        r = requests.post(
            f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
            data={"chat_id": TG_CHAT, "text": message, "parse_mode": "HTML"}
        )
    print(f"تليجرام: {r.status_code}")

with open(LAST_FILE, 'w') as f:
    f.write(entries[0].id)

print("تم بنجاح ✅")
