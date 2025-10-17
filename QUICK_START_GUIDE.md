# 🚀 Quick Start Guide - Mifumo SMS Purchase System

## ✅ **Both Servers Are Now Running!**

### **Django API Server**
- **URL:** http://localhost:8000
- **Status:** ✅ Running
- **Purpose:** Handles authentication, packages, and payments

### **Purchase Page Server**
- **URL:** http://localhost:8080/purchase_packages.html
- **Status:** ✅ Running
- **Purpose:** Beautiful web interface for purchasing SMS packages

## 🎯 **How to Use**

### **1. Open the Purchase Page**
Go to: **http://localhost:8080/purchase_packages.html**

### **2. Select a Package**
- **Lite:** 5,000 credits for 150,000 TZS
- **Standard:** 50,000 credits for 1,250,000 TZS (Popular)
- **Pro:** 250,000 credits for 4,500,000 TZS
- **Enterprise:** 1,000,000 credits for 12,000,000 TZS

### **3. Fill in Your Details**
- **Name:** Your full name
- **Email:** Your email address
- **Phone:** 0614853618 (your Halotel number)
- **Provider:** Will auto-select "Halotel" for your number

### **4. Complete Payment**
- Click "Initiate Payment"
- Check your phone for Halotel Money push notification
- Complete payment on your mobile device
- Receive SMS credits automatically

## 🔧 **Troubleshooting**

### **If Page Shows "Loading packages...":**
1. **Press Ctrl+F5** to force refresh
2. **Open Developer Tools** (F12) and check Console tab
3. **Check Network tab** for failed requests

### **If No Push Notification:**
1. **Check Halotel Money app** - Make sure it's installed
2. **Enable notifications** - Settings > Apps > Halotel Money > Notifications
3. **Contact Halotel support** - *149*149#

### **If Servers Stop:**
1. **Run:** `start_servers.bat` (Windows)
2. **Or run:** `python start_servers.py`
3. **Or manually start:**
   - Django: `python manage.py runserver`
   - Purchase Page: `python serve_purchase_page.py`

## 📱 **Phone Number Guide**

| Phone Number | Provider | App |
|--------------|----------|-----|
| 0614853618 | Halotel | Halotel Money |
| 0744963858 | Vodacom | M-Pesa |
| 0651234567 | Tigo | Tigo Pesa |
| 0712345678 | Airtel | Airtel Money |

## 🎉 **Success Indicators**

You'll know it's working when:
- ✅ Packages load on the page
- ✅ Payment initiation succeeds
- ✅ You receive push notification on phone
- ✅ You can complete payment in mobile money app
- ✅ SMS credits are added to your account

## 📞 **Support**

- **Halotel Support:** *149*149#
- **Technical Issues:** Check console logs (F12)
- **API Documentation:** http://localhost:8000/swagger/

**The system is now fully operational!** 🚀
