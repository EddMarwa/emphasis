from rest_framework import serializers
from .models import BotConfig, BotTrade, BotPerformance, BotExecutionLog


class BotConfigSerializer(serializers.ModelSerializer):
    win_rate = serializers.SerializerMethodField()

    class Meta:
        model = BotConfig
        fields = [
            'id',
            'is_enabled',
            'strategy',
            'daily_trading_limit',
            'max_trades_per_day',
            'take_profit_percentage',
            'stop_loss_percentage',
            'total_trades',
            'winning_trades',
            'losing_trades',
            'total_profit',
            'win_rate',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['total_trades', 'winning_trades', 'losing_trades', 'total_profit', 'created_at', 'updated_at']

    def get_win_rate(self, obj):
        return str(obj.calculate_win_rate())


class BotTradeSerializer(serializers.ModelSerializer):
    profit_percentage = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    opened_at = serializers.DateTimeField(read_only=True)
    closed_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = BotTrade
        fields = [
            'id',
            'trade_type',
            'asset',
            'entry_price',
            'entry_amount',
            'quantity',
            'exit_price',
            'exit_amount',
            'profit',
            'profit_percentage',
            'status',
            'opened_at',
            'closed_at',
            'was_auto_executed',
            'triggered_by',
            'notes',
        ]
        read_only_fields = ['profit', 'profit_percentage', 'opened_at', 'closed_at', 'was_auto_executed']


class BotPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotPerformance
        fields = [
            'id',
            'period_type',
            'period_start',
            'period_end',
            'trades_count',
            'winning_trades',
            'losing_trades',
            'win_rate',
            'total_profit',
            'average_trade_profit',
            'largest_win',
            'largest_loss',
            'starting_balance',
            'ending_balance',
            'roi_percentage',
            'created_at',
        ]
        read_only_fields = ['created_at']


class BotExecutionLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotExecutionLog
        fields = [
            'id',
            'event_type',
            'event_message',
            'event_data',
            'related_trade',
            'created_at',
        ]
        read_only_fields = ['created_at']


class BotDashboardSerializer(serializers.Serializer):
    """Combined bot dashboard data"""
    config = BotConfigSerializer()
    recent_trades = BotTradeSerializer(many=True)
    today_performance = serializers.DictField()
    week_performance = serializers.DictField()
    month_performance = serializers.DictField()
    execution_logs = BotExecutionLogSerializer(many=True)
