from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
from pathlib import Path
from datetime import date, timedelta
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
    "photo": {"type": "image", "coords": (200, 183, 550, 660)},
    "qrcode": {"type": "image", "coords": (1760, 65, 2300, 600)},
    "fin_code": {"type": "image", "coords": (1310, 570, 1615, 610)},
    "small_image": {"type": "image", "coords": (1027, 507, 1112, 625)},
    "barcode": {"type": "image", "coords": (630, 540, 930, 627)}
}

def gregorian_to_ethiopian(g_y, g_m, g_d):
    ethiopian_month_lengths = [30] * 12 + [5]
    
    new_year_offset = 11
    
    g = date(g_y, g_m, g_d)
    
    e_new_year = date(g_y, 9, new_year_offset)
    if g < e_new_year:
        e_new_year = date(g_y-1, 9, new_year_offset)
        e_year = g_y - 1 - 7
    else:
        e_year = g_y - 7
    
    delta = (g - e_new_year).days
    for m_idx, ml in enumerate(ethiopian_month_lengths):
        if delta < ml:
            e_month = m_idx + 1
            e_day = delta + 1
            break
        delta -= ml
    else:
        e_month = 13
        e_day = delta + 1
    
    return e_year, e_month, e_day

def draw_bold_text(draw: ImageDraw.Draw, position, text, font, fill=(0, 0, 0), boldness=1):
    """Draw text in bold by overlaying the same text slightly offset."""
    x, y = position
    for dx in range(boldness + 1):
        for dy in range(boldness + 1):
            draw.text((x + dx, y + dy), text, font=font, fill=fill)

def draw_vertical_text(base_img, position, text, font_path, font_size=23, fill=(0, 0, 0), boldness=1):
    """Draw vertical upward text (rotated 90° counterclockwise) at the given position, bold and small."""
    # Create font
    font = ImageFont.truetype(font_path, font_size)

    # Create a temporary transparent image for the text
    text_img = Image.new("RGBA", (400, 80), (255, 255, 255, 0))
    text_draw = ImageDraw.Draw(text_img)

    # Draw bold text by layering
    for dx in range(boldness + 1):
        for dy in range(boldness + 1):
            text_draw.text((dx, dy), text, font=font, fill=fill)

    # Rotate upward (90° counterclockwise)
    rotated = text_img.rotate(90, expand=1)

    # Paste it upward from the given (x, y) position
    x, y = position
    base_img.paste(rotated, (x, y - rotated.height), rotated)


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

    today = date.today()
    e_year, e_month, e_day = gregorian_to_ethiopian(today.year, today.month, today.day)
    date_of_issue_greg = f"{today.day:02d}/{today.month:02d}/{today.year}"
    date_of_issue_eth = f"{e_day:02d}/{e_month:02d}/{e_year}"
    expiry_eth_date = f"{e_day:02d}/{e_month:02d}/{e_year+8}"
    expiry_date_greg = f"{today.day:02d}/{today.month:02d}/{today.year+8}"

    text_data["expiry_date"] = f"{expiry_eth_date} | {expiry_date_greg}"
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
        pil_crop = pil_crop.resize((target_w, target_h), Image.Resampling.LANCZOS)


        # Center in box
        paste_x = x1 + (target_w - pil_crop.width) // 2
        paste_y = y1 + (target_h - pil_crop.height) // 2
        img_pil.paste(pil_crop, (paste_x, paste_y))

    
    draw_vertical_text(
        img_pil,
        position=(155, 275),
        text=date_of_issue_greg,
        font_path=font_english,
        font_size=22,
        fill=(0, 0, 0),
        boldness=1
    )

    draw_vertical_text(
        img_pil,
        position=(155, 550),
        text=date_of_issue_eth,
        font_path=font_english,
        font_size=22,
        fill=(0, 0, 0),
        boldness=1
    )

    # 6️⃣ Convert back to OpenCV and encode as PNG bytes
    final_img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    _, buffer = cv2.imencode(".png", final_img)
    return buffer.tobytes()