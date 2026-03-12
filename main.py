import asyncio
import os
import requests
from twikit import Client

async def main():
    TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    TARGET_ACCOUNTS  = os.environ['TARGET_ACCOUNT'].split(',')
    TW_USERNAME      = os.environ['TW_USERNAME']
    TW_EMAIL         = os.environ['TW_EMAIL']
    TW_PASSWORD      = os.environ['TW_PASSWORD']

    client = Client('en-US')

    cookie_file = 'cookies.json'
    if os.path.exists(cookie_file):
        client.load_cookies(cookie_file)
    else:
        await client.login(
            auth_info_1=TW_USERNAME,
            auth_info_2=TW_EMAIL,
            password=TW_PASSWORD
        )
        client.save_cookies(cookie_file)

    for account in TARGET_ACCOUNTS:
        account = account.strip()
        last_id_file = f'last_tweet_id_{account}.txt'

        last_id = None
        if os.path.exists(last_id_file):
            content = open(last_id_file).read().strip()
            if content:
                last_id = content

        try:
            user   = await client.get_user_by_screen_name(account)
            tweets = await user.get_tweets('Tweets', count=10)
        except Exception as e:
            print(f"خطأ في {account}: {e}")
            continue

        if not tweets:
            print(f"لا يوجد تغريدات جديدة من {account}")
            continue

        new_tweets = []
        for tweet in tweets:
            if last_id and tweet.id <= last_id:
                break
            new_tweets.append(tweet)

        print(f"تغريدات جديدة من {account}: {len(new_tweets)}")

        for tweet in reversed(new_tweets):
            message = (
                f"🐦 تغريدة جديدة من @{account}:\n\n"
                f"{tweet.text}\n\n"
                f"🔗 https://x.com/{account}/status/{tweet.id}"
            )
            r = requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
            )
            print(f"تليجرام: {r.status_code}")

        with open(last_id_file, 'w') as f:
            f.write(tweets[0].id)

asyncio.run(main())
