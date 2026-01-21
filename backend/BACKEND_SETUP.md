# Backend Authentication Setup Complete

## Overview
The backend authentication system has been set up to support:
1. User registration with country-based User ID generation
2. Login with email OR User ID
3. JWT token authentication
4. Country code support (for User ID generation)

## Files Created/Modified

### 1. Models (`apps/users/models.py`)
- Updated `generate_user_id()` method to accept `country_code` parameter
- User IDs are now generated in format: `{COUNTRY_CODE}-QC-{NUMBER}`
- Example: `KE-QC-00001`, `US-QC-00001`, `NG-QC-00001`

### 2. Serializers (`apps/users/serializers.py`)
- `UserRegistrationSerializer`: Handles user registration
- `UserLoginSerializer`: Handles login (accepts email_or_user_id)
- `UserSerializer`: Serializes user data

### 3. Views (`apps/users/views.py`)
- `register_view`: POST `/api/auth/register/`
- `login_view`: POST `/api/auth/login/` (accepts email or user_id)
- `get_current_user_view`: GET `/api/auth/user/`

### 4. Authentication (`apps/users/authentication.py`)
- `CustomJWTAuthentication`: Custom JWT authentication for our User model

### 5. URLs (`apps/users/urls.py`)
- Authentication routes

### 6. Settings (`config/settings.py`)
- JWT configuration
- CORS settings updated

## API Endpoints

### Register User
```
POST /api/auth/register/
Content-Type: application/json

{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone": "+254 700 000 000",
  "country_code": "KE",
  "password": "password123",
  "date_of_birth": "1990-01-01" (optional),
  "referral_code": "ABC12345" (optional)
}

Response:
{
  "user_id": "KE-QC-00001",
  "user": { ... },
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "message": "User registered successfully"
}
```

### Login
```
POST /api/auth/login/
Content-Type: application/json

{
  "email_or_user_id": "john@example.com" OR "KE-QC-00001",
  "password": "password123"
}

Response:
{
  "user_id": "KE-QC-00001",
  "user": { ... },
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token",
  "message": "Login successful"
}
```

### Get Current User
```
GET /api/auth/user/
Authorization: Bearer {access_token}

Response:
{
  "user_id": "KE-QC-00001",
  "email": "john@example.com",
  ...
}
```

### Refresh Token
```
POST /api/auth/token/refresh/
Content-Type: application/json

{
  "refresh": "jwt_refresh_token"
}

Response:
{
  "access": "new_jwt_access_token"
}
```

## Next Steps

1. Run migrations:
```bash
cd backend
python manage.py makemigrations users
python manage.py migrate
```

2. Test the endpoints (you can use Postman or curl)

3. The frontend is already configured to use these endpoints

## Country Codes Supported
- Any 2-letter country code (ISO 3166-1 alpha-2)
- Examples: KE (Kenya), US (United States), NG (Nigeria), etc.
- User IDs are generated per country (e.g., KE-QC-00001, US-QC-00001)

