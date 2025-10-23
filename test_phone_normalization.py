#!/usr/bin/env python3
"""
Test phone number normalization
"""

import re
import phonenumbers
from phonenumbers import NumberParseException

def _normalize_phone_to_e164(phone):
    """Normalize phone number to E.164 format with comprehensive format support."""
    if not phone:
        return None

    # Clean the phone number - remove spaces, dashes, parentheses
    cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone.strip())

    # If it's already in E.164 format, return as is
    if cleaned_phone.startswith('+') and len(cleaned_phone) >= 12:
        try:
            parsed = phonenumbers.parse(cleaned_phone, None)
            if phonenumbers.is_valid_number(parsed):
                return cleaned_phone
        except NumberParseException:
            pass

    # Try to parse with different country codes
    country_codes = ['TZ', 'KE', 'UG', 'RW', 'BI']  # East African countries

    for country in country_codes:
        try:
            parsed = phonenumbers.parse(cleaned_phone, country)
            if phonenumbers.is_valid_number(parsed):
                return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            continue

    # Fallback to manual normalization for Tanzanian numbers
    digits = re.sub(r'\D', '', cleaned_phone)

    # Handle Tanzanian number patterns
    if digits.startswith('255') and len(digits) == 12:
        return f"+{digits}"
    elif digits.startswith('0') and len(digits) == 10:
        return f"+255{digits[1:]}"
    elif len(digits) == 9 and digits.startswith(('6', '7', '8', '9')):
        # Local format without leading 0
        return f"+255{digits}"
    elif len(digits) == 10 and digits.startswith('0'):
        # Local format with leading 0
        return f"+255{digits[1:]}"
    elif len(digits) == 12 and digits.startswith('255'):
        # International format without +
        return f"+{digits}"

    # If we can't normalize, return the cleaned version
    return cleaned_phone if cleaned_phone else phone

def test_phone_normalization():
    """Test phone number normalization"""
    print("🔍 Testing Phone Number Normalization")
    print("=" * 50)

    test_phones = [
        "+255712345678",
        "255712345679",
        "0712345678",
        "0712345679",
        "712345678",
        "712345679"
    ]

    for phone in test_phones:
        normalized = _normalize_phone_to_e164(phone)
        print(f"'{phone}' -> '{normalized}'")

if __name__ == "__main__":
    test_phone_normalization()
