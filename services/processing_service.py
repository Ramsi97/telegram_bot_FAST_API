from services.telegram_service import TelegramService
from core.image.image_generator import generate_final_id_image
from core.pdf.extractor import get_pdf_metadata  
from typing import Optional
from pathlib import Path
import tempfile

class ProcessingService:
    def __init__(self, telegram_service: TelegramService):
        self.telegram = telegram_service

    async def process_pdf_from_telegram(self, file_id: str, chat_id: int) -> bool:
        """
        Main processing pipeline:
        1. Download PDF from Telegram
        2. Validate PDF has exactly 1 page
        3. Process PDF using your ID card generator
        4. Send generated ID card image back to user
        """
        try:
            # Step 1: Download PDF
            await self.telegram.send_message(chat_id, "📥 Downloading your PDF...")
            pdf_bytes = await self.telegram.download_file(file_id)
            
            # Step 2: Validate PDF page count
            metadata = get_pdf_metadata(pdf_bytes)  # ✅ Use correct function
            page_count = metadata.get("page_count", 1)
            
            # ✅ Validate single page requirement
            if page_count != 1:
                await self.telegram.send_message(
                    chat_id,
                    f"❌ Invalid PDF: This PDF has {page_count} pages.\n\n"
                    "Please send a **single-page PDF** document. "
                    "Multi-page documents are not supported."
                )
                return False
            
            await self.telegram.send_message(
                chat_id, 
                "✅ Valid single-page PDF detected. Generating ID card..."
            )
            
            # Step 3: Process with your ID card generator
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Save PDF to temporary file (your function expects file paths)
                pdf_file = temp_path / "input.pdf"
                with open(pdf_file, "wb") as f:
                    f.write(pdf_bytes)
                
                # Create output directory for your function
                output_dir = temp_path / "output"
                output_dir.mkdir(exist_ok=True)
                
                # ✅ Call your function with correct parameters
                await self.telegram.send_message(chat_id, "🔄 Processing PDF and generating ID card...")
                image_bytes = generate_final_id_image(
                    pdf_path=pdf_file,           # ✅ Path object
                    output_dir=output_dir,       # ✅ Path object  
                    font_amharic="/usr/share/fonts/truetype/noto/NotoSansEthiopic-Regular.ttf",
                    font_english="/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
                    font_size=24,
                    boldness=1
                )
            
            # Step 4: Send the generated ID card
            await self.telegram.send_message(chat_id, "📤 Sending your ID card...")
            await self.telegram.send_photo_bytes(chat_id, image_bytes, "id_card.png")
            
            await self.telegram.send_message(chat_id, "✅ ID card generation complete!")
            return True
            
        except Exception as e:
            error_msg = f"❌ Error generating ID card: {str(e)}"
            await self.telegram.send_message(chat_id, error_msg)
            return False