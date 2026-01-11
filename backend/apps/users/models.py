from django.db import models\nfrom django.contrib.auth.hashers import make_password, check_password\nimport random\nimport string\n\nclass User(models.Model):\n    user_id = models.CharField(max_length=20, unique=True)\n    email = models.EmailField(unique=True)\n    phone = models.CharField(max_length=20, unique=True)\n    password_hash = models.CharField(max_length=255)\n    first_name = models.CharField(max_length=100)\n    last_name = models.CharField(max_length=100)\n    country_code = models.CharField(max_length=5, default=\'KE\')\n    date_of_birth = models.DateField(null=True, blank=True)\n    profile_picture = models.CharField(max_length=255, null=True, blank=True)\n    \n    ACCOUNT_STATUS_CHOICES = [\n        (\'active\', \'Active\'),\n        (\'suspended\', \'Suspended\'),\n        (\'pending\', \'Pending\'),\n        (\'closed\', \'Closed\'),\n    ]\n    account_status = models.CharField(max_length=20, choices=ACCOUNT_STATUS_CHOICES, default=\'active\')\n    \n    email_verified = models.BooleanField(default=False)\n    phone_verified = models.BooleanField(default=False)\n    \n    KYC_STATUS_CHOICES = [\n        (\'unverified\', \'Unverified\'),\n        (\'pending\', \'Pending\'),\        (\'verified\', \'Verified\'),\
        (\'rejected\', \'Rejected\'),\
    ]\
    kyc_status = models.CharField(max_length=20, choices=KYC_STATUS_CHOICES, default=\'unverified\')\
    \
    referral_code = models.CharField(max_length=20, unique=True)\
    referred_by = models.CharField(max_length=20, null=True, blank=True)\
    \
    created_at = models.DateTimeField(auto_now_add=True)\
    updated_at = models.DateTimeField(auto_now=True)\
    last_login = models.DateTimeField(null=True, blank=True)\
    \
    class Meta:\
        db_table = \'users\'\
    \
    def set_password(self, raw_password):\
        self.password_hash = make_password(raw_password)\
    \
    def check_password(self, raw_password):\
        return check_password(raw_password, self.password_hash)\
    \
    @staticmethod\
    def generate_user_id():\
        last_user = User.objects.order_by(\'-id\').first()\
        if last_user and last_user.user_id:\
            last_number = int(last_user.user_id.split(\'-\')[-1])\
            new_number = last_number + 1\
        else:\
            new_number = 1\
        return f\"KE-QC-{str(new_number).zfill(5)}\"\
    \
    @staticmethod\
    def generate_referral_code():\
        return \'\'.join(random.choices(string.ascii_uppercase + string.digits, k=8))\
    \
    def __str__(self):\
        return f\"{self.user_id} - {self.email}\"\

