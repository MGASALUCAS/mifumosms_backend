# 📱 Mifumo SMS Purchase Page Setup

## 🚀 Quick Start

### 1. Start Django Server
```bash
python manage.py runserver
```

### 2. Start Purchase Page Server
```bash
python serve_purchase_page.py
```

### 3. Open Purchase Page
Open your browser and go to: **http://localhost:8080/purchase_packages.html**

## ✨ Features

### 📦 Package Selection
- **Browse all SMS packages** with pricing and features
- **Visual package cards** with popular package highlighting
- **Real-time package information** from the database

### 💳 Payment Flow
- **Auto-suggest mobile money provider** based on phone number
- **Form validation** for all required fields
- **Real-time payment initiation** with ZenoPay
- **Payment status tracking** with progress indicators

### 📱 Mobile Money Integration
- **Vodacom M-Pesa** (074, 075, 076, 078)
- **Tigo Pesa** (065, 066, 067, 068, 069)
- **Airtel Money** (071, 073)
- **Halotel Money** (061, 062, 063, 064)

## 🔧 Technical Details

### API Endpoints Used
- `GET /api/billing/sms/packages/` - Get available packages
- `POST /api/auth/login/` - User authentication
- `POST /api/billing/payments/initiate/` - Initiate payment

### Phone Number Auto-Detection
The page automatically suggests the correct mobile money provider based on your phone number prefix:

| Prefix | Provider | App |
|--------|----------|-----|
| 061xxx | Halotel | Halotel Money |
| 062xxx | Halotel | Halotel Money |
| 063xxx | Halotel | Halotel Money |
| 064xxx | Halotel | Halotel Money |
| 065xxx | Tigo | Tigo Pesa |
| 066xxx | Tigo | Tigo Pesa |
| 067xxx | Tigo | Tigo Pesa |
| 068xxx | Tigo | Tigo Pesa |
| 069xxx | Tigo | Tigo Pesa |
| 071xxx | Airtel | Airtel Money |
| 073xxx | Airtel | Airtel Money |
| 074xxx | Vodacom | M-Pesa |
| 075xxx | Vodacom | M-Pesa |
| 076xxx | Vodacom | M-Pesa |
| 078xxx | Vodacom | M-Pesa |

## 🧪 Testing

### Test API Endpoints
```bash
python simple_purchase_test.py
```

### Test Complete Flow
1. Open the purchase page
2. Select a package
3. Fill in your details (use your real phone number)
4. Click "Initiate Payment"
5. Check your phone for push notification
6. Complete payment on your mobile device

## 🎯 Example Usage

### For Halotel Users (061xxx numbers)
1. Enter phone: `0614853618`
2. Provider auto-selects: `halotel`
3. Complete payment on Halotel Money app

### For Vodacom Users (074xxx, 075xxx, 076xxx, 078xxx numbers)
1. Enter phone: `0757347863`
2. Provider auto-selects: `vodacom`
3. Complete payment on M-Pesa app

## 🔍 Troubleshooting

### No Push Notification?
1. **Check your phone number prefix** - make sure you're using the correct provider
2. **Check your mobile money app** - make sure it's installed and notifications are enabled
3. **Check your phone settings** - make sure push notifications are allowed
4. **Try a different amount** - some providers have minimum amounts

### Payment Not Working?
1. **Check your internet connection**
2. **Make sure Django server is running** on port 8000
3. **Check browser console** for JavaScript errors
4. **Verify your phone number format** (07XXXXXXXX or 06XXXXXXXX)

## 📋 Files Created

- `purchase_packages.html` - Main purchase page
- `serve_purchase_page.py` - Local server for the page
- `simple_purchase_test.py` - API testing script
- `PURCHASE_PAGE_SETUP.md` - This setup guide

## 🎉 Success!

Once everything is working, you'll have a beautiful, functional SMS package purchase page that:
- ✅ Displays all available packages
- ✅ Handles user authentication
- ✅ Initiates payments with ZenoPay
- ✅ Provides real-time feedback
- ✅ Works with all major mobile money providers in Tanzania

**Happy purchasing!** 🚀
