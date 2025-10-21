"""
SMS Service for Mifumo WMS.
Implements multiple SMS providers with Beem Africa as the primary provider.
"""
import requests
import logging
import base64
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Tuple
from django.conf import settings
from django.utils import timezone as django_timezone

from ..models_sms import SMSProvider, SMSSenderID, SMSTemplate, SMSMessage, SMSDeliveryReport

logger = logging.getLogger(__name__)


class BaseSMSProvider:
    """
    Base class for SMS providers.
    """
    
    def __init__(self, provider: SMSProvider):
        self.provider = provider
        self.api_key = provider.api_key
        self.secret_key = provider.secret_key
        self.api_url = provider.api_url
        self.settings = provider.settings or {}
    
    def send_sms(self, to: str, message: str, sender_id: str, **kwargs) -> Dict[str, Any]:
        """Send SMS message."""
        raise NotImplementedError
    
    def check_balance(self) -> Dict[str, Any]:
        """Check account balance."""
        raise NotImplementedError
    
    def get_delivery_report(self, request_id: str, dest_addr: str) -> Dict[str, Any]:
        """Get delivery report for a message."""
        raise NotImplementedError
    
    def create_sender_id(self, sender_id: str, sample_content: str) -> Dict[str, Any]:
        """Create/register a sender ID."""
        raise NotImplementedError
    
    def get_sender_ids(self) -> Dict[str, Any]:
        """Get list of sender IDs."""
        raise NotImplementedError
    
    def create_template(self, name: str, message: str) -> Dict[str, Any]:
        """Create SMS template."""
        raise NotImplementedError
    
    def get_templates(self) -> Dict[str, Any]:
        """Get list of templates."""
        raise NotImplementedError


