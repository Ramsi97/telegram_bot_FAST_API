import httpx
from app.config import settings
from pathlib import Path
from typing import Optional

class TelegramService:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"{settings.API_BASE_URL}/bot{token}"
        self.file_url = f"{settings.API_BASE_URL}/file/bot{token}"

    async def send_message(self, chat_id: int, text: str) -> bool:
        """Send text message to Telegram chat"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sendMessage",
                    json={"chat_id": chat_id, "text": text}
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to send message: {e}")
            return False

    async def send_photo_bytes(self, chat_id: int, image_bytes: bytes, filename: str = "image.jpg") -> bool:
        """Send photo using image bytes (NEW METHOD)"""
        try:
            async with httpx.AsyncClient() as client:
                files = {"photo": (filename, image_bytes, "image/jpeg")}
                response = await client.post(
                    f"{self.base_url}/sendPhoto",
                    data={"chat_id": chat_id},
                    files=files
                )
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to send photo: {e}")
            return False

    async def send_photo(self, chat_id: int, image_path: Path) -> bool:
        """Send photo from file path"""
        try:
            async with httpx.AsyncClient() as client:
                with open(image_path, "rb") as f:
                    files = {"photo": f}
                    response = await client.post(
                        f"{self.base_url}/sendPhoto",
                        data={"chat_id": chat_id},
                        files=files
                    )
                    return response.status_code == 200
        except Exception as e:
            print(f"Failed to send photo from file: {e}")
            return False

    async def download_file(self, file_id: str) -> bytes:
        """Download file from Telegram"""
        try:
            async with httpx.AsyncClient() as client:
                # Get file path
                file_info = await client.get(
                    f"{self.base_url}/getFile",
                    params={"file_id": file_id}
                )
                file_path = file_info.json()["result"]["file_path"]
                
                # Download file content
                file_data = await client.get(f"{self.file_url}/{file_path}")
                return file_data.content
                
        except Exception as e:
            raise Exception(f"Failed to download file from Telegram: {str(e)}")

    async def set_webhook(self) -> bool:  # ✅ ADD THIS METHOD
        """Set webhook URL with Telegram"""
        try:
            async with httpx.AsyncClient() as client:
                webhook_url = f"{settings.WEBHOOK_URL}/api/v1/webhook"
                response = await client.post(
                    f"{self.base_url}/setWebhook",
                    json={"url": webhook_url}
                )
                print(f"Webhook set to: {webhook_url}")
                return response.status_code == 200
        except Exception as e:
            print(f"Failed to set webhook: {e}")
            return False

    async def get_me(self) -> Optional[dict]:
        """Test bot authentication and get bot info"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/getMe")
                if response.status_code == 200:
                    return response.json()["result"]
                return None
        except Exception as e:
            print(f"Failed to get bot info: {e}")
            return None