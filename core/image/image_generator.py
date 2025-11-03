from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from pathlib import Path
from core.image.image_crop import crop_pdf_sections
from core.pdf.pdf_data_extractor import extract_user_data  # your OCR/text function

# Constants and Mappings
# Use the system's default Noto Sans (or provide a valid path for your VS Code environment)
FONT_AMHARIC_DEFAULT = "/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf"
FONT_ENGLISH_DEFAULT = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"

TEMPLATE_PATH = Path("/home/ramsi/telegram_bot/data/templates/modified_id_high_quality.jpg")

TEMPLATE_FIELDS = {
    # Amharic Fields (Use font_am)
    "name_am": {"type": "text", "coords": (565, 210), "lang": "am"},
    "date_of_birth_et": {"type": "text", "coords": (565, 342), "lang": "am"},
    "sex_am": {"type": "text", "coords": (565, 413), "lang": "am"},
    "region_am": {"type": "text", "coords": (1315, 270), "lang": "am"},
    "zone_am": {"type": "text", "coords": (1315, 340), "lang": "am"},
    "woreda_am": {"type": "text", "coords": (1315, 420), "lang": "am"},

    # English/Gregorian/Numeric Fields (Use font_en or font_am for combined text)
    "name_en": {"type": "text", "coords": (565, 260), "lang": "en"},
    "date_of_birth_greg": {"type": "text", "coords": (565, 372), "lang": "en"},
    "sex_en": {"type": "text", "coords": (680, 413), "lang": "en"},
    "expiry_date": {"type": "text", "coords": (565, 495), "lang": "en"}, # Usually Gregorian/Numeric
    "phone_number": {"type": "text", "coords": (1315, 110), "lang": "en"}, # Numeric
    "region_en": {"type": "text", "coords": (1315, 305), "lang": "en"},
    "zone_en": {"type": "text", "coords": (1315, 380), "lang": "en"},
    "woreda_en": {"type": "text", "coords": (1315, 455), "lang": "en"},
    "fan_code": {"type": "text", "coords": (626, 534), "lang": "en"},

    # Image fields
    "photo": {"type": "image", "coords": (440, 120, 508, 208)},
    "qr_code": {"type": "image", "coords": (410, 363, 538, 483)},
    "fin_code": {"type": "image", "coords": (470, 492, 542, 502)},
    "small_photo": {"type": "image", "coords": (1027, 507, 1112, 625)},
}

def draw_bold_text(draw: ImageDraw.Draw, position, text, font, fill=(0, 0, 0), boldness=1):
    """Draw text in bold by overlaying the same text slightly offset."""
    x, y = position
    for dx in range(boldness + 1):
        for dy in range(boldness + 1):
            draw.text((x + dx, y + dy), text, font=font, fill=fill)


