from django.contrib import admin
from django.utils.html import format_html
from .models import BotConfig, BotTrade, BotPerformance, BotExecutionLog


@admin.register(BotConfig)
class BotConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'strategy', 'is_enabled_display', 'total_trades', 'win_rate_display', 'total_profit']
    list_filter = ['strategy', 'is_enabled', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['total_trades', 'winning_trades', 'losing_trades', 'total_profit', 'win_rate', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Info', {'fields': ('user',)}),
        ('Bot Settings', {
            'fields': (
                'is_enabled',
                'strategy',
                'daily_trading_limit',
                'max_trades_per_day',
                'take_profit_percentage',
                'stop_loss_percentage'
            )
        }),
        ('Performance Metrics', {
            'fields': (
                'total_trades',
                'winning_trades',
                'losing_trades',
                'win_rate',
                'total_profit'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )

    def is_enabled_display(self, obj):
        if obj.is_enabled:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')
    is_enabled_display.short_description = 'Status'

    def win_rate_display(self, obj):
        return f"{obj.calculate_win_rate():.2f}%"
    win_rate_display.short_description = 'Win Rate'


@admin.register(BotTrade)
class BotTradeAdmin(admin.ModelAdmin):
    list_display = ['user', 'trade_type', 'asset', 'status', 'profit_display', 'opened_at']
    list_filter = ['status', 'trade_type', 'opened_at', 'was_auto_executed']
    search_fields = ['user__username', 'asset']
    readonly_fields = ['profit', 'profit_percentage', 'opened_at', 'closed_at']
    
    fieldsets = (
        ('User & Bot', {'fields': ('user', 'bot_config')}),
        ('Trade Details', {
            'fields': (
                'trade_type',
                'asset',
                'entry_price',
                'entry_amount',
                'quantity'
            )
        }),
        ('Exit Details', {
            'fields': (
                'exit_price',
                'exit_amount',
                'profit',
                'profit_percentage'
            ),
            'classes': ('collapse',)
        }),
        ('Status & Timing', {
            'fields': (
                'status',
                'opened_at',
                'closed_at'
            )
        }),
        ('Execution Info', {
            'fields': (
                'was_auto_executed',
                'triggered_by'
            )
        }),
        ('Notes', {'fields': ('notes',)}),
    )

    def profit_display(self, obj):
        if obj.profit > 0:
            return format_html(f'<span style="color: green;">+${obj.profit:.2f}</span>')
        elif obj.profit < 0:
            return format_html(f'<span style="color: red;">-${abs(obj.profit):.2f}</span>')
        return f'${obj.profit:.2f}'
    profit_display.short_description = 'Profit'


@admin.register(BotPerformance)
class BotPerformanceAdmin(admin.ModelAdmin):
    list_display = ['user', 'period_type', 'period_end', 'trades_count', 'win_rate', 'total_profit_display']
    list_filter = ['period_type', 'period_end']
    search_fields = ['user__username']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User & Bot', {'fields': ('user', 'bot_config')}),
        ('Period', {
            'fields': (
                'period_type',
                'period_start',
                'period_end'
            )
        }),
        ('Trade Metrics', {
            'fields': (
                'trades_count',
                'winning_trades',
                'losing_trades',
                'win_rate'
            )
        }),
        ('Profit Metrics', {
            'fields': (
                'total_profit',
                'average_trade_profit',
                'largest_win',
                'largest_loss'
            )
        }),
        ('Portfolio Metrics', {
            'fields': (
                'starting_balance',
                'ending_balance',
                'roi_percentage'
            )
        }),
        ('Timestamp', {'fields': ('created_at',)}),
    )

    def total_profit_display(self, obj):
        if obj.total_profit > 0:
            return format_html(f'<span style="color: green;">+${obj.total_profit:.2f}</span>')
        elif obj.total_profit < 0:
            return format_html(f'<span style="color: red;">-${abs(obj.total_profit):.2f}</span>')
        return f'${obj.total_profit:.2f}'
    total_profit_display.short_description = 'Total Profit'


@admin.register(BotExecutionLog)
class BotExecutionLogAdmin(admin.ModelAdmin):
    list_display = ['bot_config', 'event_type', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['bot_config__user__username', 'event_message']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Bot Config', {'fields': ('bot_config',)}),
        ('Event', {
            'fields': (
                'event_type',
                'event_message'
            )
        }),
        ('Event Data', {'fields': ('event_data',), 'classes': ('collapse',)}),
        ('Related Trade', {'fields': ('related_trade',), 'classes': ('collapse',)}),
        ('Timestamp', {'fields': ('created_at',)}),
    )
