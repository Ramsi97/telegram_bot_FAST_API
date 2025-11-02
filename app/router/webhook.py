from fastapi import APIRouter, Depends, Request
from services.processing_service import ProcessingService
from services.telegram_service import TelegramService

router = APIRouter(tags=["webhooks"])

@router.post("/webhooks")
async def webhook(request: Request,
                  telegram: TelegramService = Depends(),
                  processor: ProcessingService = Depends()):
    update = await request.json()

    message = update.get("message", {})
    chat_id = message["chat"]["id"]

    if "document" in message:
        file_id = message["document"]["file_id"]
        image_path = await processor.process_pdf(file_id)
        await telegram.send_photo(chat_id, image_path)
    else:
        await telegram.send_message(chat_id, "Please send a PDF file.")

    return {"status": "ok"}