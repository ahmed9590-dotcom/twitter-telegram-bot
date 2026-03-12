import os
import requests
import feedparser

def main():
    TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    TARGET_ACCOUNTS  = os.environ['TARGET_ACCOUNT'].split(',')

    nitter_instances = [
        'https://nitter.privacydev.net',
        'https://nitter.poast.org',
        'https://nitter.net',
    ]

    for account in TARGET_ACCOUNTS:
        account = account.strip()
        last_id_file = f'last_tweet_id_{account}.txt'

        last_id = None
        if os.path.exists(last_id_file):
            content = open(last_id_file).read().strip()
            if content:
                last_id = content

        feed = None
        for instance in nitter_instances:
            try:
                rss_url = f'{instance}/{account}/rss'
                response = requests.get(rss_url, timeout=10)
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    if feed.entries:
                        break
            except:
                continue

        if not feed or not feed.entries:
            print(f"لا يوجد تغريدات من {account}")
            continue

        new_tweets = []
        for entry in feed.entries:
            tweet_id = entry.link.split('/')[-1].split('#')[0]
            if last_id and tweet_id <= last_id:
                break
            new_tweets.append((tweet_id, entry.title, entry.link))

        for tweet_id, text, link in reversed(new_tweets):
            message = (
                f"🐦 تغريدة جديدة من @{account}:\n\n"
                f"{text}\n\n"
                f"🔗 {link}"
            )
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
            )
            print(f"تم إرسال: {tweet_id}")

        if new_tweets:
            with open(last_id_file, 'w') as f:
                f.write(new_tweets[0][0])

main()
