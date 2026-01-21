from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import json

User = get_user_model()


class BotConfig(models.Model):
    """Bot trading configuration per user"""
    STRATEGY_CHOICES = [
        ('conservative', 'Conservative - Low Risk'),
        ('balanced', 'Balanced - Medium Risk'),
        ('aggressive', 'Aggressive - High Risk'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='bot_config')
    is_enabled = models.BooleanField(default=False, help_text='Enable/disable bot trading')
    strategy = models.CharField(max_length=20, choices=STRATEGY_CHOICES, default='balanced')
    
    # Trading parameters
    daily_trading_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('1000'),
        help_text='Maximum amount to trade per day'
    )
    max_trades_per_day = models.IntegerField(default=5, help_text='Maximum number of trades per day')
    take_profit_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('5'),
        help_text='Take profit at X% gain'
    )
    stop_loss_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('2'),
        help_text='Stop loss at X% loss'
    )
    
    # Performance metrics
    total_trades = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bot_config'
        ordering = ['-updated_at']

    def __str__(self):
        return f"BotConfig for {self.user.username} ({self.strategy})"

    def calculate_win_rate(self):
        """Calculate win rate percentage"""
        total = self.total_trades
        if total == 0:
            return Decimal('0')
        return (Decimal(self.winning_trades) / Decimal(total)) * 100

    def update_metrics(self):
        """Update performance metrics from recent trades"""
        recent_trades = BotTrade.objects.filter(bot_config=self)
        self.total_trades = recent_trades.count()
        self.winning_trades = recent_trades.filter(status='closed', profit__gt=0).count()
        self.losing_trades = recent_trades.filter(status='closed', profit__lt=0).count()
        self.total_profit = sum([t.profit for t in recent_trades.filter(status='closed')]) or Decimal('0')
        self.win_rate = self.calculate_win_rate()
        self.save()


class BotTrade(models.Model):
    """Individual bot trade record"""
    TRADE_TYPE_CHOICES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('cancelled', 'Cancelled'),
    ]

    bot_config = models.ForeignKey(BotConfig, on_delete=models.CASCADE, related_name='trades')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bot_trades')
    
    # Trade details
    trade_type = models.CharField(max_length=10, choices=TRADE_TYPE_CHOICES)
    asset = models.CharField(max_length=20, default='USD', help_text='Asset being traded')
    entry_price = models.DecimalField(max_digits=12, decimal_places=2)
    entry_amount = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=8)
    
    # Exit details
    exit_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    exit_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    profit_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))
    
    # Status & timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    opened_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Auto trading
    was_auto_executed = models.BooleanField(default=True, help_text='Was this trade auto-executed by bot')
    triggered_by = models.CharField(
        max_length=50,
        default='scheduled',
        help_text='What triggered this trade: scheduled, price_action, signal, manual'
    )
    
    # Notes
    notes = models.TextField(blank=True, help_text='Trade notes or analysis')

    class Meta:
        db_table = 'bot_trade'
        ordering = ['-opened_at']

    def __str__(self):
        return f"Trade {self.id}: {self.trade_type} {self.quantity} {self.asset} @ {self.entry_price}"

    def calculate_profit(self):
        """Calculate profit when trade is closed"""
        if self.status != 'closed' or not self.exit_price:
            return Decimal('0')
        
        if self.trade_type == 'buy':
            gross_profit = (self.exit_price - self.entry_price) * self.quantity
        else:  # sell
            gross_profit = (self.entry_price - self.exit_price) * self.quantity
        
        # Deduct platform fees (0.5%)
        platform_fee = gross_profit * Decimal('0.005')
        net_profit = gross_profit - platform_fee
        
        if self.entry_amount > 0:
            profit_pct = (net_profit / self.entry_amount) * 100
        else:
            profit_pct = Decimal('0')
        
        return net_profit, profit_pct

    def close_trade(self, exit_price):
        """Close a trade at given price"""
        self.exit_price = exit_price
        self.exit_amount = exit_price * self.quantity
        self.status = 'closed'
        self.closed_at = timezone.now()
        
        profit, profit_pct = self.calculate_profit()
        self.profit = profit
        self.profit_percentage = profit_pct
        self.save()
        
        return profit


class BotPerformance(models.Model):
    """Daily/Weekly/Monthly bot performance snapshots"""
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    bot_config = models.ForeignKey(BotConfig, on_delete=models.CASCADE, related_name='performance_history')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bot_performance')
    
    # Period info
    period_type = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Metrics
    trades_count = models.IntegerField(default=0)
    winning_trades = models.IntegerField(default=0)
    losing_trades = models.IntegerField(default=0)
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    
    total_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    average_trade_profit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    largest_win = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    largest_loss = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    
    # Portfolio metrics
    starting_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    ending_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    roi_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal('0'))
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bot_performance'
        ordering = ['-period_end']
        indexes = [
            models.Index(fields=['bot_config', 'period_type', 'period_end']),
            models.Index(fields=['user', 'period_type']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.period_type.capitalize()} ({self.period_start.date()})"

    @staticmethod
    def calculate_daily_performance(bot_config, date):
        """Calculate daily performance for a bot config"""
        from datetime import timedelta
        
        start = timezone.datetime.combine(date, timezone.datetime.min.time())
        end = timezone.datetime.combine(date + timedelta(days=1), timezone.datetime.min.time())
        
        trades = BotTrade.objects.filter(
            bot_config=bot_config,
            closed_at__gte=start,
            closed_at__lt=end,
            status='closed'
        )
        
        if not trades.exists():
            return None
        
        winning = trades.filter(profit__gt=0).count()
        losing = trades.filter(profit__lt=0).count()
        total = trades.count()
        
        total_profit = sum([t.profit for t in trades]) or Decimal('0')
        
        return {
            'trades_count': total,
            'winning_trades': winning,
            'losing_trades': losing,
            'win_rate': (Decimal(winning) / Decimal(total) * 100) if total > 0 else Decimal('0'),
            'total_profit': total_profit,
            'average_trade_profit': total_profit / Decimal(total) if total > 0 else Decimal('0'),
            'largest_win': max([t.profit for t in trades]) if trades.exists() else Decimal('0'),
            'largest_loss': min([t.profit for t in trades]) if trades.exists() else Decimal('0'),
        }


class BotExecutionLog(models.Model):
    """Log of bot execution events"""
    EVENT_TYPE_CHOICES = [
        ('started', 'Bot Started'),
        ('stopped', 'Bot Stopped'),
        ('trade_executed', 'Trade Executed'),
        ('trade_closed', 'Trade Closed'),
        ('error', 'Error'),
        ('config_updated', 'Config Updated'),
    ]

    bot_config = models.ForeignKey(BotConfig, on_delete=models.CASCADE, related_name='execution_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    
    # Event details
    event_message = models.TextField()
    event_data = models.JSONField(default=dict, help_text='Additional event data as JSON')
    
    # Related trade (optional)
    related_trade = models.ForeignKey(BotTrade, on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bot_execution_log'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.bot_config.user.username} - {self.event_type} ({self.created_at})"