def generate_final_id_image(
    pdf_path: Path,
    output_dir: Path,
    font_amharic: str = FONT_AMHARIC_DEFAULT,
    font_english: str = FONT_ENGLISH_DEFAULT,
    font_size: int = 24,
    boldness: int = 1
) -> bytes:
    """Generate final ID image with text and images, ready as PNG bytes."""

    # 1️⃣ Extract images and text
    # Assuming crop_pdf_sections and extract_user_data are defined elsewhere
    image_crops = crop_pdf_sections(pdf_path, output_dir, dpi=400)
    text_data = extract_user_data(pdf_path)

    # 2️⃣ Load template image
    template_img = cv2.imread(str(TEMPLATE_PATH))
    if template_img is None:
        raise ValueError(f"Template image not found at {TEMPLATE_PATH}")

    # 3️⃣ Convert to PIL and Load Fonts
    img_pil = Image.fromarray(cv2.cvtColor(template_img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    
    height, width = template_img.shape[:2]

    # Draw vertical lines every 100 pixels
    # for x in range(0, width, 100):
    #     cv2.line(template_img, (x, 0), (x, height), (0, 0, 255), 2)  # Red lines

    # # Draw horizontal lines every 100 pixels
    # for y in range(0, height, 100):
    #     cv2.line(template_img, (0, y), (width, y), (255, 0, 0), 2)
    # Load Amharic font

    cv2.rectangle(template_img, (200, 183), (550, 655), (0, 0, 0), 2)
    cv2.rectangle(template_img, (630, 540), (930, 627), (0, 0, 0), 2)
    cv2.rectangle(template_img, (1760, 65), (2300, 600), (0, 0, 0), 2)
    cv2.rectangle(template_img, (1025, 500), (1115, 625), (0, 0, 0), 2)
    cv2.rectangle(template_img, (1310, 570), (1615, 610), (0, 0, 0), 2)
    

    png_params = [cv2.IMWRITE_PNG_COMPRESSION, 0]
    cv2.imwrite("/home/ramsi/telegram_bot/storage/photo.png",  template_img, png_params)
    try:
        font_am = ImageFont.truetype(font_amharic, font_size)
    except Exception as e:
        print(f"Warning: Amharic font not found or failed to load ({e}). Using default.")
        font_am = ImageFont.load_default()

    # Load English font
    try:
        font_en = ImageFont.truetype(font_english, font_size)
    except Exception as e:
        print(f"Warning: English font not found or failed to load ({e}). Using Amharic font.")
        font_en = font_am # Fallback to the Amharic font if English fails

    # 4️⃣ Draw text fields
    for key, field in TEMPLATE_FIELDS.items():
        if field["type"] != "text" or key not in text_data:
            continue
        
        # Determine the correct font to use
        current_font = font_am if field.get("lang") == "am" else font_en
        
        # --- Handle Combined Fields ---
        text_to_draw = str(text_data[key])
        if key == "date_of_birth_greg":
            continue
        
        if key == "sex_en":
        # Get the length of the *Amharic* sex field that was just drawn (or would be drawn)
            am_sex_text = str(text_data.get('sex_am', ''))
            am_sex_font = font_am
            
            # 1. Calculate the final X-position of the AMHARIC text (e.g., 565 + width)
            am_sex_start_x = TEMPLATE_FIELDS['sex_am']['coords'][0]
            am_sex_width = draw.textlength(am_sex_text, font=am_sex_font)
            
            # 2. Define a small, fixed padding (e.g., 5 pixels)
            horizontal_padding = 5
            
            # 3. Calculate the new X-coordinate for the English text
            new_x = am_sex_start_x + am_sex_width + horizontal_padding
            
            # 4. Set the new coordinates for the current 'sex_en' field
            field["coords"] = (new_x, field["coords"][1])
            
            # Change text to include the separator visually (as you had before)
            text_to_draw = "| " + text_to_draw
            
        if key == "date_of_birth_et" and "date_of_birth_greg" in text_data:
            text_greg = str(text_data.get('date_of_birth_greg', ''))
            text_to_draw = f"{text_data['date_of_birth_et']} | {text_greg}"
            # CRITICAL FIX: Use the English/Numeric font for this combined string
            # to ensure the Latin numbers and the pipe character render correctly.
            current_font = font_en

        # --- Draw the Text ---
        draw_bold_text(
            draw, 
            field["coords"], 
            text_to_draw, 
            current_font, # The corrected font variable
            boldness=boldness
        )

    # 5️⃣ Paste cropped images (same logic as before)
    for key, field in TEMPLATE_FIELDS.items():
        if field["type"] != "image" or key not in image_crops:
            continue

        crop_img = image_crops[key]
        # Check if the cropped image is valid (not None and not empty)
        if crop_img is None or crop_img.size == 0:
            continue

        pil_crop = Image.fromarray(cv2.cvtColor(crop_img, cv2.COLOR_BGR2RGB))
        x1, y1, x2, y2 = field["coords"]
        target_w, target_h = x2 - x1, y2 - y1

        # Resize with aspect ratio
        pil_crop.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)

        # Center in box
        paste_x = x1 + (target_w - pil_crop.width) // 2
        paste_y = y1 + (target_h - pil_crop.height) // 2
        img_pil.paste(pil_crop, (paste_x, paste_y))

    # 6️⃣ Convert back to OpenCV and encode as PNG bytes
    final_img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode(".png", final_img)
    return buffer.tobytes()