import os
import requests
from openai import OpenAI
import random
import time

# Load secrets from GitHub Actions
ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
URN = os.getenv("LINKEDIN_PERSON_URN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

def generate_simple_post():
    prompt = (
        "Write a short, professional LinkedIn post in very simple, easy-to-read English. "
        "Keep sentences short, use common words, and make it engaging for anyone. "
        "Do not use jargon. Make it around 50-70 words."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def post_to_linkedin(text):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    body = {
        "author": URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    response = requests.post(url, headers=headers, json=body)
    print("LinkedIn Response:", response.json())

if __name__ == "__main__":
    # Random delay: 0 to 2 hours (0–7200 seconds)
    delay_seconds = random.randint(0, 7200)
    print(f"Delaying post by {delay_seconds // 60} minutes ({delay_seconds} seconds) to appear more natural...")
    time.sleep(delay_seconds)

    post_text = generate_simple_post()
    print("Generated Post:\n", post_text)
    post_to_linkedin(post_text)
