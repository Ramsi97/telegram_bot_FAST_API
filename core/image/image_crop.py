# core/image/cropper.py
import cv2
from pathlib import Path
from core.pdf.pdf_to_image_converter import pdf_to_image

def crop_pdf_sections(pdf_path: Path, output_dir: Path):
    """
    Convert PDF to image, crop regions (photo, barcode, QR), and save them.
    Returns a dict with cropped image paths.
    """

    # Make sure output dir exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1️⃣ Convert PDF to image
    image_path = pdf_to_image(pdf_path, output_dir)

    # 2️⃣ Load image using OpenCV
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Image not found at {image_path}")

    # 3️⃣ Define crop coordinates (x1, y1, x2, y2)
    photo_coords = (345, 93, 396, 160)
    barcode_coords = (340, 225, 400, 245)
    qrcode_coords = (325, 285, 420, 377)

    # 4️⃣ Crop each section
    photo = img[photo_coords[1]:photo_coords[3], photo_coords[0]:photo_coords[2]]
    barcode = img[barcode_coords[1]:barcode_coords[3], barcode_coords[0]:barcode_coords[2]]
    qrcode = img[qrcode_coords[1]:qrcode_coords[3], qrcode_coords[0]:qrcode_coords[2]]

    # 5️⃣ Save each cropped image
    photo_path = output_dir / "photo_crop.png"
    barcode_path = output_dir / "barcode_crop.png"
    qrcode_path = output_dir / "qrcode_crop.png"

    cv2.imwrite(str(photo_path), photo)
    cv2.imwrite(str(barcode_path), barcode)
    cv2.imwrite(str(qrcode_path), qrcode)

    # 6️⃣ (Optional) draw rectangles for visualization
    cv2.rectangle(img, (445, 93), (496, 160), (0, 0, 255), 1)
    cv2.rectangle(img, (340, 225), (400, 245), (0, 0, 255), 1)
    cv2.rectangle(img, (325, 285), (420, 377), (0, 0, 255), 1)

    marked_path = output_dir / "marked_image.png"
    cv2.imwrite(str(marked_path), img)

    print("✅ Cropped and saved:")
    print(photo_path, barcode_path, qrcode_path, marked_path)

    return {
        "photo": photo_path,
        "barcode": barcode_path,
        "qrcode": qrcode_path,
        "marked": marked_path,
    }


# ✅ Corrected function call
if __name__ == "__main__":
    crop_pdf_sections(
        Path("/home/ramsi/telegram_bot/pdf_file/efayda_Ahmed Gelgelu Dido.pdf"),
        Path("/home/ramsi/telegram_bot/storage/images_produced")
    )
