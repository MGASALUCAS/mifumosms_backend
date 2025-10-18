"""
ZenoPay Payment Gateway Service
Handles integration with ZenoPay Mobile Money Tanzania API
"""
import requests
import logging
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid

logger = logging.getLogger(__name__)


class ZenoPayService:
    """
    Service class for ZenoPay payment gateway integration.
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'ZENOPAY_API_KEY', '')
        # For testing purposes, if no API key is set, use a placeholder
        if not self.api_key:
            logger.warning("ZENOPAY_API_KEY is not configured. Please set it in your .env file.")
            # You can temporarily set a test API key here for testing
            # self.api_key = 'your_test_api_key_here'
        self.base_url = 'https://zenoapi.com/api/payments'
        self.timeout = getattr(settings, 'ZENOPAY_API_TIMEOUT', 30)
        
    def _get_headers(self):
        """Get headers for ZenoPay API requests."""
        return {
            'Content-Type': 'application/json',
            'x-api-key': self.api_key
        }
    
    def _validate_phone_number(self, phone):
        """
        Validate and format Tanzanian phone number.
        Expected format: 07XXXXXXXX (as per ZenoPay docs)
        """
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))
        
        # Handle different input formats
        if phone.startswith('07'):
            # Already in correct format
            return phone
        elif phone.startswith('06'):
            # Halotel numbers (06 prefix) - keep as is
            return phone
        elif phone.startswith('255'):
            # Convert from international format to local
            if phone[3:5] in ['07', '06']:
                return '0' + phone[3:]
            else:
                return '0' + phone[3:]
        else:
            # Assume it's missing the prefix
            if len(phone) == 9:
                return '0' + phone
            else:
                return '07' + phone
    
    def create_payment(self, order_id, buyer_email, buyer_name, buyer_phone, amount, webhook_url=None, mobile_money_provider='vodacom'):
        """
        Create a payment request with ZenoPay.
        
        Args:
            order_id (str): Unique order identifier
            buyer_email (str): Customer email
            buyer_name (str): Customer name
            buyer_phone (str): Customer phone number (format: 07XXXXXXXX)
            amount (Decimal): Amount in TZS
            webhook_url (str, optional): Webhook URL for status updates
            mobile_money_provider (str): Mobile money provider (vodacom, halotel, tigo, airtel)
            
        Returns:
            dict: ZenoPay API response
        """
        try:
            # Validate and format phone number to 07XXXXXXXX format
            formatted_phone = self._validate_phone_number(buyer_phone)
            
            # Prepare payload according to ZenoPay documentation
            payload = {
                'order_id': order_id,
                'buyer_email': buyer_email,
                'buyer_name': buyer_name,
                'buyer_phone': formatted_phone,
                'amount': int(amount)  # ZenoPay expects integer amount
            }
            
            # Add webhook URL if provided (as per ZenoPay docs)
            if webhook_url:
                payload['webhook_url'] = webhook_url
            
            # Make API request to the correct endpoint
            response = requests.post(
                f"{self.base_url}/mobile_money_tanzania",
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            # Log the request and response
            logger.info(f"ZenoPay Payment Request: {payload}")
            logger.info(f"ZenoPay Response Status: {response.status_code}")
            logger.info(f"ZenoPay Response: {response.text}")
            
            # Parse response
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('status') == 'success':
                return {
                    'success': True,
                    'data': response_data,
                    'order_id': response_data.get('order_id'),
                    'message': response_data.get('message', 'Payment request created successfully')
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Payment request failed'),
                    'response_data': response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"ZenoPay API request failed: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"ZenoPay payment creation error: {str(e)}")
            return {
                'success': False,
                'error': f'Payment creation failed: {str(e)}'
            }
    
    def check_payment_status(self, order_id):
        """
        Check payment status with ZenoPay.
        
        Args:
            order_id (str): Order ID to check
            
        Returns:
            dict: Payment status response
        """
        try:
            # Make API request
            response = requests.get(
                f"{self.base_url}/order-status",
                params={'order_id': order_id},
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            # Log the request and response
            logger.info(f"ZenoPay Status Check for Order: {order_id}")
            logger.info(f"ZenoPay Status Response: {response.status_code}")
            logger.info(f"ZenoPay Status Data: {response.text}")
            
            # Parse response
            response_data = response.json()
            
            if response.status_code == 200:
                # Parse ZenoPay response according to their API documentation
                data_array = response_data.get('data', [])
                payment_data = data_array[0] if data_array else {}
                
                return {
                    'success': True,
                    'data': response_data,
                    'payment_status': response_data.get('result', 'UNKNOWN'),  # This is the 'result' field
                    'reference': response_data.get('reference'),
                    'transid': payment_data.get('transid'),
                    'channel': payment_data.get('channel'),
                    'msisdn': payment_data.get('msisdn'),
                    'order_id': payment_data.get('order_id'),
                    'amount': payment_data.get('amount'),
                    'creation_date': payment_data.get('creation_date')
                }
            else:
                return {
                    'success': False,
                    'error': response_data.get('message', 'Status check failed'),
                    'response_data': response_data
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"ZenoPay status check failed: {str(e)}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            logger.error(f"ZenoPay status check error: {str(e)}")
            return {
                'success': False,
                'error': f'Status check failed: {str(e)}'
            }
    
    def process_webhook(self, webhook_data):
        """
        Process webhook notification from ZenoPay.
        
        Args:
            webhook_data (dict): Webhook payload from ZenoPay
            
        Returns:
            dict: Processed webhook data
        """
        try:
            # Extract relevant data from webhook
            order_id = webhook_data.get('order_id')
            payment_status = webhook_data.get('payment_status')
            reference = webhook_data.get('reference')
            
            logger.info(f"Processing ZenoPay webhook for order {order_id}: {payment_status}")
            
            return {
                'success': True,
                'order_id': order_id,
                'payment_status': payment_status,
                'reference': reference,
                'webhook_data': webhook_data
            }
            
        except Exception as e:
            logger.error(f"ZenoPay webhook processing error: {str(e)}")
            return {
                'success': False,
                'error': f'Webhook processing failed: {str(e)}'
            }
    
    def generate_order_id(self):
        """Generate a unique order ID for ZenoPay."""
        return str(uuid.uuid4())
    
    def format_amount(self, amount):
        """Format amount for ZenoPay (convert to integer TZS)."""
        if isinstance(amount, Decimal):
            return int(amount)
        return int(amount)


# Global instance
zenopay_service = ZenoPayService()
