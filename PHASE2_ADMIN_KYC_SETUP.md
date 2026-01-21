# Phase 2 Implementation Guide - Admin Panel & KYC System Setup

## Overview
Phase 2 introduces Admin Panel (dashboard, user management, withdrawal approval) and KYC verification system (document submission, auto-verification, level-based withdrawal limits).

## Database Setup

### Step 1: Run Migrations
```bash
cd backend
python manage.py makemigrations admin_panel kyc
python manage.py migrate admin_panel kyc
```

### Step 2: Create Django Admin Superuser
```bash
python manage.py createsuperuser
```

### Step 3: Initialize System Configuration
```bash
python manage.py shell
```

Then run:
```python
from apps.admin_panel.models import SystemConfiguration, AdminUser
from apps.kyc.models import KYCWithdrawalLimit
from django.contrib.auth import get_user_model
from django.utils import timezone

# Initialize System Configuration
config, created = SystemConfiguration.objects.get_or_create(
    id=1,
    defaults={
        'maintenance_mode': False,
        'kyc_required': True,
        'kyc_auto_approve_documents': True,
        'platform_fee_percentage': 0.02,
        'minimum_investment': 100,
        'maximum_investment': 100000,
        'minimum_withdrawal': 50,
        'maximum_withdrawal': 50000,
        'kyc_auto_verify_threshold': 80,
        'max_login_attempts': 5
    }
)

# Create KYC Withdrawal Limits for each level
limits_config = [
    {'verification_level': 1, 'daily_limit': 1000, 'monthly_limit': 5000, 'per_transaction_limit': 500},
    {'verification_level': 2, 'daily_limit': 10000, 'monthly_limit': 50000, 'per_transaction_limit': 5000},
    {'verification_level': 3, 'daily_limit': 50000, 'monthly_limit': 200000, 'per_transaction_limit': 20000},
]

for config_data in limits_config:
    KYCWithdrawalLimit.objects.get_or_create(**config_data)

# Create Admin User
User = get_user_model()
admin_user = User.objects.filter(is_superuser=True).first()
if admin_user:
    AdminUser.objects.get_or_create(
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

print("System initialized successfully!")
exit()
```

## API Endpoints

### Admin Panel APIs (`/api/admin/`)

#### 1. Dashboard Statistics
- **Endpoint**: `GET /api/admin/dashboard/statistics/`
- **Description**: Get platform-wide statistics
- **Response**: User count, AUM, pending withdrawals, pending KYC, active investments

#### 2. Recent Admin Activity
- **Endpoint**: `GET /api/admin/dashboard/recent_activity/`
- **Description**: Get recent admin actions
- **Response**: List of admin logs with action details

#### 3. System Health
- **Endpoint**: `GET /api/admin/dashboard/system_health/`
- **Description**: Check system status
- **Response**: Feature flags, integration status, system health

#### 4. User Management
- **Endpoint**: `GET /api/admin/users/list_users/`
- **Description**: List all users with details
- **Response**: User list with balance, profit, investment count

- **Endpoint**: `GET /api/admin/users/{id}/user_detail/`
- **Description**: Get detailed user info
- **Response**: User profile with transactions

- **Endpoint**: `POST /api/admin/users/{id}/suspend_user/`
- **Description**: Suspend a user
- **Body**: `{"reason": "string"}`

- **Endpoint**: `POST /api/admin/users/{id}/activate_user/`
- **Description**: Activate a suspended user

- **Endpoint**: `GET /api/admin/users/{id}/user_transactions/`
- **Description**: Get all user transactions

#### 5. Withdrawal Management
- **Endpoint**: `GET /api/admin/withdrawals/pending_withdrawals/`
- **Description**: List pending withdrawal requests
- **Response**: Pending withdrawals queue

- **Endpoint**: `POST /api/admin/withdrawals/{id}/approve_withdrawal/`
- **Description**: Approve a withdrawal
- **Body**: `{"approval_notes": "string"}`

- **Endpoint**: `POST /api/admin/withdrawals/{id}/reject_withdrawal/`
- **Description**: Reject a withdrawal (auto-restores balance)
- **Body**: `{"rejection_reason": "string"}`

#### 6. System Configuration
- **Endpoint**: `GET /api/admin/config/get_config/`
- **Description**: Get system configuration

- **Endpoint**: `PUT /api/admin/config/update_config/`
- **Description**: Update system configuration
- **Body**: Configuration fields

#### 7. Reporting & Exports
- **Endpoint**: `GET /api/admin/reports/daily_report/`
- **Description**: Get daily platform report

- **Endpoint**: `GET /api/admin/reports/export_users_csv/`
- **Description**: Export users as CSV

- **Endpoint**: `GET /api/admin/reports/export_transactions_csv/`
- **Description**: Export transactions as CSV

### KYC APIs (`/api/kyc/`)

#### 1. My KYC Status
- **Endpoint**: `GET /api/kyc/documents/my_kyc/`
- **Description**: Get current user's KYC status
- **Response**: Current KYC document status and verification level

#### 2. Submit KYC
- **Endpoint**: `POST /api/kyc/documents/submit_kyc/`
- **Description**: Submit or resubmit KYC documents
- **Body**:
```json
{
    "full_name": "string",
    "date_of_birth": "YYYY-MM-DD",
    "nationality": "string",
    "document_type": "national_id|passport|drivers_license",
    "country": "string",
    "state_province": "string",
    "city": "string",
    "postal_code": "string"
}
```
- **Note**: Upload files separately, auto-verification triggers on submit

