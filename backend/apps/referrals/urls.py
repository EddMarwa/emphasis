from django.urls import path
from . import views

urlpatterns = [
    path('stats/', views.get_referral_stats, name='referral-stats'),
    path('code/', views.get_referral_code, name='referral-code'),
    path('my-referrals/', views.get_my_referrals, name='my-referrals'),
    path('analytics/', views.get_referral_analytics, name='referral-analytics'),
    path('leaderboard/', views.get_referral_leaderboard, name='referral-leaderboard'),
    path('my-ranking/', views.get_my_ranking, name='my-ranking'),
]
