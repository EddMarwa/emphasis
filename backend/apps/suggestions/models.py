from django.db import models
from apps.users.models import User


class Suggestion(models.Model):
    """User feedback and suggestions"""
    CATEGORY_CHOICES = [
        ('bug', 'Bug Report'),
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending_review', 'Pending Review'),
        ('under_consideration', 'Under Consideration'),
        ('accepted', 'Accepted/Planned'),
        ('implemented', 'Implemented'),
        ('rejected', 'Rejected'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='suggestions')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    attachment = models.CharField(max_length=500, null=True, blank=True)  # File path or URL
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='pending_review')
    admin_response = models.TextField(null=True, blank=True)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_suggestions')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'suggestions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['category', '-created_at']),
            models.Index(fields=['-upvotes']),
        ]
    
    def __str__(self):
        author = "Anonymous" if self.is_anonymous else (self.user.user_id if self.user else "Unknown")
        return f"{author} - {self.title} ({self.status})"


class SuggestionVote(models.Model):
    """Track user votes on suggestions"""
    VOTE_CHOICES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]
    
    suggestion = models.ForeignKey(Suggestion, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='suggestion_votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'suggestion_votes'
        unique_together = ('suggestion', 'user')
        indexes = [
            models.Index(fields=['suggestion', 'vote_type']),
        ]
    
    def __str__(self):
        return f"{self.user.user_id} - {self.vote_type} on #{self.suggestion.id}"
