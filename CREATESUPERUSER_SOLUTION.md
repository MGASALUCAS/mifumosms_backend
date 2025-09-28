# Createsuperuser Solution for Custom User Model

## Problem
Django's built-in `createsuperuser` command doesn't work with custom user models that use `email` as the `USERNAME_FIELD`.

## Solution
We've created a custom management command `create_admin` that works perfectly with our custom user model.

## Usage Options

### Option 1: Use the custom management command (Recommended)
```bash
python manage.py create_admin --email admin@example.com --first-name Admin --last-name User --password securepass123
```

### Option 2: Use the simple Python script
```bash
python createsuperuser.py admin@example.com Admin User securepass123
```

### Option 3: Interactive mode
```bash
python manage.py create_admin
```
Then follow the prompts.

## What it does
1. Creates a superuser with the custom User model
2. Creates a tenant (if it doesn't exist)
3. Creates a membership linking the user to the tenant
4. Provides all necessary credentials and URLs

## Admin Access
- **Admin URL**: `http://localhost:8000/admin/`
- **Email**: The email you provided
- **Password**: The password you provided

## Why this works
Our custom User model uses `email` as the `USERNAME_FIELD`, but Django's built-in `createsuperuser` still expects a `username` parameter. Our custom command handles this correctly by passing `username=email` to the `create_user()` method.
