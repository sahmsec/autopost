import os
import requests
from openai import OpenAI

# ------------------------------
# Load secrets from environment
# ------------------------------
ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
URN = os.getenv("LINKEDIN_PERSON_URN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

# ------------------------------
# Generate LinkedIn post text
# ------------------------------
def generate_cyber_post():
    prompt = (
        "Write a LinkedIn post in a friendly, human-readable style about web security, "
        "network security, or vulnerabilities. Use storytelling, simple English, "
        "and 2-3 hashtags. Around 80-120 words."
    )

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

# ------------------------------
# Generate an image from post text
# ------------------------------
def generate_image(prompt_text, filename="cyber_post.png"):
    response = client.images.generate(
        model="gpt-image-1",
        prompt=f"Cybersecurity themed illustration for: {prompt_text}",
        size="1024x1024"
    )
    image_url = response.data[0].url
    # Download image
    image_data = requests.get(image_url).content
    with open(filename, "wb") as f:
        f.write(image_data)
    return filename

# ------------------------------
# Upload image to LinkedIn
# ------------------------------
def upload_image_to_linkedin(image_path):
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    register_body = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": URN,
            "serviceRelationships": [
                {"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
            ]
        }
    }
    r = requests.post(register_url, headers=headers, json=register_body).json()
    upload_url = r["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
    asset = r["value"]["asset"]

    # Upload the image bytes
    with open(image_path, "rb") as f:
        requests.put(upload_url, data=f, headers={"Authorization": f"Bearer {ACCESS_TOKEN}"})

    return asset

# ------------------------------
# Post text and image to LinkedIn
# ------------------------------
def post_to_linkedin(text, image_path=None):
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0"
    }

    specific_content = {
        "com.linkedin.ugc.ShareContent": {
            "shareCommentary": {"text": text},
            "shareMediaCategory": "NONE"
        }
    }

    if image_path:
        asset_id = upload_image_to_linkedin(image_path)
        specific_content["com.linkedin.ugc.ShareContent"]["shareMediaCategory"] = "IMAGE"
        specific_content["com.linkedin.ugc.ShareContent"]["media"] = [{
            "status": "READY",
            "description": {"text": "Cybersecurity illustration"},
            "media": asset_id,
            "title": {"text": "Cybersecurity"}
        }]

    body = {
        "author": URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": specific_content,
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"}
    }

    response = requests.post(url, headers=headers, json=body)
    print("LinkedIn Response:", response.json())

# ------------------------------
# Main script
# ------------------------------
if __name__ == "__main__":
    print("Posting immediately...")

    # Generate post text
    post_text = generate_cyber_post()
    print("Generated Post:\n", post_text)

    # Generate relevant image
    image_file = generate_image(post_text)
    print("Image file saved as:", image_file)

    # Post to LinkedIn
    post_to_linkedin(post_text, image_path=image_file)

    # Save post record locally
    with open("posted_logs.txt", "a", encoding="utf-8") as f:
        f.write(f"Post text:\n{post_text}\nImage file: {image_file}\n\n---\n\n")

    print("Post saved locally and published to LinkedIn.")
