import os
import time
from dotenv import load_dotenv

from news_fetcher import fetch_latest_news
from llm_processor import generate_content_for_news
from image_generator import generate_background_image, create_quote_image
from sns_publisher import publish_all
from storage_manager import upload_to_imgbb, upload_to_gdrive

load_dotenv()

def main():
    print("=== Auto SNS Posting (News -> Quote + Satire) Pipeline Started ===")
    
    # 1. Fetch News
    print("\n[1] Fetching latest news...")
    news_items = fetch_latest_news(limit=1)
    if not news_items:
        print("Failed to fetch news. Exiting.")
        return
        
    top_news = news_items[0]
    news_title = top_news['title']
    print(f"Selected News: {news_title}")
    
    # 2. Generate Text Content (LLM)
    print("\n[2] Generating quote, caption, and image prompt via LLM...")
    llm_content = generate_content_for_news(news_title)
    if not llm_content:
        print("Failed to generate content. Exiting.")
        return
        
    quote = llm_content.get('quote')
    caption = llm_content.get('caption')
    image_prompt = llm_content.get('image_prompt')
    
    print(f"Quote: {quote}")
    print(f"Caption:\n{caption}")
    print(f"Image Prompt: {image_prompt}")
    
    # 3. Generate Background Image
    print("\n[3] Generating background image via DALL-E 3...")
    img_bytes = generate_background_image(image_prompt)
    if not img_bytes:
        print("Failed to generate background image. Exiting.")
        return
        
    # 4. Create Final Image with Text Overlay
    print("\n[4] Overlaying text on image...")
    output_filename = f"post_{int(time.time())}.jpg"
    created_img_path = create_quote_image(img_bytes, quote, output_filename)
    if not created_img_path:
        print("Failed to create quote image. Exiting.")
        return
        
    # 5. SNS Publishing (Bridge via ImgBB)
    print("\n[5] Uploading to ImgBB to get a Public URL...")
    public_url = upload_to_imgbb(created_img_path)
    
    if public_url:
        print("\n[6] Publishing to Instagram and Threads...")
        publish_all(public_url, caption)
    else:
        print("Skipping SNS publishing because ImgBB upload failed.")
        
    # 7. Permanent Backup (Google Drive)
    print("\n[7] Backing up results to Google Drive...")
    
    # Save a local text log to upload alongside the image
    log_filename = f"log_{int(time.time())}.txt"
    try:
        with open(log_filename, "w", encoding="utf-8") as f:
            f.write(f"News: {news_title}\n\n")
            f.write(f"Quote: {quote}\n\n")
            f.write(f"Caption: {caption}\n\n")
            f.write(f"Image Prompt: {image_prompt}\n")
            
        print("Uploading Image to Drive...")
        upload_to_gdrive(created_img_path)
        
        print("Uploading Log to Drive...")
        upload_to_gdrive(log_filename)
        
    except Exception as e:
        print(f"Error saving/uploading log file: {e}")
    
    print("\n=== Pipeline Completed Successfully! ===")
    print("Instance can now safely spin down.")

if __name__ == "__main__":
    main()
