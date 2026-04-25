import os
import json
import requests
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

load_dotenv()

IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")
GDRIVE_FOLDER_ID = os.getenv("GDRIVE_FOLDER_ID")
# In GitHub Actions, we'll pass the JSON as a string environment variable.
# Locally, you might use a file path, but reading from an env string is universally safer for CI.
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")

def upload_to_imgbb(image_path):
    """
    Uploads an image to ImgBB and returns its public URL.
    """
    if not IMGBB_API_KEY:
        print("IMGBB_API_KEY not found.")
        return None

    print(f"Uploading {image_path} to ImgBB...")
    url = "https://api.imgbb.com/1/upload"
    
    with open(image_path, "rb") as file:
        payload = {
            "key": IMGBB_API_KEY
        }
        files = {
            "image": file
        }
        response = requests.post(url, data=payload, files=files)
        
    if response.status_code == 200:
        data = response.json()
        public_url = data['data']['url']
        print(f"Successfully uploaded to ImgBB! URL: {public_url}")
        return public_url
    else:
        print(f"Failed to upload to ImgBB: {response.text}")
        return None

def get_gdrive_service():
    """
    Authenticates and returns the Google Drive API service.
    """
    if not GOOGLE_CREDENTIALS_JSON:
        print("GOOGLE_SERVICE_ACCOUNT_JSON not found. Skipping Google Drive upload.")
        return None
        
    try:
        credentials_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
        scopes = ['https://www.googleapis.com/auth/drive.file']
        creds = service_account.Credentials.from_service_account_info(credentials_dict, scopes=scopes)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Failed to authenticate with Google Drive: {e}")
        return None

def upload_to_gdrive(file_path, folder_id=GDRIVE_FOLDER_ID):
    """
    Uploads a file to a specific Google Drive folder.
    """
    service = get_gdrive_service()
    if not service or not folder_id:
        print("Google Drive service unavailable or Folder ID missing.")
        return False
        
    print(f"Uploading {file_path} to Google Drive...")
    file_name = os.path.basename(file_path)
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    # Simple content type deduction
    mimetype = 'application/octet-stream'
    if file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
        mimetype = 'image/jpeg'
    elif file_path.endswith('.txt'):
        mimetype = 'text/plain'
    elif file_path.endswith('.json'):
        mimetype = 'application/json'
        
    try:
        media = MediaFileUpload(file_path, mimetype=mimetype)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        print(f"Successfully uploaded to Google Drive. File ID: {file.get('id')}")
        return True
    except Exception as e:
        print(f"Google Drive upload failed: {e}")
        return False