class BeemSMSService(BaseSMSProvider):
    """
    Beem Africa SMS service implementation.
    """
    
    def __init__(self, provider: SMSProvider):
        super().__init__(provider)
        # Use environment variables for API URLs
        self.send_url = getattr(settings, 'BEEM_SEND_URL', 'https://apisms.beem.africa/v1/send')
        self.balance_url = getattr(settings, 'BEEM_BALANCE_URL', 'https://apisms.beem.africa/public/v1/vendors/balance')
        self.delivery_url = getattr(settings, 'BEEM_DELIVERY_URL', 'https://dlrapi.beem.africa/public/v1/delivery-reports')
        self.sender_url = getattr(settings, 'BEEM_SENDER_URL', 'https://apisms.beem.africa/public/v1/sender-names')
        self.template_url = getattr(settings, 'BEEM_TEMPLATE_URL', 'https://apisms.beem.africa/public/v1/sms-templates')
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header."""
        credentials = f"{self.api_key}:{self.secret_key}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded_credentials}"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get standard headers for API requests."""
        return {
            'Content-Type': 'application/json',
            'Authorization': self._get_auth_header()
        }
    
    def _detect_encoding(self, message: str) -> int:
        """
        Detect the appropriate encoding for SMS message.
        
        Args:
            message: SMS message content
            
        Returns:
            int: 0 for GSM7 (standard), 1 for UCS2 (Unicode/emojis)
        """
        try:
            # Check if message contains emojis or non-GSM7 characters
            # GSM7 character set includes basic Latin characters, numbers, and some symbols
            gsm7_chars = set(
                'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
                '0123456789@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ '
                '!"#%&\'()*+,-./:;<=>?¡ÄÖÑÜ§¿äöñüà'
            )
            
            # Check if any character is not in GSM7 set
            for char in message:
                if char not in gsm7_chars:
                    # Character is not in GSM7 set, likely emoji or Unicode
                    logger.info(f"Non-GSM7 character detected: '{char}' - using UCS2 encoding")
                    return 1  # UCS2 encoding for Unicode/emojis
            
            # All characters are GSM7 compatible
            return 0  # GSM7 encoding
            
        except Exception as e:
            logger.warning(f"Error detecting encoding: {e} - defaulting to UCS2")
            return 1  # Default to UCS2 for safety
    
    def send_sms(self, to: str, message: str, sender_id: str, **kwargs) -> Dict[str, Any]:
        """
        Send SMS message via Beem Africa.
        
        Args:
            to: Phone number in E.164 format (without +)
            message: SMS message content
            sender_id: Sender ID
            **kwargs: Additional parameters (schedule_time, recipient_id, etc.)
        
        Returns:
            Dict with success status and message ID or error
        """
        try:
            # Prepare recipients array
            recipients = [{
                "recipient_id": kwargs.get('recipient_id', 1),
                "dest_addr": to
            }]
            
            # Auto-detect encoding based on message content
            encoding = self._detect_encoding(message)
            
            # Prepare request data
            data = {
                "source_addr": sender_id,
                "message": message,
                "encoding": encoding,
                "recipients": recipients
            }
            
            # Add optional parameters
            if kwargs.get('schedule_time'):
                data["schedule_time"] = kwargs['schedule_time']
            
            # Make API request
            response = requests.post(
                self.send_url,
                json=data,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('successful'):
                return {
                    'success': True,
                    'request_id': response_data.get('request_id'),
                    'message_id': response_data.get('request_id'),
                    'valid_count': response_data.get('valid', 0),
                    'invalid_count': response_data.get('invalid', 0),
                    'duplicates_count': response_data.get('duplicates', 0),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Unknown error'),
                    'error_code': response_data.get('code'),
                    'response': response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Beem SMS API request failed: {str(e)}")
            return {
                'success': False,
                'error': f"API request failed: {str(e)}",
                'error_code': 'NETWORK_ERROR'
            }
        except Exception as e:
            logger.error(f"Beem SMS service error: {str(e)}")
            return {
                'success': False,
                'error': f"Service error: {str(e)}",
                'error_code': 'SERVICE_ERROR'
            }
    
    def check_balance(self) -> Dict[str, Any]:
        """Check account balance."""
        try:
            response = requests.get(
                self.balance_url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'balance': response_data.get('data', {}).get('credit_balance', 0),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to check balance'),
                    'response': response_data
                }
                
        except Exception as e:
            logger.error(f"Beem balance check failed: {str(e)}")
            return {
                'success': False,
                'error': f"Balance check failed: {str(e)}"
            }
    
    def get_delivery_report(self, request_id: str, dest_addr: str) -> Dict[str, Any]:
        """Get delivery report for a message."""
        try:
            params = {
                'dest_addr': dest_addr,
                'request_id': request_id
            }
            
            response = requests.get(
                self.delivery_url,
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'reports': response_data if isinstance(response_data, list) else [response_data],
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('error', 'Failed to get delivery report'),
                    'response': response_data
                }
                
        except Exception as e:
            logger.error(f"Beem delivery report failed: {str(e)}")
            return {
                'success': False,
                'error': f"Delivery report failed: {str(e)}"
            }
    
    def create_sender_id(self, sender_id: str, sample_content: str) -> Dict[str, Any]:
        """Create/register a sender ID."""
        try:
            data = {
                "senderid": sender_id,
                "sample_content": sample_content
            }
            
            response = requests.post(
                self.sender_url,
                json=data,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'sender_id': response_data.get('data', {}).get('senderid'),
                    'id': response_data.get('data', {}).get('id'),
                    'status': response_data.get('data', {}).get('status'),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to create sender ID'),
                    'response': response_data
                }
                
        except Exception as e:
            logger.error(f"Beem sender ID creation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Sender ID creation failed: {str(e)}"
            }
    
    def get_sender_ids(self, q: str = None, status: str = None) -> Dict[str, Any]:
        """Get list of sender IDs."""
        try:
            params = {}
            if q:
                params['q'] = q
            if status:
                params['status'] = status
            
            response = requests.get(
                self.sender_url,
                params=params,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'sender_ids': response_data.get('data', []),
                    'pagination': response_data.get('pagination', {}),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to get sender IDs'),
                    'response': response_data
                }
                
        except Exception as e:
            logger.error(f"Beem sender IDs fetch failed: {str(e)}")
            return {
                'success': False,
                'error': f"Sender IDs fetch failed: {str(e)}"
            }
    
    def create_template(self, name: str, message: str) -> Dict[str, Any]:
        """Create SMS template."""
        try:
            data = {
                "sms_title": name,
                "message": message
            }
            
            response = requests.post(
                self.template_url,
                json=data,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'template_id': response_data.get('data', {}).get('id'),
                    'template_name': response_data.get('data', {}).get('sms_title'),
                    'message': response_data.get('data', {}).get('message'),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to create template'),
                    'response': response_data
                }
                
        except Exception as e:
            logger.error(f"Beem template creation failed: {str(e)}")
            return {
                'success': False,
                'error': f"Template creation failed: {str(e)}"
            }
    
    def get_templates(self) -> Dict[str, Any]:
        """Get list of templates."""
        try:
            response = requests.get(
                self.template_url,
                headers=self._get_headers(),
                timeout=30
            )
            
            response_data = response.json()
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'templates': response_data.get('data', []),
                    'pagination': response_data.get('pagination', {}),
                    'response': response_data
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Failed to get templates'),
                    'response': response_data
                }
                
        except Exception as e:
            logger.error(f"Beem templates fetch failed: {str(e)}")
            return {
                'success': False,
                'error': f"Templates fetch failed: {str(e)}"
            }


class SMSService:
    """
    Main SMS service that manages multiple providers.
    """
    
    def __init__(self, tenant_id: str = None):
        self.tenant_id = tenant_id
        self._providers = {}
    
    def get_provider(self, provider_id: str = None) -> BaseSMSProvider:
        """Get SMS provider instance."""
        if not provider_id:
            # Get default provider for tenant
            provider = SMSProvider.objects.filter(
                tenant_id=self.tenant_id,
                is_active=True,
                is_default=True
            ).first()
            
            if not provider:
                provider = SMSProvider.objects.filter(
                    tenant_id=self.tenant_id,
                    is_active=True
                ).first()
        else:
            provider = SMSProvider.objects.get(id=provider_id)
        
        if not provider:
            raise ValueError("No active SMS provider found")
        
        # Cache provider instances
        if provider.id not in self._providers:
            if provider.provider_type == 'beem':
                self._providers[provider.id] = BeemSMSService(provider)
            else:
                raise ValueError(f"Unsupported provider type: {provider.provider_type}")
        
        return self._providers[provider.id]
    
    def send_sms(self, to: str, message: str, sender_id: str, provider_id: str = None, **kwargs) -> Dict[str, Any]:
        """Send SMS message."""
        provider = self.get_provider(provider_id)
        return provider.send_sms(to, message, sender_id, **kwargs)
    
    def check_balance(self, provider_id: str = None) -> Dict[str, Any]:
        """Check account balance."""
        provider = self.get_provider(provider_id)
        return provider.check_balance()
    
    def get_delivery_report(self, request_id: str, dest_addr: str, provider_id: str = None) -> Dict[str, Any]:
        """Get delivery report."""
        provider = self.get_provider(provider_id)
        return provider.get_delivery_report(request_id, dest_addr)
    
    def create_sender_id(self, sender_id: str, sample_content: str, provider_id: str = None) -> Dict[str, Any]:
        """Create sender ID."""
        provider = self.get_provider(provider_id)
        return provider.create_sender_id(sender_id, sample_content)
    
    def get_sender_ids(self, provider_id: str = None, **kwargs) -> Dict[str, Any]:
        """Get sender IDs."""
        provider = self.get_provider(provider_id)
        return provider.get_sender_ids(**kwargs)
    
    def create_template(self, name: str, message: str, provider_id: str = None) -> Dict[str, Any]:
        """Create template."""
        provider = self.get_provider(provider_id)
        return provider.create_template(name, message)
    
    def get_templates(self, provider_id: str = None) -> Dict[str, Any]:
        """Get templates."""
        provider = self.get_provider(provider_id)
        return provider.get_templates()


class SMSBulkProcessor:
    """
    Handles bulk SMS processing from Excel uploads.
    """
    
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id
        self.sms_service = SMSService(tenant_id)
    
    def process_excel_upload(self, file_path: str, campaign_id: str = None) -> Dict[str, Any]:
        """
        Process Excel file for bulk SMS sending.
        
        Expected Excel format:
        - Column A: Phone Number (E.164 format)
        - Column B: Name (optional)
        - Column C: Message (optional, uses template if not provided)
        - Column D: Sender ID (optional, uses default if not provided)
        - Additional columns: Custom variables for template
        """
        try:
            import pandas as pd
            
            # Read Excel file
            df = pd.read_excel(file_path)
            
            # Validate required columns
            if 'phone' not in df.columns and 'Phone' not in df.columns:
                return {
                    'success': False,
                    'error': 'Phone number column is required'
                }
            
            # Process each row
            results = []
            errors = []
            
            for index, row in df.iterrows():
                try:
                    # Extract phone number
                    phone_col = 'phone' if 'phone' in df.columns else 'Phone'
                    phone = str(row[phone_col]).strip()
                    
                    # Clean phone number (remove + if present)
                    if phone.startswith('+'):
                        phone = phone[1:]
                    
                    # Extract other data
                    name = row.get('name', row.get('Name', phone))
                    message = row.get('message', row.get('Message', ''))
                    sender_id = row.get('sender_id', row.get('Sender ID', ''))
                    
                    # Extract custom variables
                    variables = {}
                    for col in df.columns:
                        if col.lower() not in ['phone', 'name', 'message', 'sender_id']:
                            variables[col.lower()] = str(row[col]) if pd.notna(row[col]) else ''
                    
                    # Send SMS
                    result = self.sms_service.send_sms(
                        to=phone,
                        message=message,
                        sender_id=sender_id,
                        recipient_id=index + 1,
                        **variables
                    )
                    
                    results.append({
                        'row': index + 1,
                        'phone': phone,
                        'name': name,
                        'success': result['success'],
                        'message_id': result.get('message_id'),
                        'error': result.get('error')
                    })
                    
                except Exception as e:
                    errors.append({
                        'row': index + 1,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'total_rows': len(df),
                'processed_rows': len(results),
                'successful_rows': len([r for r in results if r['success']]),
                'failed_rows': len(errors),
                'results': results,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Excel processing failed: {str(e)}")
            return {
                'success': False,
                'error': f"Excel processing failed: {str(e)}"
            }
