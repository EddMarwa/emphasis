# Admin Dashboard - Quick Start Guide

## What's Included

This implementation provides a complete admin dashboard for Quantum Capital with:
- User management and account control
- Payment processing (M-Pesa & Crypto)
- Financial reporting and analytics
- Complete audit trail for compliance

---

## Backend Setup (5 minutes)

### 1. Create Admin Users

```python
# In Django shell: python manage.py shell
from django.contrib.auth.models import User
from apps.admin_panel.models import AdminUser

# Create Django user
user = User.objects.create_user(username='admin', email='admin@quantumcapital.com', password='securepass123')

# Create admin profile
admin = AdminUser.objects.create(user=user, role='superadmin')
print(f"Admin created: {admin}")
```

### 2. Configure Settings

Add to `backend/config/settings.py`:

```python
# M-Pesa Configuration
MPESA_CONSUMER_KEY = "your_daraja_consumer_key"
MPESA_CONSUMER_SECRET = "your_daraja_consumer_secret"
MPESA_SHORTCODE = "174379"  # Test: 174379, Live: your_code
MPESA_PASSKEY = "your_passkey"
MPESA_CALLBACK_URL = "https://yourdomain.com/api/payments/mpesa/callback/"
MPESA_B2C_INITIATOR = "testapi"
MPESA_B2C_SECURITY_CREDENTIAL = "your_encrypted_credentials"

# Crypto Configuration
CRYPTO_API_KEY = "your_coingecko_api_key"
CRYPTO_API_SECRET = "your_crypto_secret"
```

### 3. Run Migrations

```bash
cd backend
python manage.py migrate admin_panel
python manage.py migrate reports
```

### 4. Register URLs

In `backend/config/urls.py`:

```python
urlpatterns = [
    # ... existing urls ...
    path('api/admin/', include('apps.admin_panel.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/reports/', include('apps.reports.urls')),
]
```

### 5. Start Backend Server

```bash
python manage.py runserver
# Access API at: http://localhost:8000/api/admin/
```

---

## Frontend Setup (5 minutes)

### 1. Add Component to App

In `frontend/src/App.jsx`:

```jsx
import AdminDashboard from './pages/AdminDashboard'

function App() {
  return (
    <Routes>
      // ... existing routes ...
      <Route path="/admin" element={<AdminDashboard />} />
    </Routes>
  )
}
```

### 2. Create Route Link

Add to your navigation:

```jsx
<Link to="/admin">Admin Dashboard</Link>
```

### 3. Ensure API URL is Correct

In `frontend/src/services/api.js`:

```javascript
export const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
})
```

### 4. Start Frontend Server

```bash
cd frontend
npm start
# Access at: http://localhost:3000/admin
```

---

## Testing the Integration

### 1. Get Admin Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"securepass123"}'
```

### 2. Test Admin Dashboard

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/admin/dashboard/statistics/
```

### 3. Test M-Pesa Payment

```bash
curl -X POST http://localhost:8000/api/payments/mpesa/stk-push/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount":1000,"phone":"254712345678"}'
```

### 4. Test Reporting

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/reports/daily-summary/"
```

---

## Key Admin Features

### User Management
- ✅ View all users with balances
- ✅ Suspend/reactivate accounts
- ✅ View transaction history
- ✅ Export user list as CSV

### Withdrawals
- ✅ View pending requests
- ✅ Approve with processing
- ✅ Reject with reason
- ✅ Automatic refunds

### Payments
- ✅ M-Pesa STK push
- ✅ Transaction verification
- ✅ Exchange rates (live)
- ✅ Crypto deposit generation

### Reports
- ✅ Daily summaries
- ✅ Monthly reports
- ✅ User profit statements
- ✅ Fee breakdowns
- ✅ CSV exports

---

## Common Tasks

### Suspend a User

```bash
curl -X POST http://localhost:8000/api/admin/users/suspend_user/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"KE-QC-00001","reason":"Suspicious activity"}'
```

### Check Payment Status

```bash
curl http://localhost:8000/api/payments/status/?transaction_id=123 \
  -H "Authorization: Bearer TOKEN"
```

### Generate Monthly Report

```bash
curl "http://localhost:8000/api/reports/monthly-summary/?month=2024-01" \
  -H "Authorization: Bearer TOKEN"
```

### Get User Profit Statement

```bash
curl "http://localhost:8000/api/reports/user-profit-statement/?user_id=KE-QC-00001&start_date=2024-01-01&end_date=2024-01-31" \
  -H "Authorization: Bearer TOKEN"
```

---

## Troubleshooting

### Admin Dashboard Blank
- Check authentication token
- Verify user has admin profile
- Check browser console for errors
- Verify API URL in settings

### M-Pesa Errors
- Check consumer key/secret
- Verify shortcode
- Check callback URL is accessible
- Review M-Pesa logs

### Reports Not Loading
- Verify transaction records exist
- Check date format (YYYY-MM-DD)
- Ensure user exists
- Check balance records

### Permission Denied
- Verify admin role is set
- Check permissions in AdminUser model
- Ensure is_active=True

---

## Admin Roles & Permissions

### SuperAdmin (Full Access)
- All user management
- Transaction adjustments
- System configuration
- Admin management

### Admin
- User management (suspend/activate)
- Transaction adjustments
- Withdrawal approvals
- Report generation

### Moderator
- KYC verification
- User support
- View reports
- No modifications

### Analyst
- View reports only
- No modifications
- Export functionality

---

## Environment Variables

### Backend (.env)
```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com

MPESA_CONSUMER_KEY=xxx
MPESA_CONSUMER_SECRET=xxx
MPESA_SHORTCODE=174379
MPESA_PASSKEY=xxx

CRYPTO_API_KEY=xxx
```

### Frontend (.env)
```
REACT_APP_API_URL=https://api.yourdomain.com
```

---

## Production Checklist

- [ ] M-Pesa production credentials configured
- [ ] HTTPS enabled
- [ ] Admin users created and tested
- [ ] Email notifications configured
- [ ] Database backups enabled
- [ ] Monitoring/logging configured
- [ ] Rate limiting enabled
- [ ] CORS settings updated
- [ ] API documentation reviewed
- [ ] Security audit completed

---

## Support Resources

- **API Documentation**: See `ADMIN_DASHBOARD_SETUP.md`
- **Completion Report**: See `ADMIN_DASHBOARD_COMPLETION_REPORT.md`
- **Feature List**: See `feature list.txt`

---

## Next Steps

1. **Set up admin users** - Create superadmin account
2. **Test integration** - Run test requests
3. **Configure payments** - Set up M-Pesa and crypto
4. **Train staff** - Admin team walkthroughs
5. **Go live** - Deploy to production

---

## Quick Reference

| Feature | Endpoint | Status |
|---------|----------|--------|
| Dashboard Stats | `GET /api/admin/dashboard/statistics/` | ✅ |
| User List | `GET /api/admin/users/list_users/` | ✅ |
| Suspend User | `POST /api/admin/users/suspend_user/` | ✅ |
| M-Pesa Payment | `POST /api/payments/mpesa/stk-push/` | ✅ |
| Crypto Rate | `GET /api/payments/crypto/exchange-rate/` | ✅ |
| Daily Report | `GET /api/reports/daily-summary/` | ✅ |
| User Statement | `GET /api/reports/user-profit-statement/` | ✅ |
| Fee Breakdown | `GET /api/reports/fee-breakdown/` | ✅ |

---

**Everything is ready to deploy! 🚀**

For detailed information, see the comprehensive guides in the project root directory.
