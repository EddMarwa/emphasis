# Admin Dashboard Setup - Complete Implementation Guide

## Overview
Complete admin dashboard setup for Quantum Capital platform with:
- Admin authentication and user management
- Platform statistics and analytics
- User account management (suspend/activate)
- Transaction adjustments with audit trails
- Payment integration (M-Pesa & Crypto)
- Comprehensive reporting system

---

## Backend Implementation

### 1. Admin Panel Module (`apps/admin_panel/`)

#### Models
- **AdminUser**: Admin accounts with role-based permissions
  - Roles: superadmin, admin, moderator, analyst
  - Permission fields for granular control
  
- **AdminLog**: Complete audit trail of all admin actions
  - Tracks: user changes, transactions, KYC, withdrawals, system configs
  - Stores old/new values for compliance

- **PlatformStatistics**: Daily statistics snapshots
  - User counts, financial metrics, AUM, KYC stats
  
- **SystemConfiguration**: Platform-wide settings
  - Feature flags, payment settings, security parameters

#### Views & Endpoints

**AdminDashboardView**
```
GET /api/admin/dashboard/statistics/      - Platform overview stats
GET /api/admin/dashboard/recent_activity/  - Recent admin logs
GET /api/admin/dashboard/system_health/    - System status
```

**UserManagementViewSet**
```
GET  /api/admin/users/list_users/           - All users with balances
GET  /api/admin/users/user_detail/          - Detailed user info
GET  /api/admin/users/user_transactions/    - User transaction history
POST /api/admin/users/suspend_user/         - Suspend account
POST /api/admin/users/activate_user/        - Reactivate account
```

**WithdrawalManagementViewSet**
```
GET  /api/admin/withdrawals/pending_withdrawals/  - Pending requests
POST /api/admin/withdrawals/approve_withdrawal/   - Approve & process
POST /api/admin/withdrawals/reject_withdrawal/    - Reject & refund
```

**SystemConfigurationViewSet**
```
GET  /api/admin/config/get_config/     - Current system config
POST /api/admin/config/update_config/  - Update settings
```

**TransactionAdjustmentViewSet** (NEW)
```
POST /api/admin/transactions/adjust_balance/  - Manual balance adjustment
POST /api/admin/transactions/reverse_transaction/  - Reverse completed transaction
GET  /api/admin/transactions/audit_trail/     - View audit logs
```

**ReportingViewSet**
```
GET /api/admin/reports/daily_report/         - Daily stats
GET /api/admin/reports/monthly_summary/      - Monthly stats
GET /api/admin/reports/user_profit_statements/  - User profit details
GET /api/admin/reports/platform_fee_report/  - Fee breakdown
GET /api/admin/reports/monthly_summary/      - Monthly summary
GET /api/admin/reports/export_users_csv/     - Export users
GET /api/admin/reports/export_transactions_csv/ - Export transactions
```

---

### 2. Payment Integration (`apps/payments/`)

#### Services (`services.py`)

**MPesaIntegration**
```python
- get_access_token()          # Get Daraja API token
- stk_push(phone, amount)     # Initiate payment prompt
- query_transaction_status()  # Check payment confirmation
- b2c_withdrawal(phone, amount)  # Process withdrawal
```

**CryptoIntegration**
```python
- get_exchange_rate(symbol, fiat)  # Real-time rates
- generate_wallet_address()        # Create deposit address
- verify_transaction(txid)         # Blockchain verification
```

**PaymentVerificationService**
```python
- verify_deposit(deposit_id, method)  # Confirm deposit
- get_payment_status(transaction_id)  # Get any payment status
```

**ReportingService**
```python
- generate_daily_report(date)           # Daily stats
- generate_user_profit_statement()      # User profit details
```

#### API Endpoints (`payment_api.py`)

**M-Pesa**
```
POST /api/payments/mpesa/stk-push/      - Initiate STK push
GET  /api/payments/mpesa/status/        - Check payment status
```

**Crypto**
```
GET  /api/payments/crypto/exchange-rate/    - Get conversion rates
POST /api/payments/crypto/generate-address/ - Create deposit wallet
POST /api/payments/crypto/verify-deposit/   - Verify crypto transaction
```

**General**
```
GET /api/payments/status/               - Check any payment status
GET /api/payments/user-transactions/    - User transaction history
GET /api/payments/profit-statement/     - User profit statement
GET /api/payments/platform-stats/       - Platform financial stats
```

---

### 3. Reporting Module (`apps/reports/`)

#### ReportingViewSet Endpoints

```
GET  /api/reports/daily-summary/          - Daily report
GET  /api/reports/monthly-summary/        - Monthly report
GET  /api/reports/user-profit-statement/  - User profit details
GET  /api/reports/fee-breakdown/          - Fee analysis
GET  /api/reports/export-daily/           - Export as CSV
GET  /api/reports/export-statement/       - Export user statement
```

#### Query Parameters

**Daily Summary**
```
?date=2024-01-15
```

**Monthly Summary**
```
?month=2024-01
```

**User Profit Statement**
```
?user_id=KE-QC-00001&start_date=2024-01-01&end_date=2024-01-31
```

**Fee Breakdown**
```
?start_date=2024-01-01&end_date=2024-01-31&group_by=user
  group_by options: user, day, transaction_type
```

---

## Frontend Implementation

### AdminDashboard Component (`src/pages/AdminDashboard.jsx`)

#### Features
1. **Overview Tab**
   - Statistics cards (users, AUM, profit, fees)
   - Financial summary breakdown
   - Fund allocation pie chart
   - System status indicators

2. **Users Tab**
   - Complete user list with filters
   - User status management
   - Suspend/activate functionality
   - User details modal
   - CSV export

