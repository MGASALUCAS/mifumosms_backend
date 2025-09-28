"""
AI service for generating suggestions and summaries using Hugging Face.
"""
import requests
import logging
from django.conf import settings
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)


class AIService:
    """
    Service for AI-powered features using Hugging Face Inference API.
    """
    
    def __init__(self):
        self.api_url = settings.HF_API_URL
        self.api_key = settings.HF_API_KEY
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def suggest_reply(self, tenant_name: str, context: List[Dict[str, Any]]) -> List[str]:
        """
        Generate AI suggestions for replying to a conversation.
        
        Args:
            tenant_name: Name of the tenant/business
            context: List of recent messages in the conversation
        
        Returns:
            List of suggested replies
        """
        try:
            # Format context for the AI
            context_text = self._format_context_for_ai(context)
            
            # Create prompt for reply suggestions
            prompt = f"""You are a concise, warm customer support agent for {tenant_name}. 
Reply with JSON only:
{{"replies": ["...", "...", "..."]}}
Keep each under 25 words, simple English (or detect and match language).

CONTEXT:
{context_text}"""
            
            # Call Hugging Face API
            response = self._call_huggingface_api(prompt)
            
            if response and "replies" in response:
                return response["replies"]
            else:
                # Fallback suggestions
                return [
                    "Thank you for your message. How can I help you today?",
                    "I understand your concern. Let me assist you with that.",
                    "Thanks for reaching out. I'll get back to you shortly."
                ]
        
        except Exception as e:
            logger.error(f"Error generating AI suggestions: {str(e)}")
            return [
                "Thank you for your message. How can I help you today?",
                "I understand your concern. Let me assist you with that.",
                "Thanks for reaching out. I'll get back to you shortly."
            ]
    
    def summarize_conversation(self, context: List[Dict[str, Any]]) -> List[str]:
        """
        Generate AI summary for a conversation.
        
        Args:
            context: List of all messages in the conversation
        
        Returns:
            List of summary bullet points
        """
        try:
            # Format context for the AI
            context_text = self._format_context_for_ai(context)
            
            # Create prompt for conversation summary
            prompt = f"""Summarize this WhatsApp conversation into 3-5 bullets (JSON):
{{"summary":["...","...","..."]}}

CONVERSATION:
{context_text}"""
            
            # Call Hugging Face API
            response = self._call_huggingface_api(prompt)
            
            if response and "summary" in response:
                return response["summary"]
            else:
                # Fallback summary
                return [
                    "Customer inquiry received",
                    "Support provided",
                    "Issue resolved"
                ]
        
        except Exception as e:
            logger.error(f"Error generating AI summary: {str(e)}")
            return [
                "Customer inquiry received",
                "Support provided", 
                "Issue resolved"
            ]
    
    def _format_context_for_ai(self, context: List[Dict[str, Any]]) -> str:
        """
        Format conversation context for AI processing.
        
        Args:
            context: List of messages
        
        Returns:
            Formatted context string
        """
        formatted_messages = []
        
        for msg in context:
            direction = "Customer" if msg["direction"] == "in" else "Agent"
            text = msg["text"][:200]  # Limit text length
            formatted_messages.append(f"{direction}: {text}")
        
        return "\n".join(formatted_messages)
    
    def _call_huggingface_api(self, prompt: str) -> Dict[str, Any]:
        """
        Call Hugging Face Inference API.
        
        Args:
            prompt: Input prompt for the AI
        
        Returns:
            Parsed response from the API
        """
        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 200,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get("generated_text", "")
            else:
                generated_text = str(result)
            
            # Try to parse as JSON
            try:
                # Clean up the response to extract JSON
                start_idx = generated_text.find("{")
                end_idx = generated_text.rfind("}") + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = generated_text[start_idx:end_idx]
                    return json.loads(json_str)
                else:
                    logger.warning("No valid JSON found in AI response")
                    return {}
            
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse AI response as JSON: {str(e)}")
                return {}
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Hugging Face API: {str(e)}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error calling Hugging Face API: {str(e)}")
            return {}
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text.
        
        Args:
            text: Input text
        
        Returns:
            Language code (e.g., 'en', 'sw', 'fr')
        """
        try:
            # Simple language detection based on common words
            text_lower = text.lower()
            
            # Swahili indicators
            swahili_words = ['hujambo', 'sawa', 'asante', 'karibu', 'pole', 'hapana', 'ndiyo']
            if any(word in text_lower for word in swahili_words):
                return 'sw'
            
            # French indicators
            french_words = ['bonjour', 'merci', 'oui', 'non', 'comment', 'pourquoi']
            if any(word in text_lower for word in french_words):
                return 'fr'
            
            # Arabic indicators
            arabic_chars = ['ا', 'ب', 'ت', 'ث', 'ج', 'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض', 'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ك', 'ل', 'م', 'ن', 'ه', 'و', 'ي']
            if any(char in text for char in arabic_chars):
                return 'ar'
            
            # Default to English
            return 'en'
        
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return 'en'
    
    def generate_auto_reply(self, message_text: str, tenant_name: str) -> str:
        """
        Generate an automatic reply for common inquiries.
        
        Args:
            message_text: Incoming message text
            tenant_name: Name of the tenant/business
        
        Returns:
            Generated auto-reply text
        """
        try:
            text_lower = message_text.lower()
            
            # Common greeting patterns
            if any(word in text_lower for word in ['hello', 'hi', 'hey', 'hujambo', 'bonjour']):
                return f"Hello! Welcome to {tenant_name}. How can I help you today?"
            
            # Help requests
            if any(word in text_lower for word in ['help', 'support', 'assistance', 'msaada']):
                return f"Hi! I'm here to help you with {tenant_name}. What do you need assistance with?"
            
            # Pricing inquiries
            if any(word in text_lower for word in ['price', 'cost', 'fee', 'charge', 'bei']):
                return f"Thanks for your interest in {tenant_name}! Let me connect you with our pricing information."
            
            # Hours of operation
            if any(word in text_lower for word in ['hours', 'time', 'open', 'closed', 'muda']):
                return f"Thanks for asking about our hours! Let me get you the current schedule for {tenant_name}."
            
            # Default response
            return f"Thank you for contacting {tenant_name}! I'll get back to you as soon as possible."
        
        except Exception as e:
            logger.error(f"Error generating auto-reply: {str(e)}")
            return f"Thank you for contacting {tenant_name}! I'll get back to you as soon as possible."
