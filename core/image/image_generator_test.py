from pathlib import Path
from core.image.image_generator import generate_final_id_image

pdf_path = Path("/home/ramsi/telegram_bot/storage/uploads/gebre.pdf")
output_dir = Path("/home/ramsi/telegram_bot/storage/temp")

final_bytes = generate_final_id_image(pdf_path, output_dir)

# For local test:
with open("/home/ramsi/telegram_bot/storage/final_test.png", "wb") as f:
    f.write(final_bytes)

print("✅ Final image saved for review!")
