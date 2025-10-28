# SMS Package Ranges Update

## Summary

Updated the SMS package ranges and credit amounts to reflect the new tier structure:

- **Lite**: 1 to 49,999 SMS
- **Standard**: 50,000 to 149,999 SMS  
- **Pro**: 250,000 SMS and above

## Changes Made

### 1. Updated Model Subtitle Property (`billing/models.py`)

The `subtitle` property now returns range-based text instead of just credit amounts:

```python
@property
def subtitle(self):
    """Generate package subtitle showing credit range."""
    # Return range-based subtitle based on package type
    if self.package_type == 'lite':
        return "1 to 49,999 SMS"
    elif self.package_type == 'standard':
        return "50,000 to 149,999 SMS"
    elif self.package_type == 'pro':
        return "250,000 SMS and above"
    else:
        return f"{self.credits:,} SMS Credits"
```

### 2. Updated Package Credit Amounts (`billing/management/commands/setup_sms_packages.py`)

Updated the actual credit amounts to reflect the maximums of each range:

| Package | Old Credits | New Credits | Price (TZS) | Unit Price (TZS/SMS) |
|---------|------------|-------------|-------------|---------------------|
| **Lite** | 5,000 | **49,999** | 899,982 | 18.00 |
| **Standard** | 50,000 | **149,999** | 2,099,986 | 14.00 |
| **Pro** | 250,000 | **250,000** | 3,000,000 | 12.00 |

## Database Update

Packages have been successfully updated in the database:

```
- Lite: 49,999 credits, 899,982.00 TZS, 18.00 TZS/SMS (40.0% savings)
- Standard: 149,999 credits, 2,099,986.00 TZS, 14.00 TZS/SMS (53.3% savings)
- Pro: 250,000 credits, 3,000,000.00 TZS, 12.00 TZS/SMS (60.0% savings)
```

## Impact

- **Frontend**: Will now display the new range-based subtitles instead of credit amounts
- **Pricing**: Prices updated to reflect the new credit amounts at the same unit prices
- **Savings**: All packages maintain their same discount percentages (40%, 53.3%, 60%)

## Notes

- The `subtitle` property is dynamically generated based on package type
- Credits represent the maximum value purchasable in each tier
- Prices are calculated by multiplying credits by the unit price
- The ranges clearly separate each package tier for better user understanding

## Command to Re-run

If you need to update the packages again:

```bash
python manage.py setup_sms_packages --update
```

Or to reset and recreate all packages:

```bash
python manage.py setup_sms_packages --reset
```

