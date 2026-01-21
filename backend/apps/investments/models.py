from django.db import models
from apps.users.models import User


class Investment(models.Model):
    """User investment record"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    entry_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('closed', 'Closed'),
            ('paused', 'Paused'),
        ],
        default='active'
    )
    
    class Meta:
        db_table = 'investments'
    
    def __str__(self):
        return f"{self.user.user_id} - {self.amount} KES"


class Allocation(models.Model):
    """Fund allocation within an investment"""
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='allocations')
    name = models.CharField(max_length=100, default='Active Trading')
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'allocations'
    
    def __str__(self):
        return f"{self.investment.user.user_id} - {self.name} ({self.percentage}%)"
