# Phase 2 Deployment & Testing Guide

## Quick Start: Get Everything Running

### Step 1: Backend Setup (5 minutes)

```bash
cd d:\PROJECTS\emphasis\backend

# Create migrations
python manage.py makemigrations admin_panel kyc bot

# Apply all migrations
python manage.py migrate

# Create superuser (if not already created)
python manage.py createsuperuser

# Initialize configuration (copy entire block)
python manage.py shell << 'EOF'
from apps.admin_panel.models import SystemConfiguration, AdminUser
from apps.kyc.models import KYCWithdrawalLimit
from django.contrib.auth import get_user_model

User = get_user_model()

# 1. Create System Configuration
config, created = SystemConfiguration.objects.get_or_create(
    id=1,
    defaults={
        'maintenance_mode': False,
        'kyc_required': True,
        'kyc_auto_approve_documents': True,
        'enable_bot_trading': True,
        'platform_fee_percentage': 0.02,
        'minimum_investment': 100,
        'maximum_investment': 100000,
        'minimum_withdrawal': 50,
        'maximum_withdrawal': 50000,
        'kyc_auto_verify_threshold': 80,
        'max_login_attempts': 5,
        'mpesa_enabled': False,
        'crypto_enabled': False,
        'email_notifications_enabled': True,
        'sms_notifications_enabled': False,
    }
)
print(f"✓ System configuration: {'created' if created else 'already exists'}")

# 2. Create KYC Withdrawal Limits
limits_config = [
    {'verification_level': 1, 'daily_limit': 1000, 'monthly_limit': 5000, 'per_transaction_limit': 500},
    {'verification_level': 2, 'daily_limit': 10000, 'monthly_limit': 50000, 'per_transaction_limit': 5000},
    {'verification_level': 3, 'daily_limit': 50000, 'monthly_limit': 200000, 'per_transaction_limit': 20000},
]
for limit_data in limits_config:
    obj, created = KYCWithdrawalLimit.objects.get_or_create(**limit_data)
    if created:
        print(f"✓ Created KYC Level {limit_data['verification_level']} limits")

# 3. Create AdminUser for superuser (if doesn't exist)
admin_user = User.objects.filter(is_superuser=True).first()
if admin_user:
    admin_obj, created = AdminUser.objects.get_or_create(
        user=admin_user,
        defaults={
            'role': 'superadmin',
            'can_suspend_users': True,
            'can_approve_withdrawals': True,
            'can_verify_kyc': True,
            'can_manage_admins': True,
            'is_active': True
        }
    )
    print(f"✓ Admin user: {'created' if created else 'already exists'}")

print("\n✅ All Phase 2 systems initialized successfully!")
EOF

# Start development server
python manage.py runserver
```

### Step 2: Frontend Setup (2 minutes)

```bash
cd d:\PROJECTS\emphasis\frontend

# Install dependencies (if not already done)
npm install

# Start dev server
npm run dev
```

### Step 3: Access the Platform

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **API Status**: http://localhost:8000/api/status

## API Testing with cURL

### Get Auth Token

```bash
# Register/Login to get token
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'

# Login to get token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'

# Copy the access token from response
export TOKEN="<your_access_token_here>"
```

### Test Admin Panel Endpoints

```bash
# 1. Get Dashboard Statistics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/dashboard/statistics/

# 2. List All Users
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/users/list_users/

# 3. Get System Configuration
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/config/get_config/

# 4. Get Pending Withdrawals
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/withdrawals/pending_withdrawals/

# 5. Export Users as CSV
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/reports/export_users_csv/ > users.csv
```

### Test KYC System Endpoints

```bash
# 1. Get Current KYC Status
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/kyc/documents/my_kyc/

# 2. Submit KYC
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "date_of_birth": "1990-01-15",
    "nationality": "US",
    "document_type": "passport",
    "country": "US",
    "state_province": "California",
    "city": "San Francisco",
    "postal_code": "94105"
  }' \
  http://localhost:8000/api/kyc/documents/submit_kyc/

# 3. Get KYC Withdrawal Limits
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/kyc/config/withdrawal_limits/

# 4. Get Rejection Templates (as admin)
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/kyc/config/rejection_templates/
```

### Test Bot Trading Endpoints

```bash
# 1. Get Bot Configuration
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/config/my_config/

# 2. Start Bot
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/config/start_bot/

# 3. Update Bot Config
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": "aggressive",
    "daily_trading_limit": "5000.00",
    "max_trades_per_day": 10,
    "take_profit_percentage": "10.00",
    "stop_loss_percentage": "5.00"
  }' \
  http://localhost:8000/api/bot/config/update_config/

# 4. Execute Manual Trade
curl -X POST \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "trade_type": "buy",
    "asset": "USD",
    "entry_price": "100.50",
    "entry_amount": "500.00",
    "quantity": "4.97",
    "notes": "Manual trade based on market analysis"
  }' \
  http://localhost:8000/api/bot/trades/execute_trade/

# 5. Get Daily Performance
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/performance/daily_performance/

# 6. Get Bot Dashboard
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/performance/dashboard/

# 7. Get Recent Trades
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/trades/my_trades/?limit=10
```

## Admin Interface Testing

### Access Django Admin

