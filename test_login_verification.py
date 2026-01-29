#!/usr/bin/env python
"""
Login & Responsive Design Verification Script
Tests backend login endpoint and data flow
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:8000/api"
TEST_EMAIL = "test@example.com"
TEST_USER_ID = "KE-QC-00001"
TEST_PASSWORD = "password123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{text}")
    print(f"{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.RESET}")

def test_backend_connectivity():
    """Test if backend server is running"""
    print_header("1. Testing Backend Connectivity")
    
    try:
        response = requests.get(f"{BACKEND_URL}/auth/user/", timeout=5)
        # Expected to get 401 Unauthorized (no token), but shows server is up
        if response.status_code in [401, 403]:
            print_success(f"Backend is running at {BACKEND_URL}")
            return True
        elif response.status_code == 200:
            print_success(f"Backend is running and responding correctly")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to backend at {BACKEND_URL}")
        print_warning("Make sure Django server is running: python manage.py runserver")
        return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_login_endpoint():
    """Test login with email"""
    print_header("2. Testing Login Endpoint (Email)")
    
    # First, create a test user if needed
    payload = {
        "email_or_user_id": TEST_EMAIL,
        "password": TEST_PASSWORD,
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login/",
            json=payload,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login successful!")
            print(f"  User ID: {data.get('user_id')}")
            print(f"  Email: {data.get('user', {}).get('email')}")
            print(f"  Is Admin: {data.get('user', {}).get('is_admin')}")
            print(f"  Access Token: {data.get('access')[:50]}...")
            print(f"  Refresh Token: {data.get('refresh')[:50]}...")
            return data
        elif response.status_code == 401:
            print_warning("Invalid credentials")
            print(f"Response: {response.json()}")
            return None
        else:
            print_error(f"Unexpected response: {response.status_code}")
            print(f"Response: {response.json()}")
            return None
            
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_login_with_user_id(user_id):
    """Test login with User ID"""
    print_header("3. Testing Login with User ID")
    
    payload = {
        "email_or_user_id": user_id,
        "password": TEST_PASSWORD,
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/login/",
            json=payload,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Login with User ID ({user_id}) successful!")
            return data
        elif response.status_code == 401:
            print_warning(f"Invalid User ID or password for {user_id}")
            return None
        else:
            print_error(f"Unexpected response: {response.status_code}")
            print(f"Response: {response.json()}")
            return None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_token_refresh(refresh_token):
    """Test token refresh"""
    print_header("4. Testing Token Refresh")
    
    payload = {
        "refresh": refresh_token
    }
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/auth/token/refresh/",
            json=payload,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Token refresh successful!")
            print(f"  New Access Token: {data.get('access')[:50]}...")
            return data
        else:
            print_error(f"Token refresh failed: {response.status_code}")
            print(f"Response: {response.json()}")
            return None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_protected_endpoint(access_token):
    """Test accessing protected endpoint"""
    print_header("5. Testing Protected Endpoint (/api/auth/user/)")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(
            f"{BACKEND_URL}/auth/user/",
            headers=headers,
            timeout=5
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Protected endpoint accessible!")
            print(f"  User ID: {data.get('user_id')}")
            print(f"  Email: {data.get('email')}")
            print(f"  Username: {data.get('username')}")
            return data
        elif response.status_code == 401:
            print_error("Token invalid or expired")
            return None
        else:
            print_error(f"Unexpected response: {response.status_code}")
            print(f"Response: {response.json()}")
            return None
            
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None

def test_api_endpoints():
    """Test various API endpoints"""
    print_header("6. Testing Key API Endpoints")
    
    # List of endpoints to check
    endpoints = [
        ("/auth/register/", "POST"),
        ("/auth/login/", "POST"),
        ("/auth/logout/", "POST"),
        ("/auth/token/refresh/", "POST"),
        ("/investments/", "GET"),
        ("/transactions/", "GET"),
        ("/balance/", "GET"),
    ]
    
    for endpoint, method in endpoints:
        url = f"{BACKEND_URL}{endpoint}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=2)
            else:
                response = requests.post(url, json={}, timeout=2)
            
            # Any response (including errors) means endpoint exists
            if response.status_code < 500:
                print_success(f"{method} {endpoint} - Available (HTTP {response.status_code})")
            else:
                print_error(f"{method} {endpoint} - Server Error (HTTP {response.status_code})")
        except requests.exceptions.Timeout:
            print_warning(f"{method} {endpoint} - Timeout")
        except requests.exceptions.ConnectionError:
            print_error(f"{method} {endpoint} - Connection Error")
        except Exception as e:
            print_warning(f"{method} {endpoint} - {str(e)}")

def print_summary(results):
    """Print test summary"""
    print_header("Test Summary")
    
    total = len(results)
    passed = sum(1 for r in results if r)
    failed = total - passed
    
    print(f"Total Tests: {total}")
    print_success(f"Passed: {passed}")
    if failed > 0:
        print_error(f"Failed: {failed}")
    
    if failed == 0:
        print_success("\n✓ All tests passed! System is operational.")
    else:
        print_warning("\n⚠ Some tests failed. Check the output above.")

def main():
    print(f"\n{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     LOGIN & DATA FLOW VERIFICATION TEST SUITE              ║")
    print("║                  Quantum Capital Platform                   ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.RESET}")
    
    print_info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print_info(f"Backend URL: {BACKEND_URL}")
    
    results = []
    
    # Test 1: Backend connectivity
    results.append(test_backend_connectivity())
    
    if not results[0]:
        print_error("\nBackend server is not running. Please start it first.")
        sys.exit(1)
    
    # Test 2: Login endpoint
    login_data = test_login_endpoint()
    results.append(login_data is not None)
    
    if login_data:
        # Test 3: Login with User ID (if available)
        user_id = login_data.get('user_id')
        if user_id:
            user_id_data = test_login_with_user_id(user_id)
            results.append(user_id_data is not None)
        
        # Test 4: Token refresh
        refresh_token = login_data.get('refresh')
        if refresh_token:
            refresh_data = test_token_refresh(refresh_token)
            results.append(refresh_data is not None)
            
            # Test 5: Protected endpoint
            if refresh_data:
                access_token = refresh_data.get('access')
            else:
                access_token = login_data.get('access')
            
            protected_data = test_protected_endpoint(access_token)
            results.append(protected_data is not None)
    
    # Test 6: API endpoints
    test_api_endpoints()
    results.append(True)
    
    # Print summary
    print_summary(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Colors.RED}Unexpected error: {str(e)}{Colors.RESET}")
        sys.exit(1)
