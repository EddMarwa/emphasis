from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta, datetime
from decimal import Decimal

from .models import BotConfig, BotTrade, BotPerformance, BotExecutionLog
from .serializers import (
    BotConfigSerializer,
    BotTradeSerializer,
    BotPerformanceSerializer,
    BotExecutionLogSerializer,
    BotDashboardSerializer,
)
from apps.payments.models import Transaction, Balance
from apps.admin_panel.models import AdminLog


class BotConfigViewSet(viewsets.ViewSet):
    """Bot configuration and management"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_config(self, request):
        """Get current user's bot configuration"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            # Create default config if doesn't exist
            config = BotConfig.objects.create(
                user=request.user,
                strategy='balanced',
                is_enabled=False
            )
        
        serializer = BotConfigSerializer(config)
        return Response(serializer.data)

    @action(detail=False, methods=['put'])
    def update_config(self, request):
        """Update bot configuration"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            config = BotConfig.objects.create(user=request.user)

        serializer = BotConfigSerializer(config, data=request.data, partial=True)
        if serializer.is_valid():
            # Log config update if user is admin
            if hasattr(request.user, 'admin_user'):
                AdminLog.objects.create(
                    admin_user=request.user.admin_user,
                    action_type='config_updated',
                    resource_type='bot_config',
                    resource_id=config.id,
                    ip_address=self.get_client_ip(request),
                )
            
            serializer.save()
            BotExecutionLog.objects.create(
                bot_config=config,
                event_type='config_updated',
                event_message='Bot configuration updated',
                event_data={'changes': request.data}
            )
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def start_bot(self, request):
        """Start automated bot trading"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response({'error': 'Bot config not found'}, status=status.HTTP_404_NOT_FOUND)

        if config.is_enabled:
            return Response({'message': 'Bot is already running'}, status=status.HTTP_400_BAD_REQUEST)

        config.is_enabled = True
        config.save()

        BotExecutionLog.objects.create(
            bot_config=config,
            event_type='started',
            event_message='Bot trading started',
        )

        return Response({'message': 'Bot started successfully', 'config': BotConfigSerializer(config).data})

    @action(detail=False, methods=['post'])
    def stop_bot(self, request):
        """Stop automated bot trading"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response({'error': 'Bot config not found'}, status=status.HTTP_404_NOT_FOUND)

        if not config.is_enabled:
            return Response({'message': 'Bot is not running'}, status=status.HTTP_400_BAD_REQUEST)

        config.is_enabled = False
        config.save()

        BotExecutionLog.objects.create(
            bot_config=config,
            event_type='stopped',
            event_message='Bot trading stopped',
        )

        return Response({'message': 'Bot stopped successfully', 'config': BotConfigSerializer(config).data})

    @staticmethod
    def get_client_ip(request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR', '')


class BotTradeViewSet(viewsets.ViewSet):
    """Bot trade history and management"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def my_trades(self, request):
        """Get current user's trades"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response([], status=status.HTTP_200_OK)

        limit = request.query_params.get('limit', 20)
        trades = BotTrade.objects.filter(bot_config=config).order_by('-opened_at')[:int(limit)]
        
        serializer = BotTradeSerializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def open_trades(self, request):
        """Get currently open trades"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response([])

        trades = BotTrade.objects.filter(bot_config=config, status='open')
        serializer = BotTradeSerializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def closed_trades(self, request):
        """Get closed trades"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response([])

        trades = BotTrade.objects.filter(bot_config=config, status='closed')
        serializer = BotTradeSerializer(trades, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def execute_trade(self, request):
        """Manually execute a trade (admin or authorized users)"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response({'error': 'Bot not configured'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = BotTradeSerializer(data=request.data)
        if serializer.is_valid():
            # Check daily trading limit
            today_trades = BotTrade.objects.filter(
                bot_config=config,
                opened_at__date=timezone.now().date()
            )
            
            if today_trades.count() >= config.max_trades_per_day:
                return Response(
                    {'error': f'Daily trade limit ({config.max_trades_per_day}) reached'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            trade = serializer.save(bot_config=config, user=request.user, was_auto_executed=False)

            # Log execution
            BotExecutionLog.objects.create(
                bot_config=config,
                event_type='trade_executed',
                event_message=f'Manual trade executed: {trade.trade_type} {trade.quantity} {trade.asset}',
                related_trade=trade,
            )

            return Response(BotTradeSerializer(trade).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BotPerformanceViewSet(viewsets.ViewSet):
    """Bot performance analytics"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def daily_performance(self, request):
        """Get today's performance"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response({})

        today = timezone.now().date()
        performance_data = BotPerformance.calculate_daily_performance(config, today)
        
        return Response(performance_data or {})

    @action(detail=False, methods=['get'])
    def weekly_performance(self, request):
        """Get weekly performance"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response({})

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        
        performances = BotPerformance.objects.filter(
            bot_config=config,
            period_type='weekly',
            period_start__date=week_start
        )
        
        if performances.exists():
            serializer = BotPerformanceSerializer(performances.first())
            return Response(serializer.data)
        
        return Response({})

    @action(detail=False, methods=['get'])
    def monthly_performance(self, request):
        """Get monthly performance"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response({})

        today = timezone.now().date()
        month_start = today.replace(day=1)
        
        performances = BotPerformance.objects.filter(
            bot_config=config,
            period_type='monthly',
            period_start__date=month_start
        )
        
        if performances.exists():
            serializer = BotPerformanceSerializer(performances.first())
            return Response(serializer.data)
        
        return Response({})

    @action(detail=False, methods=['get'])
    def performance_history(self, request):
        """Get historical performance"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response([])

        period_type = request.query_params.get('period_type', 'daily')
        limit = request.query_params.get('limit', 30)
        
        performances = BotPerformance.objects.filter(
            bot_config=config,
            period_type=period_type
        ).order_by('-period_end')[:int(limit)]
        
        serializer = BotPerformanceSerializer(performances, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get comprehensive bot dashboard"""
        try:
            config = BotConfig.objects.get(user=request.user)
        except BotConfig.DoesNotExist:
            return Response({'error': 'Bot not configured'}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)

        # Get recent trades
        recent_trades = BotTrade.objects.filter(bot_config=config).order_by('-opened_at')[:10]

        # Calculate performance for today, week, month
        today_perf = BotPerformance.calculate_daily_performance(config, today) or {}
        
        week_perf = BotPerformance.objects.filter(
            bot_config=config,
            period_type='weekly',
            period_start__date=week_start
        ).first()
        week_perf_data = BotPerformanceSerializer(week_perf).data if week_perf else {}

        month_perf = BotPerformance.objects.filter(
            bot_config=config,
            period_type='monthly',
            period_start__date=month_start
        ).first()
        month_perf_data = BotPerformanceSerializer(month_perf).data if month_perf else {}

        # Get recent execution logs
        logs = BotExecutionLog.objects.filter(bot_config=config).order_by('-created_at')[:20]

        dashboard_data = {
            'config': BotConfigSerializer(config).data,
            'recent_trades': BotTradeSerializer(recent_trades, many=True).data,
            'today_performance': today_perf,
            'week_performance': week_perf_data,
            'month_performance': month_perf_data,
            'execution_logs': BotExecutionLogSerializer(logs, many=True).data,
        }

        return Response(dashboard_data)
