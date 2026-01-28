from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from .models import Referral, ReferralBonus, ReferralLeaderboard, ReferralAnalytics, ReferralProgram
from .serializers import (ReferralSerializer, ReferralBonusSerializer, ReferralLeaderboardSerializer,
                         ReferralAnalyticsSerializer, ReferralStatsSerializer)
from apps.users.models import User


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_stats(request):
    """Get referral statistics for current user"""
    try:
        user = request.user
        
        # Get all referrals
        referrals = Referral.objects.filter(referrer=user)
        
        # Calculate stats
        total_referrals = referrals.count()
        active_referrals = referrals.filter(status='active').count()
        pending_referrals = referrals.filter(status='pending').count()
        
        # Tier counts
        tier1_count = referrals.filter(tier_level=1).count()
        tier2_count = referrals.filter(tier_level=2).count()
        tier3_count = referrals.filter(tier_level=3).count()
        
        # Bonus stats
        bonuses = ReferralBonus.objects.filter(recipient=user)
        total_bonuses_earned = bonuses.aggregate(
            total=Sum('amount', filter=Q(status__in=['approved', 'distributed']))
        )['total'] or Decimal('0.00')
        
        total_bonuses_pending = bonuses.aggregate(
            total=Sum('amount', filter=Q(status='pending'))
        )['total'] or Decimal('0.00')
        
        total_bonuses_distributed = bonuses.aggregate(
            total=Sum('amount', filter=Q(status='distributed'))
        )['total'] or Decimal('0.00')
        
        # Referral link
        referral_link = f"{request.scheme}://{request.get_host()}/register?ref={user.referral_code}"
        
        stats = {
            'total_referrals': total_referrals,
            'active_referrals': active_referrals,
            'pending_referrals': pending_referrals,
            'total_bonuses_earned': total_bonuses_earned,
            'total_bonuses_pending': total_bonuses_pending,
            'total_bonuses_distributed': total_bonuses_distributed,
            'referral_code': user.referral_code,
            'referral_link': referral_link,
            'tier1_count': tier1_count,
            'tier2_count': tier2_count,
            'tier3_count': tier3_count,
        }
        
        serializer = ReferralStatsSerializer(stats)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_code(request):
    """Get user's referral code and link"""
    try:
        user = request.user
        referral_link = f"{request.scheme}://{request.get_host()}/register?ref={user.referral_code}"
        
        return Response({
            'referral_code': user.referral_code,
            'referral_link': referral_link
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_referrals(request):
    """Get list of user's referrals"""
    try:
        user = request.user
        referrals = Referral.objects.filter(referrer=user).select_related('referee')
        serializer = ReferralSerializer(referrals, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_analytics(request):
    """Get referral analytics over time"""
    try:
        user = request.user
        days = int(request.GET.get('days', 30))
        
        start_date = timezone.now().date() - timedelta(days=days)
        analytics = ReferralAnalytics.objects.filter(
            user=user,
            date__gte=start_date
        ).order_by('date')
        
        serializer = ReferralAnalyticsSerializer(analytics, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_referral_leaderboard(request):
    """Get referral leaderboard"""
    try:
        period = request.GET.get('period', 'monthly')  # weekly, monthly, quarterly, yearly, all_time
        limit = int(request.GET.get('limit', 100))
        
        # Get current period dates
        today = timezone.now().date()
        if period == 'weekly':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'monthly':
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        elif period == 'quarterly':
            quarter = (today.month - 1) // 3
            start_date = today.replace(month=quarter * 3 + 1, day=1)
            end_month = (quarter + 1) * 3 + 1
            if end_month > 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=end_month, day=1) - timedelta(days=1)
        elif period == 'yearly':
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:  # all_time
            start_date = datetime(2020, 1, 1).date()
            end_date = today
        
        leaderboard = ReferralLeaderboard.objects.filter(
            period_type=period,
            period_start=start_date,
            period_end=end_date
        ).order_by('rank')[:limit]
        
        serializer = ReferralLeaderboardSerializer(leaderboard, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_ranking(request):
    """Get current user's ranking"""
    try:
        user = request.user
        period = request.GET.get('period', 'monthly')
        
        ranking = ReferralLeaderboard.objects.filter(
            user=user,
            period_type=period
        ).first()
        
        if ranking:
            serializer = ReferralLeaderboardSerializer(ranking)
            return Response(serializer.data)
        else:
            return Response({
                'rank': 0,
                'total_referrals': 0,
                'total_bonus_earned': 0,
                'points': 0
            })
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
