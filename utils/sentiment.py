# utils/sentiment.py
import requests
import time
import re
from collections import Counter
from transformers import pipeline

# Load once globally
sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

def get_sentiment_data(api_key, session):
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {"X-API-Key": api_key}
    params = {
        "query": "ethereum OR #ETH OR #ethereum lang:en",
        "queryType": "Latest",
        "count": 30
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        tweets = data.get("tweets", [])

        if not tweets:
            return 0.0

        # Deduplicate by tweet ID
        session.setdefault("tweet_ids", set())
        new_tweets = [t for t in tweets if t.get("id") not in session["tweet_ids"]]
        for t in new_tweets:
            session["tweet_ids"].add(t.get("id"))

        # Top tweets by engagement
        new_tweets.sort(key=lambda t: t.get('favorite_count', 0) + t.get('retweet_count', 0), reverse=True)
        new_tweets = new_tweets[:15]

        # Run sentiment analysis
        texts = [t.get("text", "")[:512] for t in new_tweets]
        results = sentiment_pipeline(texts)
        scores = [r['score'] if r['label'] == 'POSITIVE' else -r['score'] for r in results]
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Append to session['sentiment_history']
        session.setdefault("sentiment_history", [])
        session["sentiment_history"].append({
            "time": time.time(),
            "score": avg_score
        })

        # Limit history to last 50
        session["sentiment_history"] = session["sentiment_history"][-50:]

        # Prepare tweet card content
        for i, tweet in enumerate(new_tweets):
            tweet['sentiment'] = results[i]['label']
            tweet['impact'] = tweet.get('favorite_count', 0) + tweet.get('retweet_count', 0)
            tweet['avatar'] = tweet.get('user', {}).get('profile_image_url_https', '')
            tweet['text'] = tweet.get('text', '')[:140] + '...' if len(tweet.get('text', '')) > 140 else tweet.get('text', '')
            tweet['user_screen_name'] = tweet.get('user', {}).get('screen_name', 'Unknown')

        session['recent_tweets'] = new_tweets

        # Extract top hashtags
        all_tags = [tag.lower() for tweet in tweets for tag in re.findall(r'#\w+', tweet['text'])]
        session["top_hashtags"] = [tag for tag, _ in Counter(all_tags).most_common(5)]

        return avg_score

    except Exception as e:
        print("Twitter API Error:", e)
        return session["sentiment_history"][-1]['score'] if session.get("sentiment_history") else 0.0
