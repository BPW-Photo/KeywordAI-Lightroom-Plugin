import anthropic
import base64
import sys
import os
import io
from PIL import Image

try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

API_KEY = "YOUR-API-KEY-HERE!"

def suggest_keywords(image_path):
    if not os.path.exists(image_path):
        print(f"ERROR: Could not find image at: {image_path}")
        sys.exit(1)
    img = Image.open(image_path)
    img.thumbnail((1568, 1568), Image.LANCZOS)
    buffer = io.BytesIO()
    img.convert("RGB").save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    image_data = base64.standard_b64encode(buffer.read()).decode("utf-8")
    client = anthropic.Anthropic(api_key=API_KEY)
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}}, {"type": "text", "text": "You are an expert photo keywording assistant for Adobe Lightroom. Analyse this image and suggest keywords. Return ONLY a plain comma-separated list of keywords, no explanations, no numbering. Include subjects, setting, lighting, mood, colours, actions, style. Aim for 15-30 keywords. Use lowercase. Separate with commas."}]}],
    )
    raw = message.content[0].text.strip()
    keywords = [kw.strip().lower() for kw in raw.split(",") if kw.strip()]
    return keywords

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 suggest_keywords.py <path_to_image>")
        sys.exit(1)
    keywords = suggest_keywords(sys.argv[1])
    print(", ".join(keywords))