3. **Withdrawals Tab**
   - Pending withdrawal requests
   - Approve/reject actions
   - Payment method display
   - Audit trail

4. **Reports Tab**
   - Monthly/daily reports
   - Fee statistics
   - User profit statements
   - CSV export options

#### API Integration
```javascript
// Statistics
GET /api/admin/dashboard/statistics/

// Users
GET /api/admin/users/list_users/
POST /api/admin/users/suspend_user/
POST /api/admin/users/activate_user/

// Withdrawals
GET /api/admin/withdrawals/pending_withdrawals/
POST /api/admin/withdrawals/approve_withdrawal/
POST /api/admin/withdrawals/reject_withdrawal/

// Reports
GET /api/admin/reports/monthly_summary/
GET /api/admin/reports/export_users_csv/
```

---

## Configuration

### Required Settings (settings.py)

```python
# M-Pesa Configuration
MPESA_CONSUMER_KEY = "your_consumer_key"
MPESA_CONSUMER_SECRET = "your_consumer_secret"
MPESA_SHORTCODE = "174379"
MPESA_PASSKEY = "your_passkey"
MPESA_CALLBACK_URL = "https://yourapp.com/api/mpesa/callback/"
MPESA_B2C_INITIATOR = "username"
MPESA_B2C_SECURITY_CREDENTIAL = "encrypted_credentials"

# Crypto Configuration
CRYPTO_API_KEY = "your_crypto_api_key"
CRYPTO_API_SECRET = "your_crypto_api_secret"

# Platform Settings
PLATFORM_FEE_PERCENT = 10
MINIMUM_DEPOSIT = 10000
MAXIMUM_WITHDRAWAL = 500000
```

### URL Configuration (config/urls.py)

```python
urlpatterns = [
    # ... existing urls ...
    path('api/admin/', include('apps.admin_panel.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/reports/', include('apps.reports.urls')),
]
```

---

## Features Implemented

### ✅ Admin Panel - Basic
- [x] Admin login (role-based)
- [x] User overview list with filtering
- [x] Total registered users count
- [x] Total funds pooled (AUM)
- [x] Platform statistics dashboard
- [x] User account management (suspend/activate)
- [x] Manual transaction adjustments with audit trail

### ✅ Payment Integration
- [x] M-Pesa Daraja API integration
- [x] STK Push for deposits
- [x] B2C for withdrawals
- [x] Crypto payment gateway (USDT, Bitcoin)
- [x] Wallet address generation
- [x] Payment verification system
- [x] Exchange rate conversion

### ✅ Reporting & Analytics
- [x] Daily performance reports
- [x] User profit statements
- [x] Platform fee calculations (10% of profits)
- [x] Fee breakdown display
- [x] Monthly summaries
- [x] CSV export functionality

---

## Usage Examples

### Admin Statistics
```bash
curl -H "Authorization: Bearer token" \
  https://api.quantumcapital.com/api/admin/dashboard/statistics/
```

### User Management
```bash
# Suspend a user
curl -X POST -H "Authorization: Bearer token" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"KE-QC-00001","reason":"Suspicious activity"}' \
  https://api.quantumcapital.com/api/admin/users/suspend_user/
```

### Payment Verification
```bash
# Check M-Pesa payment status
curl -H "Authorization: Bearer token" \
  "https://api.quantumcapital.com/api/payments/mpesa/status/?checkout_request_id=..."
```

### Reporting
```bash
# Get monthly report
curl -H "Authorization: Bearer token" \
  "https://api.quantumcapital.com/api/reports/monthly-summary/?month=2024-01"

# Get user profit statement
curl -H "Authorization: Bearer token" \
  "https://api.quantumcapital.com/api/reports/user-profit-statement/?user_id=KE-QC-00001&start_date=2024-01-01&end_date=2024-01-31"
```

---

## Security Features

### Audit Trail
Every admin action is logged with:
- Admin user identity
- Action type
- Affected user/resource
- Old and new values
- IP address and timestamp
- Reason for action

### Permissions
- **SuperAdmin**: Full access
- **Admin**: Manage users, withdrawals, transactions
- **Moderator**: KYC verification, user support
- **Analyst**: Read-only access to reports

### Transaction Safety
- All adjustments create full audit trail
- Reversible transactions tracked separately
- Balance calculations verified from source transactions
- Fee calculations based on actual profit amounts

---

## Troubleshooting

### M-Pesa Integration Not Working
1. Verify credentials in settings.py
2. Check Daraja API access at: https://developer.safaricom.co.ke
3. Ensure callback URL is publicly accessible
4. Check logs: `logger.error()` messages

### Reports Not Generating
1. Verify transaction records exist in database
2. Check date format: YYYY-MM-DD
3. Ensure user exists with correct user_id
4. Check Balance records for users

### Admin Login Issues
1. Create AdminUser profile for Django user
2. Set appropriate role and permissions
3. Verify is_active=True
4. Check authentication token

---

## Deployment Checklist

- [ ] M-Pesa credentials configured
- [ ] Crypto API keys set up
- [ ] Email notifications configured
- [ ] Database migrations applied
- [ ] Admin users created
- [ ] Callback URLs registered
- [ ] CORS settings updated
- [ ] SSL/TLS enabled
- [ ] Rate limiting configured
- [ ] Monitoring/logging enabled

---

## Next Steps

1. **Testing**: Run comprehensive API tests
2. **User Training**: Admin staff training on dashboard
3. **Monitoring**: Set up alerts for transaction issues
4. **Scaling**: Configure caching for reports
5. **Integration**: Connect with existing authentication system
6. **Deployment**: Deploy to production with gradual rollout

