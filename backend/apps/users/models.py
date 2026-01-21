from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import random
import string

class User(models.Model):
    user_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=5, default='KE')
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.CharField(max_length=255, null=True, blank=True)
    
    ACCOUNT_STATUS_CHOICES = [
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
    ]
    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default='active')
    
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    
    KYC_STATUS_CHOICES = [
        ('unverified', 'Unverified'),
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default='unverified')
    
    referral_code = models.CharField(max_length=20, unique=True)
    referred_by = models.CharField(max_length=20, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
    
    def set_password(self, raw_password):
        self.password_hash = make_password(raw_password)
    
    def check_password(self, raw_password):
        return check_password(raw_password, self.password_hash)
    
    @staticmethod
    def generate_user_id(country_code='KE'):
        """
        Generate user ID based on country code.
        Format: {COUNTRY_CODE}-QC-{NUMBER}
        Example: KE-QC-00001, US-QC-00001
        """
        # Get the last user with the same country code
        last_user = User.objects.filter(country_code=country_code).order_by('-id').first()
        if last_user and last_user.user_id:
            try:
                # Extract the number from user_id (e.g., "KE-QC-00001" -> 1)
                parts = last_user.user_id.split('-')
                if len(parts) >= 3:
                    last_number = int(parts[-1])
                    new_number = last_number + 1
                else:
                    new_number = 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        return f"{country_code}-QC-{str(new_number).zfill(5)}"
    
    @staticmethod
    def generate_referral_code():
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    
    def __str__(self):
        return f"{self.user_id} - {self.email}"