1. Navigate to: http://localhost:8000/admin/
2. Login with superuser credentials
3. Verify these sections are accessible:
   - **Admin Users**: View/manage admin accounts
   - **Admin Logs**: View all admin actions and changes
   - **Platform Statistics**: View daily snapshots
   - **System Configuration**: Edit platform settings
   - **KYC Documents**: Review KYC submissions
   - **KYC Verification Logs**: View verification history
   - **Bot Configurations**: View bot trading settings
   - **Bot Trades**: View all executed trades
   - **Bot Performance**: View performance snapshots
   - **Bot Execution Logs**: View bot events

## Comprehensive Test Scenarios

### Scenario 1: KYC Verification Flow

```bash
# 1. Create test user
USER_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "kyc_test",
    "email": "kyc@test.com",
    "password": "TestPass123!",
    "password_confirm": "TestPass123!"
  }' | grep -o '"access":"[^"]*' | cut -d'"' -f4)

# 2. Submit KYC
SUBMIT=$(curl -s -X POST \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test User",
    "date_of_birth": "1995-05-20",
    "nationality": "US",
    "document_type": "passport",
    "country": "US",
    "state_province": "NY",
    "city": "New York",
    "postal_code": "10001"
  }' \
  http://localhost:8000/api/kyc/documents/submit_kyc/)

echo "KYC Submitted: $SUBMIT"

# 3. Check KYC status (should be auto-verified if all fields provided)
curl -s -H "Authorization: Bearer $USER_TOKEN" \
  http://localhost:8000/api/kyc/documents/my_kyc/ | jq '.status'

# 4. As admin, view pending KYC
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/kyc/verification/list_pending/ | jq '.'
```

### Scenario 2: Bot Trading Flow

```bash
# 1. Get bot config
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/config/my_config/ | jq '.'

# 2. Start bot
curl -s -X POST \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/config/start_bot/ | jq '.message'

# 3. Execute multiple trades
for i in {1..3}; do
  curl -s -X POST \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
      \"trade_type\": \"buy\",
      \"asset\": \"USD\",
      \"entry_price\": \"$((100 + i))\",
      \"entry_amount\": \"500\",
      \"quantity\": \"$(bc <<< 'scale=2; 500/(100+$i)')\"
    }" \
    http://localhost:8000/api/bot/trades/execute_trade/
  sleep 1
done

# 4. View trades
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/trades/my_trades/ | jq '.[]' | head -20

# 5. Check performance
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/bot/performance/dashboard/ | jq '.'
```

### Scenario 3: Admin Operations

```bash
# 1. Get all users (admin only)
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/admin/users/list_users/ | jq '.[]' | head -30

# 2. Suspend a user
USER_ID=2
curl -s -X POST \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reason": "Suspicious activity detected"}' \
  http://localhost:8000/api/admin/users/$USER_ID/suspend_user/ | jq '.message'

# 3. Get admin logs
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/admin/dashboard/recent_activity/ | jq '.[]' | head -20

# 4. Export reports
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/admin/reports/export_users_csv/ > users_export.csv

echo "✓ Exported users.csv"
```

## Verification Checklist

- [ ] All migrations run successfully
- [ ] System configuration initialized
- [ ] KYC withdrawal limits created
- [ ] Admin user account created
- [ ] Admin dashboard accessible and showing stats
- [ ] KYC endpoints working (submit, verify, configure)
- [ ] Bot endpoints working (config, trades, performance)
- [ ] Admin panel showing all new models
- [ ] Django admin interface fully functional
- [ ] CSV export working for reports
- [ ] Error handling working properly
- [ ] Audit logs recording all actions

## Performance Testing

```bash
# Test concurrent requests
ab -n 100 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/admin/dashboard/statistics/

# Test large dataset export
time curl -s -H "Authorization: Bearer $ADMIN_TOKEN" \
  http://localhost:8000/api/admin/reports/export_transactions_csv/ > /dev/null

echo "✓ Performance test complete"
```

## Debugging Commands

```bash
# Check database tables
python manage.py dbshell << 'EOF'
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name LIKE '%admin%';
EOF

# Check migrations status
python manage.py showmigrations admin_panel kyc bot

# Check model integrity
python manage.py check

# View all endpoints
python manage.py show_urls
```

## Production Deployment Checklist

Before deploying to production:

- [ ] Set `DEBUG = False` in settings.py
- [ ] Update `ALLOWED_HOSTS` with production domain
- [ ] Configure `SECURE_SSL_REDIRECT = True`
- [ ] Set up database backups
- [ ] Configure environment variables for integrations
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Enable rate limiting on API endpoints
- [ ] Configure CSRF token handling
- [ ] Set up logging and monitoring (Sentry)
- [ ] Configure static file serving
- [ ] Test all endpoints in staging environment
- [ ] Create database backup before migration

## Rollback Procedure

If issues occur:

```bash
# Revert migrations (if needed)
python manage.py migrate admin_panel 0001_initial --fake-initial

# Or remove apps entirely
python manage.py migrate admin_panel zero
python manage.py migrate kyc zero
python manage.py migrate bot zero
```

## Support

For issues or questions:
1. Check logs: `tail -f logs/debug.log`
2. Review Django admin for data integrity
3. Check database constraints: `python manage.py dbshell`
4. Verify settings: `python manage.py shell` and print settings
5. Review documentation in PHASE2_*.md files

---

**Setup Time**: ~15 minutes total
**Next Step**: Begin frontend implementation for Admin, KYC, Analytics, and Bot pages
