from fastapi import APIRouter, Request, Depends, BackgroundTasks, HTTPException
from services.telegram_service import TelegramService
from services.processing_service import ProcessingService
from app.dependencies import get_telegram_service, get_processing_service

router = APIRouter(tags=["telegram"])

@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    telegram: TelegramService = Depends(get_telegram_service),
    processor: ProcessingService = Depends(get_processing_service)
):
    try:
        update = await request.json()
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        
        if not chat_id:
            return {"status": "error", "message": "No chat ID found"}
        
        # Handle PDF document
        if "document" in message:
            document = message["document"]
            if document.get("mime_type") == "application/pdf":
                file_id = document["file_id"]
                
                # Process in background
                background_tasks.add_task(
                    processor.process_pdf_from_telegram,
                    file_id=file_id,
                    chat_id=chat_id
                )
                return {"status": "processing"}
            else:
                await telegram.send_message(chat_id, "Please send a PDF file.")
        
        # Handle text commands
        elif "text" in message:
            text = message["text"]
            if text.startswith("/start"):
                await telegram.send_message(
                    chat_id, 
                    "Welcome! Send me a PDF file and I'll convert it to an image."
                )
            else:
                await telegram.send_message(
                    chat_id,
                    "I only process PDF files. Please send a PDF document."
                )
        
        return {"status": "handled"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/set-webhook")
async def set_webhook(telegram: TelegramService = Depends(get_telegram_service)):
    """Call this once to set up the webhook with Telegram"""
    success = await telegram.set_webhook()
    return {"status": "webhook set" if success else "webhook setup failed"}