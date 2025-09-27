# 🚀 TradingView API Management v2
**Advanced RESTful API System for Pine Script Access Management with Secure Admin Panel**

[![Replit](https://img.shields.io/badge/Deploy%20on-Replit-blue?logo=replit)](https://replit.com/@trendoscope/Tradingview-Access-Management)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black?logo=github)](https://github.com/diazpolanco13/TradingView-API-Management-v2)

> **⚡ Complete automation solution for TradingView Pine Script access management with secure authentication, real-time validation, and professional admin interface.**

---

## 🌟 **What's New in v2**

### 🎯 **Major Enhancements**
- ✅ **Secure Web Admin Panel** - Professional interface with token-based authentication
- ✅ **Real-time Cookie Management** - Automatic validation and manual update system  
- ✅ **Individual Endpoint Testing** - Six dedicated test buttons for each API function
- ✅ **Enhanced Security** - Header-based admin token authentication (never in URLs)
- ✅ **Bug Fixes** - Corrected 30-day access period (now properly uses `1M` format)
- ✅ **Profile Integration** - Automatic display of username, balance, and profile image
- ✅ **Live Status Monitoring** - Real-time verification of TradingView session status

### 🔧 **Technical Improvements**
- **Manual Cookie Extraction**: Bypasses bot detection and reCAPTCHA
- **Database Session Storage**: Persistent cookie management via Replit database
- **Token Auto-generation**: Cryptographically secure admin tokens
- **Enhanced Error Handling**: Comprehensive validation and user feedback
- **Professional UI/UX**: Bootstrap-based responsive admin interface

---

## 🏗️ **System Architecture**

### **Backend Components**
- **Flask API Server** (`src/server.py`) - RESTful endpoints with authentication
- **TradingView Integration** (`src/tradingview.py`) - Session and API management
- **Helper Functions** (`src/helper.py`) - Date calculations and utilities
- **Configuration** (`config.py`) - Centralized URL management

### **Frontend Components**  
- **Admin Panel** (`templates/admin.html`) - Professional web interface
- **Login System** - Secure token-based authentication
- **Testing Interface** - Individual endpoint validation tools

### **Security Layer**
- **Token Authentication**: Auto-generated secure admin tokens
- **Session Validation**: Real-time cookie status verification
- **Header-based Auth**: X-Admin-Token headers (never query parameters)
- **Database Encryption**: Secure session storage

---

## 🚀 **Quick Setup**

### **1. Deploy on Replit**
```bash
# Clone the repository
git clone https://github.com/diazpolanco13/TradingView-API-Management-v2.git

# Or use Replit import from GitHub
```

### **2. Environment Configuration**
Set up these environment variables in Replit Secrets:
```env
username=your_tradingview_username
password=your_tradingview_password
```
> **⚠️ Requirements**: Premium TradingView subscription needed for API access.

### **3. Run the Application**
```bash
python main.py
```

**🔐 Admin Token**: The system auto-generates a secure token displayed in console:
```
🔐 Admin token generado para esta sesión:
   tvapi-abc123def456...
   Usa este token para acceder al panel de administración
```

---

## 🎮 **Admin Panel Usage**

### **Accessing the Panel**
1. **Navigate to**: `https://your-repl-name.replit.app/`
2. **Enter Admin Token**: Use the generated token from console
3. **Dashboard Access**: Full system control and testing

### **Cookie Management**
- **Automatic Validation**: System checks cookie status on load
- **Manual Updates**: Easy cookie refresh when sessions expire
- **Real-time Status**: Live indicator of authentication state

### **Endpoint Testing**
Six individual test buttons for complete API validation:
1. **🔍 Validate User** - Check username existence
2. **👀 Check Access** - Verify current user permissions  
3. **✅ Grant 30 Days** - Add month-long access
4. **🔄 Verify Grant** - Confirm access was granted
5. **❌ Revoke Access** - Remove user permissions
6. **✔️ Verify Revoke** - Confirm access removal

---

## 📡 **API Endpoints**

### **Public Endpoints**

#### **`GET /validate/{username}`**
Validates TradingView username existence.

**Response:**
```json
{
    "valid": true,
    "verified_username": "ExactUsername"
}
```

---

### **Protected Endpoints** 
> **🔐 Authentication Required**: All admin endpoints require `X-Admin-Token` header

#### **`GET /access/{username}?indicator_id={pine_id}`**
Check user's current access status for specific indicator.

**Headers:**
```
X-Admin-Token: tvapi-your-admin-token
```

**Response:**
```json
{
    "has_access": true,
    "indicator_id": "PUB;abc123...",
    "username": "user123",
    "expiration": "2025-10-27T19:28:29.087215+00:00",
    "no_expiration": false,
    "status": "checked"
}
```

#### **`POST /access/{username}`**
Grant access to user for specified duration.

**Headers:**
```
X-Admin-Token: tvapi-your-admin-token
Content-Type: application/json
```

**Payload:**
```json
{
    "indicator_id": "PUB;abc123...",
    "days": 30
}
```

**Duration Formats:**
- **30 days**: `"days": 30` → Automatically converts to `1M` (1 month)
- **Other periods**: Direct day values
- **Lifetime**: Use appropriate endpoint

**Response:**
```json
{
    "success": true,
    "message": "Access granted for 30 days"
}
```

#### **`DELETE /access/{username}?indicator_id={pine_id}`**
Revoke user access from indicator.

**Headers:**
```
X-Admin-Token: tvapi-your-admin-token
```

**Response:**
```json
{
    "success": true,
    "message": "Access revoked successfully"
}
```

---

## 🔒 **Security Features**

### **Authentication System**
- **Auto-generated Tokens**: Cryptographically secure random tokens
- **Session-based**: New token per application restart
- **Header Authentication**: Never exposed in URLs or query parameters

### **Cookie Management**
- **Manual Extraction**: Bypasses TradingView's bot detection
- **Database Storage**: Persistent session management
- **Automatic Validation**: Real-time authentication status
- **Error Recovery**: Clear instructions for session renewal

### **API Security**
- **Protected Endpoints**: All admin operations require authentication
- **Input Validation**: Comprehensive payload verification
- **Error Handling**: No sensitive information exposure

---

## 🔧 **Technical Details**

### **TradingView Integration**
The system uses TradingView's internal API endpoints:
- **Username validation**: `/pine_perm/username_hint/`
- **Access management**: `/pine_perm/modify_access/` and `/pine_perm/add_access/`
- **User verification**: `/u/{username}/` profile pages
- **Account data**: `/accounts/balance/` for user information

### **Date Period Handling**
**Critical Fix**: 30-day access periods now properly use `1M` format:
```python
# ✅ Correct implementation
if days == 30:
    tv.add_access(access, 'M', 1)  # 1 month = ~30 days
else:
    tv.add_access(access, 'd', days)  # Direct day values
```

### **Database Schema**
Using Replit's built-in key-value database:
```python
# Cookie storage
db['cookies'] = serialized_cookie_data

# Admin token (runtime only)
admin_token = generate_secure_token()
```

---

## 🎯 **Use Cases**

### **For Script Vendors**
- **Automated Access Management**: Grant/revoke access programmatically
- **Subscription Handling**: Integrate with payment systems
- **User Validation**: Verify customers before processing
- **Bulk Operations**: Manage multiple users efficiently

### **For Developers**
- **API Integration**: RESTful endpoints for external systems
- **Webhook Support**: Easy integration with payment processors
- **Admin Interface**: Non-technical user management
- **Testing Tools**: Validate functionality before deployment

---

## 🛠️ **Development**

### **Project Structure**
```
├── src/
│   ├── server.py          # Flask API server
│   ├── tradingview.py     # TradingView integration
│   └── helper.py          # Utility functions
├── templates/
│   └── admin.html         # Admin panel interface
├── config.py              # Configuration management
├── main.py                # Application entry point
└── replit.md              # Project documentation
```

### **Dependencies**
- **Flask**: Web framework and API server
- **requests**: HTTP client for TradingView API
- **python-dateutil**: Advanced date calculations
- **Replit Database**: Built-in key-value storage

---

## 🔍 **Troubleshooting**

### **Common Issues**

#### **Cookie Expiration**
**Symptoms**: API returns authentication errors
**Solution**: 
1. Open admin panel
2. Click "Update Cookies" button  
3. Follow manual extraction instructions

#### **Token Authentication**
**Symptoms**: "Unauthorized" responses
**Solution**: 
1. Check console for current admin token
2. Include token in `X-Admin-Token` header
3. Restart application for new token if needed

#### **30-Day Access Issues**
**Fixed**: System now properly uses `1M` (1 month) format instead of `30D`

---

## 📈 **Monitoring**

### **Built-in Diagnostics**
- **Cookie Status**: Real-time session validation
- **API Health**: Endpoint response monitoring
- **User Balance**: Account information display
- **Error Logging**: Comprehensive debugging information

### **Admin Dashboard**
- **Profile Information**: Username, balance, profile image
- **System Status**: Real-time operational indicators
- **Test Results**: Individual endpoint validation
- **Session Management**: Cookie status and refresh options

---

## 🚀 **Publishing**

Deploy your API to production with Replit's built-in deployment:
1. **Test thoroughly** using the admin panel
2. **Configure environment** variables properly
3. **Deploy** via Replit's "Publish" button
4. **Custom domain** available with Replit Pro

---

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create feature branch
3. Test with admin panel
4. Submit pull request

### **Bug Reports**
Use the admin panel's testing interface to validate issues before reporting.

---

## 📞 **Support & Links**

### **Referral Programs**
If you found this project useful, consider using these referral links:
- **[TradingView Premium](https://www.tradingview.com/?aff_id=112733)** 
- **[Bybit Trading](https://partner.bybit.com/b/TRENDOSCOPE)**
- **[BingX Exchange](https://bingx.com/en-us/partner/Trendoscope/)**

### **Original Developer**
<div align="center">
<a href="https://p.trendoscope.au/"><img src="https://s3.tradingview.com/userpics/7387160-gqgs_big.png" width="100" height="100"></a>
<a href="https://p.trendoscope.au/twitter"><img src="https://i.pinimg.com/originals/aa/3d/75/aa3d750ddec109594ac7c89cb8cbabab.jpg" width="100" height="100"></a>
<a href="https://p.trendoscope.au/telegram"><img src="https://i.pinimg.com/originals/70/c3/ea/70c3ea9e43ebd11ec98de96937529408.jpg" width="100" height="100"></a>
<a href="https://p.trendoscope.au/discord"><img src="https://i.pinimg.com/originals/b6/fe/4a/b6fe4a830e0263d8344b63e3dbcf3033.jpg" width="100" height="100"></a>
<a href="https://p.trendoscope.au/youtube"><img src="https://i.pinimg.com/originals/f4/14/b8/f414b816ef11df2c1eaae61f2fc8c489.jpg" width="100" height="100"></a>
</div>

---

## 📄 **License**

This project is provided as-is for educational and commercial use. Please ensure compliance with TradingView's Terms of Service when using their APIs.

---

<div align="center">

**🎯 Ready to automate your TradingView Pine Script access management?**

[🚀 **Deploy Now**](https://replit.com/@trendoscope/Tradingview-Access-Management) • [📚 **Documentation**](https://github.com/diazpolanco13/TradingView-API-Management-v2) • [💬 **Support**](https://p.trendoscope.au/discord)

</div>