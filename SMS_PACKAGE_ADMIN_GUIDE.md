# SMS Package Admin Management Guide

## Overview
This guide covers how to manage SMS packages in the Mifumo WMS system. SMS packages can be created, updated, and managed both through the Django admin interface and command-line tools.

## Admin Interface Features

### Enhanced Admin Interface
The SMS package admin interface includes:

- **Visual Status Badges**: Color-coded badges for Popular/Regular and Active/Inactive status
- **Formatted Pricing**: Currency formatting for prices and unit prices
- **Savings Display**: Shows percentage savings compared to standard rate (30 TZS per SMS)
- **Bulk Actions**: Mark packages as popular/regular, activate/deactivate multiple packages
- **Advanced Filtering**: Filter by package type, status, popularity, and creation date
- **Search Functionality**: Search by name, package type, or sender ID

### Admin Interface Access
1. Navigate to Django Admin: `http://localhost:8000/admin/`
2. Go to **Billing** → **Sms packages**
3. Use the **"Add sms package"** button to create new packages

## Command Line Management

### Available Commands

#### 1. List SMS Packages
```bash
python manage.py list_sms_packages [options]
```

**Options:**
- `--active-only`: Show only active packages
- `--popular-only`: Show only popular packages
- `--type {lite,standard,pro,enterprise,custom}`: Filter by package type

**Example:**
```bash
python manage.py list_sms_packages --active-only --type pro
```

#### 2. Add SMS Package
```bash
python manage.py add_sms_package [options]
```

**Required Options:**
- `--name`: Package name (e.g., "Starter", "Business")
- `--type`: Package type (lite, standard, pro, enterprise, custom)
- `--credits`: Number of SMS credits
- `--price`: Price in TZS
- `--unit-price`: Price per SMS in TZS

**Optional Options:**
- `--popular`: Mark as popular package
- `--active`: Mark as active (default: True)
- `--features`: List of features (space-separated)
- `--default-sender-id`: Default sender ID
- `--sender-restriction`: Sender ID restriction policy
- `--allowed-sender-ids`: List of allowed sender IDs

**Example:**
```bash
python manage.py add_sms_package \
  --name "Premium" \
  --type pro \
  --credits 100000 \
  --price 3000000 \
  --unit-price 30 \
  --popular \
  --features "Premium SMS" "24/7 Support" "API Access"
```

#### 3. Update SMS Package
```bash
python manage.py update_sms_package [options]
```

**Required Options (choose one):**
- `--id`: Package ID (UUID)
- `--name`: Package name to search for

**Update Options:**
- `--new-name`: New package name
- `--credits`: New number of credits
- `--price`: New price in TZS
- `--unit-price`: New unit price in TZS
- `--popular`: Mark as popular
- `--not-popular`: Remove popular status
- `--active`: Mark as active
- `--inactive`: Mark as inactive
- `--features`: New list of features

**Example:**
```bash
python manage.py update_sms_package \
  --name "Premium" \
  --price 2500000 \
  --unit-price 25 \
  --popular
```

#### 4. Delete SMS Package
```bash
python manage.py delete_sms_package [options]
```

**Required Options (choose one):**
- `--id`: Package ID (UUID)
- `--name`: Package name to delete

**Options:**
- `--force`: Force delete even if packages have associated purchases
- `--dry-run`: Show what would be deleted without actually deleting

**Example:**
```bash
python manage.py delete_sms_package --name "Premium" --dry-run
```

#### 5. Create Sample Packages
```bash
python manage.py create_sample_sms_packages [options]
```

**Options:**
- `--clear-existing`: Clear all existing packages before creating new ones
- `--package-set {basic,comprehensive,enterprise}`: Package set to create (default: basic)

**Example:**
```bash
python manage.py create_sample_sms_packages --package-set comprehensive
```

## Package Configuration

### Package Types
- **lite**: Basic packages for small users
- **standard**: Standard packages for regular users
- **pro**: Professional packages for business users
- **enterprise**: Enterprise packages for large organizations
- **custom**: Custom packages with specific requirements

### Sender ID Restrictions
- **none**: No restriction - all sender IDs allowed
- **default_only**: Only default sender ID allowed
- **allowed_list**: Only sender IDs in the allowed list
- **custom_only**: Custom sender IDs only

### Features
Common features that can be assigned to packages:
- Basic SMS sending
- Priority SMS
- API Access
- Analytics
- Webhooks
- 24/7 Support
- Dedicated Support
- Custom Integration
- SLA Guarantee

## Database Schema

### SMSPackage Model Fields
- `id`: UUID primary key
- `name`: Package name (CharField, max 100 chars)
- `package_type`: Package type (choices)
- `credits`: Number of SMS credits (PositiveIntegerField)
- `price`: Price in TZS (DecimalField, 10 digits, 2 decimal places)
- `unit_price`: Price per SMS in TZS (DecimalField, 10 digits, 2 decimal places)
- `is_popular`: Popular package flag (BooleanField)
- `is_active`: Active package flag (BooleanField)
- `features`: List of features (JSONField)
- `default_sender_id`: Default sender ID (CharField, max 50 chars)
- `allowed_sender_ids`: List of allowed sender IDs (JSONField)
- `sender_id_restriction`: Sender ID restriction policy (CharField, choices)
- `created_at`: Creation timestamp (DateTimeField)
- `updated_at`: Last update timestamp (DateTimeField)

## Best Practices

### Package Pricing
- Set competitive unit prices based on market rates
- Use the savings percentage to highlight value
- Consider volume discounts for larger packages

### Package Features
- Clearly define what each feature includes
- Use consistent feature names across packages
- Consider user needs when assigning features

### Status Management
- Use "Popular" status for recommended packages
- Deactivate packages instead of deleting them when possible
- Keep a good mix of active packages for different user types

### Sender ID Configuration
- Set appropriate restrictions based on package tier
- Use "none" for basic packages to allow flexibility
- Use "allowed_list" for premium packages to maintain quality

## Troubleshooting

### Common Issues

1. **Package Already Exists**
   - Use `--name` with a different name
   - Check existing packages with `list_sms_packages`

2. **Cannot Delete Package with Purchases**
   - Use `--force` flag to force delete
   - Consider deactivating instead of deleting

3. **Admin Interface Not Loading**
   - Check Django admin configuration
   - Ensure user has proper permissions

4. **Command Not Found**
   - Ensure you're in the project root directory
   - Check that management commands are in the correct location

### Permissions
Ensure the user has the following permissions:
- `billing.add_smspackage`: Add SMS packages
- `billing.change_smspackage`: Modify SMS packages
- `billing.delete_smspackage`: Delete SMS packages
- `billing.view_smspackage`: View SMS packages

## API Integration

SMS packages are automatically available through the API endpoints:
- `GET /api/billing/sms/packages/`: List all active packages
- `GET /api/billing/sms/packages/{id}/`: Get specific package details

The API respects the `is_active` flag and will only return active packages by default.

## Monitoring and Analytics

Track package performance through:
- Purchase records in the admin interface
- Usage statistics via the API
- Revenue reports in the billing dashboard

## Support

For technical support or questions about SMS package management:
1. Check the Django admin logs
2. Review the command output for error messages
3. Verify database connectivity
4. Check user permissions

---

*Last updated: October 2024*

