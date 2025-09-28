"""
WhatsApp Business Cloud API service.
"""
import requests
import logging
from django.conf import settings
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WhatsAppService:
    """
    Service for interacting with WhatsApp Business Cloud API.
    """
    
    def __init__(self):
        self.phone_number_id = settings.WA_PHONE_NUMBER_ID
        self.token = settings.WA_TOKEN
        self.api_base = settings.WA_API_BASE
        self.verify_token = settings.WA_VERIFY_TOKEN
    
    def send_message(self, to: str, text: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a text message via WhatsApp.
        
        Args:
            to: Phone number in E.164 format
            text: Message text
            media_url: Optional media URL
        
        Returns:
            Dict with success status and message ID or error
        """
        try:
            url = f"{self.api_base}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            # Prepare message data
            message_data = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {"body": text}
            }
            
            # Add media if provided
            if media_url:
                message_data["type"] = "image"  # Default to image, could be enhanced
                message_data["image"] = {
                    "link": media_url
                }
                del message_data["text"]
            
            response = requests.post(url, headers=headers, json=message_data, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            message_id = result.get("messages", [{}])[0].get("id", "")
            
            logger.info(f"WhatsApp message sent successfully to {to}")
            
            return {
                "success": True,
                "message_id": message_id,
                "response": result
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_template_message(self, to: str, template_name: str, language: str = "en", components: Optional[list] = None) -> Dict[str, Any]:
        """
        Send a template message via WhatsApp.
        
        Args:
            to: Phone number in E.164 format
            template_name: WhatsApp template name
            language: Template language code
            components: Template components (parameters, etc.)
        
        Returns:
            Dict with success status and message ID or error
        """
        try:
            url = f"{self.api_base}/{self.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            message_data = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language}
                }
            }
            
            if components:
                message_data["template"]["components"] = components
            
            response = requests.post(url, headers=headers, json=message_data, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            message_id = result.get("messages", [{}])[0].get("id", "")
            
            logger.info(f"WhatsApp template message sent successfully to {to}")
            
            return {
                "success": True,
                "message_id": message_id,
                "response": result
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending WhatsApp template message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error sending WhatsApp template message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Get the status of a sent message.
        
        Args:
            message_id: WhatsApp message ID
        
        Returns:
            Dict with message status information
        """
        try:
            url = f"{self.api_base}/{message_id}"
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            
            # Parse status from response
            status = result.get("statuses", [{}])[0]
            
            return {
                "success": True,
                "status": status.get("status", "unknown"),
                "delivered": status.get("status") == "delivered",
                "read": status.get("status") == "read",
                "failed": status.get("status") == "failed",
                "error": status.get("errors", [{}])[0].get("title", "") if status.get("status") == "failed" else ""
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting message status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error getting message status: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def register_template(self, name: str, category: str, language: str, body: str) -> Dict[str, Any]:
        """
        Register a new message template with WhatsApp.
        
        Args:
            name: Template name
            category: Template category
            language: Template language
            body: Template body text
        
        Returns:
            Dict with success status and template ID or error
        """
        try:
            url = f"{self.api_base}/{self.phone_number_id}/message_templates"
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            template_data = {
                "name": name,
                "category": category,
                "language": language,
                "components": [
                    {
                        "type": "BODY",
                        "text": body
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=template_data, timeout=15)
            response.raise_for_status()
            
            result = response.json()
            template_id = result.get("id", "")
            
            logger.info(f"WhatsApp template registered successfully: {name}")
            
            return {
                "success": True,
                "template_id": template_id,
                "response": result
            }
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error registering WhatsApp template: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error registering WhatsApp template: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Verify webhook subscription.
        
        Args:
            mode: Verification mode
            token: Verification token
            challenge: Challenge string
        
        Returns:
            Challenge string if verification successful, None otherwise
        """
        if mode == "subscribe" and token == self.verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return challenge
        else:
            logger.warning("WhatsApp webhook verification failed")
            return None
    
    def parse_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse incoming webhook payload.
        
        Args:
            payload: Webhook payload from WhatsApp
        
        Returns:
            Parsed message data
        """
        try:
            entry = payload.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            
            # Handle message status updates
            if "statuses" in value:
                status = value["statuses"][0]
                return {
                    "type": "status",
                    "message_id": status.get("id"),
                    "status": status.get("status"),
                    "timestamp": status.get("timestamp"),
                    "recipient_id": status.get("recipient_id")
                }
            
            # Handle incoming messages
            elif "messages" in value:
                message = value["messages"][0]
                contact = value["contacts"][0] if "contacts" in value else {}
                
                # Extract message text
                text = ""
                media_url = None
                media_type = None
                
                if "text" in message:
                    text = message["text"]["body"]
                elif "image" in message:
                    media_url = message["image"]["id"]  # Would need to fetch actual URL
                    media_type = "image"
                elif "video" in message:
                    media_url = message["video"]["id"]
                    media_type = "video"
                elif "audio" in message:
                    media_url = message["audio"]["id"]
                    media_type = "audio"
                elif "document" in message:
                    media_url = message["document"]["id"]
                    media_type = "document"
                
                return {
                    "type": "message",
                    "message_id": message.get("id"),
                    "from": message.get("from"),
                    "text": text,
                    "media_url": media_url,
                    "media_type": media_type,
                    "timestamp": message.get("timestamp"),
                    "contact_name": contact.get("profile", {}).get("name", ""),
                    "contact_phone": message.get("from")
                }
            
            return {"type": "unknown", "payload": payload}
        
        except Exception as e:
            logger.error(f"Error parsing webhook payload: {str(e)}")
            return {"type": "error", "error": str(e)}
