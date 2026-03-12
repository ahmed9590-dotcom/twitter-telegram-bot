import asyncio
import os
import requests
from twikit import GuestClient

async def main():
    TELEGRAM_TOKEN   = os.environ['TELEGRAM_TOKEN']
    TELEGRAM_CHAT_ID = os.environ['TELEGRAM_CHAT_ID']
    TARGET_ACCOUNT   = os.environ['TARGET_ACCOUNT']

    last_id = None
    if os.path.exists('last_tweet_id.txt'):
        content = open('last_tweet_id.txt').read().strip()
        if content:
            last_id = content

    client = GuestClient()
    await client.activate()

    user   = await client.get_user_by_screen_name(TARGET_ACCOUNT)
    tweets = await user.get_tweets('Tweets', count=10)

    if not tweets:
        print("لا يوجد تغريدات جديدة")
        return

    new_tweets = []
    for tweet in tweets:
        if last_id and tweet.id <= last_id:
            break
        new_tweets.append(tweet)

    for tweet in reversed(new_tweets):
        message = (
            f"🐦 تغريدة جديدة من @{TARGET_ACCOUNT}:\n\n"
            f"{tweet.text}\n\n"
            f"🔗 https://x.com/{TARGET_ACCOUNT}/status/{tweet.id}"
        )
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": message
            }
        )
        print(f"تم إرسال تغريدة: {tweet.id}")

    with open('last_tweet_id.txt', 'w') as f:
        f.write(tweets[0].id)

asyncio.run(main())
