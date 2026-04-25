import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

IG_USER_ID = os.getenv("IG_USER_ID")
IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
THREADS_USER_ID = os.getenv("THREADS_USER_ID")
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN")

def post_to_instagram(image_url, caption):
    """
    Posts an image with a caption to Instagram using the Facebook Graph API.
    Note: The Instagram Graph API requires a public URL for the image container.
    """
    if not IG_USER_ID or not IG_ACCESS_TOKEN:
        print("Instagram credentials not found.")
        return False
        
    print("Uploading to Instagram...")
    
    # 1. Create a media container
    url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": IG_ACCESS_TOKEN
    }
    
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Error creating IG media container: {response.json()}")
        return False
        
    creation_id = response.json().get('id')
    
    # Wait for the media container to be processed
    time.sleep(5)
    
    # 2. Publish the container
    publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": IG_ACCESS_TOKEN
    }
    
    publish_res = requests.post(publish_url, data=publish_payload)
    if publish_res.status_code != 200:
        print(f"Error publishing IG media: {publish_res.json()}")
        return False
        
    print(f"Successfully posted to Instagram! Post ID: {publish_res.json().get('id')}")
    return True

def post_to_threads(image_url, caption):
    """
    Posts an image with a caption to Threads using the Threads API.
    Note: The Threads API also requires a public URL for media.
    """
    if not THREADS_USER_ID or not THREADS_ACCESS_TOKEN:
        print("Threads credentials not found.")
        return False
        
    print("Uploading to Threads...")
    
    # 1. Create a Threads media container
    url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads"
    payload = {
        "media_type": "IMAGE",
        "image_url": image_url,
        "text": caption,
        "access_token": THREADS_ACCESS_TOKEN
    }
    
    response = requests.post(url, data=payload)
    if response.status_code != 200:
        print(f"Error creating Threads media container: {response.json()}")
        return False
        
    creation_id = response.json().get('id')
    
    # Wait for the media container to be processed
    time.sleep(5)
    
    # 2. Publish the container
    publish_url = f"https://graph.threads.net/v1.0/{THREADS_USER_ID}/threads_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": THREADS_ACCESS_TOKEN
    }
    
    publish_res = requests.post(publish_url, data=publish_payload)
    if publish_res.status_code != 200:
        print(f"Error publishing Threads media: {publish_res.json()}")
        return False
        
    print(f"Successfully posted to Threads! Post ID: {publish_res.json().get('id')}")
    return True

def post_text_to_threads(text, link_url=None):
    """
    Posts a text-only Threads post. Returns the published Threads post ID.
    """
    if not THREADS_ACCESS_TOKEN:
        raise RuntimeError("THREADS_ACCESS_TOKEN is not set.")
    if "|" in THREADS_ACCESS_TOKEN:
        raise RuntimeError(
            "THREADS_ACCESS_TOKEN looks like an app/client token. "
            "Use a Threads Graph API user access token with publishing permission."
        )

    threads_user_id = THREADS_USER_ID if THREADS_USER_ID and THREADS_USER_ID.isdigit() else "me"
    url = f"https://graph.threads.net/v1.0/{threads_user_id}/threads"
    payload = {
        "media_type": "TEXT",
        "text": text,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    if link_url:
        payload["link_attachment"] = link_url

    response = requests.post(url, data=payload, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Error creating Threads text container: {_safe_response(response)}")

    creation_id = response.json().get("id")
    if not creation_id:
        raise RuntimeError("Threads did not return a creation container ID.")

    time.sleep(3)

    publish_url = f"https://graph.threads.net/v1.0/{threads_user_id}/threads_publish"
    publish_payload = {
        "creation_id": creation_id,
        "access_token": THREADS_ACCESS_TOKEN,
    }
    publish_res = requests.post(publish_url, data=publish_payload, timeout=30)
    if publish_res.status_code != 200:
        raise RuntimeError(f"Error publishing Threads text post: {_safe_response(publish_res)}")

    post_id = publish_res.json().get("id")
    if not post_id:
        raise RuntimeError("Threads publish response did not include a post ID.")
    return post_id

def _safe_response(response):
    try:
        return response.json()
    except ValueError:
        return response.text[:1000]

def publish_all(image_url, caption):
    """Publish to all configured platforms."""
    ig_success = post_to_instagram(image_url, caption)
    th_success = post_to_threads(image_url, caption)
    return ig_success, th_success

if __name__ == "__main__":
    # Test function requires a valid public image URL and valid access tokens.
    print("SNS Publisher loaded. Need valid tokens and a public image URL to test.")