#### 3. KYC Verification (Admin)
- **Endpoint**: `GET /api/kyc/verification/list_pending/`
- **Description**: List pending KYC approvals (admin only)

- **Endpoint**: `POST /api/kyc/verification/{id}/approve_kyc/`
- **Description**: Approve KYC document
- **Body**: `{"verification_level": 1|2|3}`

- **Endpoint**: `POST /api/kyc/verification/{id}/reject_kyc/`
- **Description**: Reject KYC with template reason
- **Body**: `{"rejection_reason": "blurry_document|information_mismatch|expired_document|suspicious_activity|other"}`

#### 4. KYC Configuration
- **Endpoint**: `GET /api/kyc/config/rejection_templates/`
- **Description**: Get rejection reason templates

- **Endpoint**: `GET /api/kyc/config/withdrawal_limits/`
- **Description**: Get all withdrawal limits by KYC level

- **Endpoint**: `GET /api/kyc/config/user_limits/`
- **Description**: Get current user's withdrawal limits based on KYC level

## KYC Verification Algorithm

The system auto-verifies KYC documents using a scoring algorithm:

- Personal Information Complete (30 points): full_name, date_of_birth, nationality
- Document Front Upload (30 points): document_front_url provided
- Address Proof (20 points): address_proof_url provided
- Selfie (20 points): selfie_url provided

**Total Score**: 0-100
**Auto-Approval Threshold**: >= 80 (configurable in SystemConfiguration)
**Manual Verification**: If score < 80, requires admin approval

When approved, verification_level is assigned:
- **Level 1**: Daily limit $1,000 | Monthly limit $5,000
- **Level 2**: Daily limit $10,000 | Monthly limit $50,000
- **Level 3**: Daily limit $50,000 | Monthly limit $200,000

## Admin Roles & Permissions

| Role | Can Suspend Users | Can Approve Withdrawals | Can Verify KYC | Can Manage Admins |
|------|------------------|------------------------|----------------|-------------------|
| superadmin | ✓ | ✓ | ✓ | ✓ |
| admin | ✓ | ✓ | ✓ | ✗ |
| moderator | ✓ | ✗ | ✓ | ✗ |
| analyst | ✗ | ✗ | ✗ | ✗ |

## Django Admin Interface

Access at `/admin/` to:

1. **Admin Users**: Manage admin accounts and roles
2. **Admin Logs**: Audit trail of all admin actions (action type, IP address, timestamp, resource changes)
3. **Platform Statistics**: View daily snapshots (users, funds, investments, profit)
4. **System Configuration**: Update platform-wide settings
5. **KYC Documents**: Review KYC submissions with verification status
6. **KYC Verification Logs**: Audit trail of KYC approvals/rejections
7. **Withdrawal Limits**: Configure limits per KYC verification level

## Testing the Setup

### Test Admin Dashboard Access
```bash
curl -H "Authorization: Bearer <admin_token>" http://localhost:8000/api/admin/dashboard/statistics/
```

### Test KYC Submission
```bash
curl -X POST \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Doe",
    "date_of_birth": "1990-01-01",
    "nationality": "US",
    "document_type": "passport",
    "country": "US",
    "state_province": "CA",
    "city": "San Francisco",
    "postal_code": "94105"
  }' \
  http://localhost:8000/api/kyc/documents/submit_kyc/
```

### Test Admin Approval
```bash
curl -X POST \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"verification_level": 2}' \
  http://localhost:8000/api/kyc/verification/1/approve_kyc/
```

## Next Steps: Phase 2 Features

After Admin & KYC setup:
1. **Bot Trading Backend**: Models, trade execution, profit calculation
2. **Advanced Analytics**: Performance reports, ROI calculation
3. **Payment Integration**: M-Pesa, Crypto, Email/SMS (requires external keys)
4. **Frontend Implementation**: Admin dashboard, KYC submission form, Analytics pages
5. **Mobile App**: React Native implementation (optional enhancement)

## Troubleshooting

### Migration Errors
```bash
python manage.py migrate --fake admin_panel 0001_initial
python manage.py migrate admin_panel
```

### Permission Issues
Ensure AdminUser exists for superuser:
```bash
python manage.py shell
from apps.admin_panel.models import AdminUser
from django.contrib.auth import get_user_model
User = get_user_model()
admin = User.objects.filter(is_superuser=True).first()
AdminUser.objects.get_or_create(user=admin, defaults={'role': 'superadmin', 'is_active': True, 'can_suspend_users': True, 'can_approve_withdrawals': True, 'can_verify_kyc': True, 'can_manage_admins': True})
```

### KYC Auto-Verification Not Triggering
Check SystemConfiguration.kyc_auto_approve_documents is True:
```bash
python manage.py shell
from apps.admin_panel.models import SystemConfiguration
config = SystemConfiguration.objects.get(id=1)
print(f"Auto-verify enabled: {config.kyc_auto_approve_documents}")
print(f"Auto-verify threshold: {config.kyc_auto_verify_threshold}")
```

## Database Schema Changes

**New Tables Created:**
- admin_panel_adminuser
- admin_panel_adminlog
- admin_panel_platformstatistics
- admin_panel_systemconfiguration
- kyc_kycdocument
- kyc_kycverificationlog
- kyc_kycrejectiontemplate
- kyc_kycwithdrawallimit

**Relationships:**
- AdminUser → User (ForeignKey, OneToOne via user field)
- AdminLog → AdminUser (ForeignKey)
- KYCDocument → User (ForeignKey)
- KYCVerificationLog → KYCDocument (ForeignKey)
- KYCWithdrawalLimit → Standalone (No FK)

All models include audit timestamps (created_at, updated_at) except singletons.
