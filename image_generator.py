import os
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_background_image(prompt):
    """
    Generates an image using DALL-E 3 and returns the image content in bytes.
    """
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        img_response = requests.get(image_url)
        return img_response.content
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def wrap_text(text, font, max_width, draw):
    """
    Wraps text dynamically to fit within max_width.
    """
    lines = []
    # If text is too long or contains newlines, process it
    words = text.split()
    current_line = []
    
    for word in words:
        current_line.append(word)
        line_str = " ".join(current_line)
        bbox = draw.textbbox((0, 0), line_str, font=font)
        if bbox[2] - bbox[0] > max_width:
            # Word makes it too long, push previous line and start new
            current_line.pop()
            lines.append(" ".join(current_line))
            current_line = [word]
            
    if current_line:
        lines.append(" ".join(current_line))
        
    return lines

def create_quote_image(image_bytes, quote_text, output_filename="output.png"):
    """
    Overlays quote text onto the background image.
    """
    try:
        # Load image
        img = Image.open(BytesIO(image_bytes)).convert("RGBA")
        
        # Darken the background for better text visibility
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.5)
        
        draw = ImageDraw.Draw(img)
        
        # Attempt to load a Korean-supporting font (Windows default) or fallback
        font_path = "C:\\Windows\\Fonts\\malgun.ttf"
        try:
            font = ImageFont.truetype(font_path, 60)
        except IOError:
            print("Warning: malgun.ttf not found. Falling back to default font (Korean may not render correctly).")
            font = ImageFont.load_default()
            
        # Wrap text
        max_width = img.width - 200 # 100px padding on each side
        lines = wrap_text(quote_text, font, max_width, draw)
        
        # Calculate total height of text block to center it
        line_heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]
        total_text_height = sum(line_heights) + 20 * (len(lines) - 1) # 20px buffer between lines
        
        y_text = (img.height - total_text_height) / 2
        
        # Draw each line centered
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            x_text = (img.width - line_width) / 2
            
            # Text shadow/outline for visibility
            shadow_pos = [(x_text-2, y_text-2), (x_text+2, y_text-2), (x_text-2, y_text+2), (x_text+2, y_text+2)]
            for pos in shadow_pos:
                draw.text(pos, line, font=font, fill="black")
                
            draw.text((x_text, y_text), line, font=font, fill="white")
            y_text += line_heights[i] + 20
            
        # Convert back to RGB for saving as JPEG/PNG
        img = img.convert("RGB")
        img.save(output_filename, "JPEG")
        print(f"Image successfully saved to {output_filename}")
        return output_filename
        
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

if __name__ == "__main__":
    # Test function (requires a valid image prompt for generation or local image to test overlay)
    print("Testing quote image generation...")
    # NOTE: Uncomment to fully test API. Be mindful of costs.
    # img_bytes = generate_background_image("An abstract dark stormy ocean representing economic hardship")
    # if img_bytes:
    #     create_quote_image(img_bytes, "고생 끝에 낙이 온다지만, 폭풍우는 생각보다 길게 이어지기도 한다.", "test_output.jpg")
