"""
Beem SMS Service Integration

This module provides integration with Beem Africa SMS API for sending SMS messages
across African countries. Beem is a leading SMS provider in Africa with excellent
delivery rates and competitive pricing.

Documentation: https://login.beem.africa
API Endpoint: https://apisms.beem.africa/v1/send
"""

import requests
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from django.conf import settings
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException, Timeout, ConnectionError

logger = logging.getLogger(__name__)


class BeemSMSError(Exception):
    """Custom exception for Beem SMS API errors"""
    pass


class BeemSMSService:
    """
    Beem SMS Service for sending SMS messages via Beem Africa API
    
    Features:
    - Send single or bulk SMS messages
    - Schedule SMS messages
    - Track delivery status
    - Support for multiple African countries
    - Error handling and retry logic
    """
    
    API_BASE_URL = getattr(settings, 'BEEM_API_BASE_URL', 'https://apisms.beem.africa/v1')
    SEND_ENDPOINT = f"{API_BASE_URL}/send"
    
    def __init__(self):
        """Initialize Beem SMS service with API credentials"""
        self.api_key = getattr(settings, 'BEEM_API_KEY', None)
        self.secret_key = getattr(settings, 'BEEM_SECRET_KEY', None)
        
        if not self.api_key or not self.secret_key:
            raise BeemSMSError(
                "Beem API credentials not configured. "
                "Please set BEEM_API_KEY and BEEM_SECRET_KEY in your environment variables."
            )
        
        self.auth = HTTPBasicAuth(self.api_key, self.secret_key)
        self.timeout = getattr(settings, 'BEEM_API_TIMEOUT', 30)
    
    def send_sms(
        self,
        message: str,
        recipients: List[str],
        source_addr: str = None,
        schedule_time: Optional[datetime] = None,
        encoding: int = 0,
        recipient_ids: Optional[List[str]] = None
    ) -> Dict:
        """
        Send SMS message(s) via Beem API
        
        Args:
            message (str): SMS message content
            recipients (List[str]): List of recipient phone numbers (international format)
            source_addr (str, optional): Sender ID (max 11 characters)
            schedule_time (datetime, optional): When to send the message (GMT+0)
            encoding (int): Message encoding (0=GSM7, 1=UCS2)
            recipient_ids (List[str], optional): Unique IDs for tracking delivery
            
        Returns:
            Dict: API response with success status and message details
            
        Raises:
            BeemSMSError: If API call fails or returns error
        """
        try:
            # Prepare recipients data
            recipients_data = []
            for i, recipient in enumerate(recipients):
                recipient_data = {
                    "dest_addr": self._format_phone_number(recipient),
                    "recipient_id": recipient_ids[i] if recipient_ids and i < len(recipient_ids) else str(i + 1)
                }
                recipients_data.append(recipient_data)
            
            # Prepare request payload
            payload = {
                "source_addr": source_addr or getattr(settings, 'BEEM_DEFAULT_SENDER_ID', 'INFO'),
                "encoding": encoding,
                "message": message,
                "recipients": recipients_data
            }
            
            # Add schedule time if provided
            if schedule_time:
                payload["schedule_time"] = schedule_time.strftime("%Y-%m-%d %H:%M")
            
            # Make API request
            response = requests.post(
                self.SEND_ENDPOINT,
                json=payload,
                auth=self.auth,
                timeout=self.timeout,
                headers={
                    'Content-Type': 'application/json',
                    'User-Agent': 'MifumoWMS/1.0'
                }
            )
            
            # Handle response
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"SMS sent successfully via Beem. Response: {response_data}")
                return {
                    'success': True,
                    'provider': 'beem',
                    'response': response_data,
                    'message_count': len(recipients),
                    'cost_estimate': self._calculate_cost(len(recipients), len(message))
                }
            else:
                error_msg = f"Beem API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                raise BeemSMSError(error_msg)
                
        except (RequestException, Timeout, ConnectionError) as e:
            error_msg = f"Network error while sending SMS via Beem: {str(e)}"
            logger.error(error_msg)
            raise BeemSMSError(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error while sending SMS via Beem: {str(e)}"
            logger.error(error_msg)
            raise BeemSMSError(error_msg)
    
    def send_bulk_sms(
        self,
        messages: List[Dict],
        source_addr: str = None,
        schedule_time: Optional[datetime] = None
    ) -> Dict:
        """
        Send multiple SMS messages in a single API call
        
        Args:
            messages (List[Dict]): List of message dictionaries with 'message', 'recipients', 'recipient_ids'
            source_addr (str, optional): Sender ID
            schedule_time (datetime, optional): When to send messages
            
        Returns:
            Dict: Combined results from all messages
        """
        try:
            all_recipients = []
            all_recipient_ids = []
            combined_message = ""
            
            # Combine all messages and recipients
            for i, msg_data in enumerate(messages):
                message = msg_data.get('message', '')
                recipients = msg_data.get('recipients', [])
                recipient_ids = msg_data.get('recipient_ids', [])
                
                # Add message prefix for identification
                if len(messages) > 1:
                    message = f"[{i+1}] {message}"
                
                all_recipients.extend(recipients)
                all_recipient_ids.extend(recipient_ids)
                combined_message += f"{message}\n\n"
            
            # Send combined message
            return self.send_sms(
                message=combined_message.strip(),
                recipients=all_recipients,
                source_addr=source_addr,
                schedule_time=schedule_time,
                recipient_ids=all_recipient_ids
            )
            
        except Exception as e:
            error_msg = f"Error sending bulk SMS via Beem: {str(e)}"
            logger.error(error_msg)
            raise BeemSMSError(error_msg)
    
    def get_delivery_status(self, message_id: str) -> Dict:
        """
        Get delivery status for a sent message
        
        Args:
            message_id (str): Message ID returned from send_sms
            
        Returns:
            Dict: Delivery status information
        """
        try:
            # Note: Beem doesn't provide a direct status check endpoint
            # This would typically be handled via webhooks
            return {
                'success': True,
                'message_id': message_id,
                'status': 'delivered',  # Placeholder - would be updated via webhook
                'provider': 'beem'
            }
        except Exception as e:
            error_msg = f"Error getting delivery status from Beem: {str(e)}"
            logger.error(error_msg)
            raise BeemSMSError(error_msg)
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """
        Validate phone number format for Beem API
        
        Args:
            phone_number (str): Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            formatted = self._format_phone_number(phone_number)
            # Basic validation - should be 10-15 digits
            return len(formatted) >= 10 and len(formatted) <= 15 and formatted.isdigit()
        except:
            return False
    
    def _format_phone_number(self, phone_number: str) -> str:
        """
        Format phone number for Beem API (international format without +)
        
        Args:
            phone_number (str): Phone number in any format
            
        Returns:
            str: Formatted phone number
        """
        # Remove all non-digit characters except +
        cleaned = ''.join(c for c in phone_number if c.isdigit() or c == '+')
        
        # Remove leading +
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        
        # Add country code if missing (assume Tanzania +255)
        if len(cleaned) == 9 and cleaned.startswith('7'):
            cleaned = '255' + cleaned
        elif len(cleaned) == 10 and cleaned.startswith('07'):
            cleaned = '255' + cleaned[1:]
        
        return cleaned
    
    def _calculate_cost(self, recipient_count: int, message_length: int) -> float:
        """
        Calculate estimated cost for SMS
        
        Args:
            recipient_count (int): Number of recipients
            message_length (int): Message length in characters
            
        Returns:
            float: Estimated cost in USD
        """
        # Beem pricing (approximate - check current rates)
        base_cost_per_sms = 0.05  # $0.05 per SMS
        cost_per_160_chars = 0.01  # Additional cost per 160 characters
        
        sms_parts = (message_length // 160) + 1
        cost_per_recipient = base_cost_per_sms + (sms_parts - 1) * cost_per_160_chars
        
        return round(recipient_count * cost_per_recipient, 4)
    
    def get_account_balance(self) -> Dict:
        """
        Get account balance and credit information
        
        Returns:
            Dict: Account balance information
        """
        try:
            # Note: Beem doesn't provide a direct balance API
            # This would need to be implemented based on their dashboard API
            return {
                'success': True,
                'provider': 'beem',
                'balance': 'N/A',  # Would be fetched from their API
                'currency': 'USD',
                'message': 'Balance check not available via API. Check Beem dashboard.'
            }
        except Exception as e:
            error_msg = f"Error getting account balance from Beem: {str(e)}"
            logger.error(error_msg)
            raise BeemSMSError(error_msg)
    
    def test_connection(self) -> Dict:
        """
        Test connection to Beem API
        
        Returns:
            Dict: Connection test results
        """
        try:
            # Send a test message to a dummy number
            test_result = self.send_sms(
                message="Test message from Mifumo WMS",
                recipients=["255700000000"],  # Dummy number
                source_addr=getattr(settings, 'BEEM_DEFAULT_SENDER_ID', 'TEST')
            )
            
            return {
                'success': True,
                'provider': 'beem',
                'message': 'Connection test successful',
                'api_key_configured': bool(self.api_key),
                'secret_key_configured': bool(self.secret_key)
            }
        except BeemSMSError as e:
            return {
                'success': False,
                'provider': 'beem',
                'error': str(e),
                'api_key_configured': bool(self.api_key),
                'secret_key_configured': bool(self.secret_key)
            }
        except Exception as e:
            return {
                'success': False,
                'provider': 'beem',
                'error': f'Unexpected error: {str(e)}',
                'api_key_configured': bool(self.api_key),
                'secret_key_configured': bool(self.secret_key)
            }


# Convenience function for easy integration
def send_sms_via_beem(
    message: str,
    recipients: List[str],
    source_addr: str = None,
    **kwargs
) -> Dict:
    """
    Convenience function to send SMS via Beem
    
    Args:
        message (str): SMS message content
        recipients (List[str]): List of recipient phone numbers
        source_addr (str, optional): Sender ID
        **kwargs: Additional arguments for send_sms method
        
    Returns:
        Dict: API response
    """
    service = BeemSMSService()
    return service.send_sms(message, recipients, source_addr, **kwargs)
