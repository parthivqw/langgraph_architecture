

import os
import json
import requests
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# The "Blueprint" for the final image prompt lives here.
POSTER_PROMPT_SKELETON = """
Envision a {visual_style} {primary_subject} on a {setting}, with {effects}, all captured in ultra-wide cinematic glory.

📐 Layout:
- Top center: Large bold heading — "{heading}"
- Just below: Smaller subheading — "{subheading}"
- Center area: Short paragraph — "{paragraph}"
- Bottom left: Compact highlight of achievements — "{highlights}"
- Very bottom: Minimal hyperlink — "{hyperlink}"

🧠 Critical Instructions:
- Do not include any field labels.
- Text should appear naturally as part of the poster design.
- Avoid overlapping, distortion, and gibberish. Fonts must be clean, {font_style}, and fully legible.
"""

# --- TOOL 1: The Final Prompt Builder ---
def build_image_prompt_tool(collected_data: dict) -> str:
    """
    Takes the user's answers collected by the interaction manager and injects
    them into the master prompt skeleton to create the final "mega-prompt".
    """
    print("---TOOL: 🛠️ Building Final Image Generation Prompt---")
    
    effects_list = collected_data.get("effects", [])
    effects_str = ", ".join(effects_list) if effects_list else "vibrant lighting"

    final_prompt = POSTER_PROMPT_SKELETON.format(
        visual_style=collected_data.get("visual_style", "cinematic"),
        primary_subject=collected_data.get("primary_subject", "a product"),
        setting=collected_data.get("setting", "a modern city street"),
        effects=effects_str,
        heading=collected_data.get("heading", "Your Title Here"),
        subheading=collected_data.get("subheading", "An engaging subtitle"),
        paragraph=collected_data.get("paragraph", "A compelling description of the product or event."),
        highlights=collected_data.get("highlights", "Key Feature 1 | Key Feature 2"),
        hyperlink=collected_data.get("hyperlink", "yourwebsite.com"),
        font_style=collected_data.get("font_style", "sans-serif")
    )
    print("✅ Final prompt built and ready for image generation.")
    return final_prompt

# --- TOOL 2: The Image Generator (Live API) ---
def generate_image_from_prompt_tool(prompt: str) -> str:
    """
    Calls the a4f.co Imagen 3 API, retrieves the image URL,
    downloads the image, and returns it as a base64 string.
    """
    print("---TOOL: 🎨 Calling Live Image Generation API---")
    API_KEY = os.getenv("IMAGEGEN_API_KEY")
    if not API_KEY:
        raise ValueError("IMAGEGEN_API_KEY not found in environment variables.")

    IMAGEN_API_URL = "https://api.a4f.co/v1/images/generations"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "provider-4/imagen-4",
        "prompt": prompt,
        "n": 1,
        "size": "1024x1024"
    }
    
    try:
        print("🎨 Calling Imagen API...")
        # Step 1: Call the Imagen API
        response = requests.post(IMAGEN_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        image_url = response.json()['data'][0]['url']
        print("✅ Image URL received:", image_url)
        
        # Step 2: Download the image
        print("📥 Downloading image...")
        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        
        # Step 3: Convert to base64
        image_bytes = image_response.content
        base64_string = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"✅ Image converted to base64 (length: {len(base64_string)})")
        return base64_string
        
    except requests.RequestException as e:
        print(f"❌ Error during image generation or download: {str(e)}")
        raise RuntimeError("Poster image generation failed.") from e

