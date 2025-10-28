# API Keys Cleanup Command

This management command helps clean up dummy/test API keys and webhooks from your database.

## Usage

### Basic cleanup (interactive)
```bash
python manage.py cleanup_api_keys
```

### Delete all webhooks
```bash
python manage.py cleanup_api_keys --delete-webhooks
```

### Keep only the latest active API key per account
```bash
python manage.py cleanup_api_keys --keep-latest
```

### Run without confirmation
```bash
python manage.py cleanup_api_keys --keep-latest --delete-webhooks --force
```

### Keep multiple keys per user
```bash
python manage.py cleanup_api_keys --keep 3 --force
```

## Options

- `--keep-latest`: Keep only the latest active API key per account, delete all older ones
- `--delete-webhooks`: Delete all webhooks
- `--keep N`: Keep N active API keys per user (default: 1)
- `--force`: Run without confirmation prompt

## Examples

### Clean up all dummy/test data
```bash
python manage.py cleanup_api_keys --keep-latest --delete-webhooks --force
```

This will:
- Delete all revoked/inactive API keys
- Keep only the most recent active API key per account
- Delete all webhooks
- Run without asking for confirmation

### Interactive cleanup
```bash
python manage.py cleanup_api_keys
```

This will:
- Show you what will be deleted
- Ask for confirmation before proceeding
- Delete revoked/inactive keys
- Keep webhooks intact

## What Gets Deleted

- **Revoked API keys**: Keys with status 'revoked'
- **Expired API keys**: Keys with status 'expired'
- **Old active keys**: When using `--keep-latest`, all but the most recent active key
- **All webhooks**: When using `--delete-webhooks`

## What's Kept

- Active API keys (by default, the most recent one per account)
- Key usage statistics and logs

## Notes

- This command does NOT delete API usage logs or statistics
- This command does NOT delete API accounts
- Be careful in production - deleted keys cannot be recovered

