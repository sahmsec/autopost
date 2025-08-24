import os
from openai import OpenAI
import requests

# Initialize OpenAI client
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# LinkedIn credentials
ACCESS_TOKEN = os.environ["LINKEDIN_ACCESS_TOKEN"]
PERSON_URN = os.environ["LINKEDIN_PERSON_URN"]

# Prompt for LinkedIn post
PROMPT = """
Write a LinkedIn post about a specific web or network vulnerability. 
Use emojis with uppercase headings (e.g., 🔹 OVERVIEW:). 
Explain the vulnerability, how it works, exploitation, impact, mitigation. 
End with a tip and 2-3 relevant hashtags. 
Do not tell a story; focus on technical education. 
"""

def generate_post():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": PROMPT}]
    )
    return response.choices[0].message.content.strip()

def post_to_linkedin(post_text):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    data = {
        "author": PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE"
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        print("Posted successfully!")
    else:
        print("Failed to post:", response.text)

if __name__ == "__main__":
    print("Generating LinkedIn post...")
    post_text = generate_post()
    print(post_text)
    print("Posting to LinkedIn...")
    post_to_linkedin(post_text)
