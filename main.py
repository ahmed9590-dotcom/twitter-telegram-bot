import asyncio
import os
import requests
from twikit import Client

async def main():
    TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    TARGET_ACCOUNTS  = os.environ['TARGET_ACCOUNT'].split(',')

    client = Client('en-US')
    await client.activate_guest_session()

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

        for tweet in reversed(new_tweets):
            message = (
                f"🐦 تغريدة جديدة من @{account}:\n\n"
                f"{tweet.text}\n\n"
                f"🔗 https://x.com/{account}/status/{tweet.id}"
            )
            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                data={"chat_id": TELEGRAM_CHAT_ID, "text": message}
            )
            print(f"تم إرسال: {tweet.id}")

        with open(last_id_file, 'w') as f:
            f.write(tweets[0].id)

asyncio.run(main())
