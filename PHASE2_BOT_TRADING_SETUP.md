# Phase 2 Implementation - Bot Trading System

## Overview
Phase 2 Bot Trading System allows users to automate their trading with configurable strategies (Conservative, Balanced, Aggressive) and includes comprehensive performance tracking.

## Bot Architecture

### 1. BotConfig Model
User's bot trading configuration with:
- **Strategies**: Conservative (low risk), Balanced (medium), Aggressive (high)
- **Trading Parameters**: Daily limit, max trades/day, take-profit %, stop-loss %
- **Performance Metrics**: Total trades, win rate, profit tracking

### 2. BotTrade Model
Individual trade records with:
- **Trade Details**: Type (buy/sell), asset, entry/exit prices, quantity
- **Status Tracking**: Pending → Open → Closed/Cancelled
- **Profit Calculation**: Gross profit - platform fees (0.5%)
- **Auto-Execution Flag**: Track manual vs bot-executed trades

### 3. BotPerformance Model
Daily/Weekly/Monthly performance snapshots:
- Period performance metrics (win rate, profit, ROI)
- Portfolio metrics (starting/ending balance)
- Largest wins/losses tracking

### 4. BotExecutionLog Model
Audit trail of all bot events:
- Trade execution, configuration updates, errors
- Event-based logging with JSON data support
- Related trade references

## Bot API Endpoints

### Configuration Management (`/api/bot/config/`)

#### Get My Config
- **Endpoint**: `GET /api/bot/config/my_config/`
- **Response**: Current bot configuration with performance metrics
- **Status**: 200 OK

#### Update Config
- **Endpoint**: `PUT /api/bot/config/update_config/`
- **Body**:
```json
{
    "is_enabled": true,
    "strategy": "balanced",
    "daily_trading_limit": "1000.00",
    "max_trades_per_day": 5,
    "take_profit_percentage": "5.00",
    "stop_loss_percentage": "2.00"
}
```
- **Response**: Updated configuration

#### Start Bot
- **Endpoint**: `POST /api/bot/config/start_bot/`
- **Response**: `{"message": "Bot started successfully", "config": {...}}`

#### Stop Bot
- **Endpoint**: `POST /api/bot/config/stop_bot/`
- **Response**: `{"message": "Bot stopped successfully", "config": {...}}`

### Trade Management (`/api/bot/trades/`)

#### Get My Trades
- **Endpoint**: `GET /api/bot/trades/my_trades/?limit=20`
- **Response**: List of all user's trades (limited to 20 most recent)

#### Get Open Trades
- **Endpoint**: `GET /api/bot/trades/open_trades/`
- **Response**: Currently open trades

#### Get Closed Trades
- **Endpoint**: `GET /api/bot/trades/closed_trades/`
- **Response**: Closed trades with final profit amounts

#### Execute Manual Trade
- **Endpoint**: `POST /api/bot/trades/execute_trade/`
- **Body**:
```json
{
    "trade_type": "buy",
    "asset": "USD",
    "entry_price": "100.50",
    "entry_amount": "500.00",
    "quantity": "4.97",
    "notes": "Manual trade based on market analysis"
}
```
- **Response**: Created trade object
- **Validation**: Checks daily trade limit, triggers execution log

### Performance Analytics (`/api/bot/performance/`)

#### Daily Performance
- **Endpoint**: `GET /api/bot/performance/daily_performance/`
- **Response**:
```json
{
    "trades_count": 3,
    "winning_trades": 2,
    "losing_trades": 1,
    "win_rate": "66.67",
    "total_profit": "125.50",
    "average_trade_profit": "41.83",
    "largest_win": "75.00",
    "largest_loss": "-10.50"
}
```

#### Weekly Performance
- **Endpoint**: `GET /api/bot/performance/weekly_performance/`
- **Response**: Full BotPerformance object for current week

#### Monthly Performance
- **Endpoint**: `GET /api/bot/performance/monthly_performance/`
- **Response**: Full BotPerformance object for current month

#### Performance History
- **Endpoint**: `GET /api/bot/performance/performance_history/?period_type=daily&limit=30`
- **Query Params**: 
  - `period_type`: daily|weekly|monthly
  - `limit`: Number of periods to return (default 30)
- **Response**: Array of BotPerformance objects

#### Bot Dashboard
- **Endpoint**: `GET /api/bot/performance/dashboard/`
- **Response**: Comprehensive dashboard with:
  - Current configuration
  - Recent trades (10 most recent)
  - Today/week/month performance
  - Execution logs (20 most recent)

## Bot Configuration Strategies

### Conservative Strategy
- **Daily Limit**: $500
- **Max Trades/Day**: 3
- **Take Profit**: 3%
- **Stop Loss**: 1%
- **Ideal For**: Risk-averse investors

### Balanced Strategy (Default)
- **Daily Limit**: $1,000
- **Max Trades/Day**: 5
- **Take Profit**: 5%
- **Stop Loss**: 2%
- **Ideal For**: Most users

### Aggressive Strategy
- **Daily Limit**: $5,000
- **Max Trades/Day**: 10
- **Take Profit**: 10%
- **Stop Loss**: 5%
- **Ideal For**: Experienced traders

## Profit Calculation

### Trade Profit Formula
```
For BUY trades:
Gross Profit = (Exit Price - Entry Price) × Quantity

For SELL trades:
Gross Profit = (Entry Price - Exit Price) × Quantity

Net Profit = Gross Profit - Platform Fee (0.5%)
Profit % = (Net Profit / Entry Amount) × 100
```

## Win Rate Calculation

```
Win Rate = (Winning Trades / Total Trades) × 100
```

Where:
- **Winning Trade**: status='closed' AND profit > 0
- **Losing Trade**: status='closed' AND profit < 0

## Database Setup

### Step 1: Create Migrations
```bash
cd backend
python manage.py makemigrations bot
```

### Step 2: Apply Migrations
```bash
python manage.py migrate bot
```

### Step 3: Verify Setup
```bash
python manage.py shell
from apps.bot.models import BotConfig
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.first()
config = BotConfig.objects.create(user=user, strategy='balanced')
print(f"Bot config created for {user.username}")
```

## Django Admin Interface

Access at `/admin/` to manage:

1. **Bot Configurations**: View all user bot configurations, performance metrics, and strategies
2. **Bot Trades**: View all executed trades with profit/loss display, filter by status
3. **Performance History**: View daily/weekly/monthly snapshots
4. **Execution Logs**: Audit trail of all bot events

## API Usage Examples

### Start Bot Trading
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/bot/config/start_bot/
```

### Check Today's Performance
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/bot/performance/daily_performance/
```

### View Bot Dashboard
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/bot/performance/dashboard/
```

### Execute Manual Trade
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "trade_type": "buy",
    "asset": "USD",
    "entry_price": "100.00",
    "entry_amount": "500.00",
    "quantity": "5.00",
    "notes": "Manual buy based on market signal"
  }' \
  http://localhost:8000/api/bot/trades/execute_trade/
```

## Frontend Integration (Services)

Create `frontend/src/services/bot.js`:

```javascript
import axios from 'axios';

const API = axios.create({
    baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
    withCredentials: true,
});

export const botAPI = {
    // Configuration
    getConfig: () => API.get('/bot/config/my_config/'),
    updateConfig: (data) => API.put('/bot/config/update_config/', data),
    startBot: () => API.post('/bot/config/start_bot/'),
    stopBot: () => API.post('/bot/config/stop_bot/'),

    // Trades
    getMyTrades: (limit = 20) => API.get(`/bot/trades/my_trades/?limit=${limit}`),
    getOpenTrades: () => API.get('/bot/trades/open_trades/'),
    getClosedTrades: () => API.get('/bot/trades/closed_trades/'),
    executeTrade: (data) => API.post('/bot/trades/execute_trade/', data),

    // Performance
    getDailyPerformance: () => API.get('/bot/performance/daily_performance/'),
    getWeeklyPerformance: () => API.get('/bot/performance/weekly_performance/'),
    getMonthlyPerformance: () => API.get('/bot/performance/monthly_performance/'),
    getPerformanceHistory: (periodType = 'daily', limit = 30) => 
        API.get(`/bot/performance/performance_history/?period_type=${periodType}&limit=${limit}`),
    getDashboard: () => API.get('/bot/performance/dashboard/'),
};
```

## Testing the System

### Test 1: Create Bot Config
```bash
# Start bot trading
curl -X POST \
  -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/bot/config/start_bot/

# Verify it started
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/bot/config/my_config/
```

### Test 2: Execute Manual Trade
```bash
curl -X POST \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "trade_type": "buy",
    "asset": "USD",
    "entry_price": "100.00",
    "entry_amount": "500.00",
    "quantity": "5.00"
  }' \
  http://localhost:8000/api/bot/trades/execute_trade/
```

### Test 3: Close Trade (Via Admin Shell)
```bash
python manage.py shell
from apps.bot.models import BotTrade
from decimal import Decimal

trade = BotTrade.objects.last()
profit = trade.close_trade(Decimal('105.00'))
print(f"Trade closed with profit: {profit}")
```

### Test 4: View Performance
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/bot/performance/dashboard/
```

## Models Summary

| Model | Purpose | Key Fields |
|-------|---------|-----------|
| BotConfig | User bot settings | strategy, is_enabled, daily_limit, max_trades |
| BotTrade | Individual trades | entry_price, exit_price, status, profit |
| BotPerformance | Period snapshots | period_type, total_profit, roi, win_rate |
| BotExecutionLog | Event audit trail | event_type, event_message, event_data |

## Next Steps: Phase 2 Completion

After Bot Trading setup:
1. **Advanced Analytics Backend**: Performance reports, return calculations, metrics
2. **Frontend Bot Management Pages**: Bot dashboard, trade history, performance charts
3. **Payment Integration**: M-Pesa, Crypto (scaffolding and integration)
4. **Mobile App**: React Native implementation
5. **Additional Features**: Referrals, Chat, Notifications

## Troubleshooting

### Bot Config Not Found Error
Ensure user has bot config created:
```bash
python manage.py shell
from apps.bot.models import BotConfig
from django.contrib.auth import get_user_model
User = get_user_model()
user = User.objects.get(username='testuser')
BotConfig.objects.get_or_create(user=user, defaults={'strategy': 'balanced'})
```

### Trade Execution Limit Error
Check daily trade count:
```bash
from apps.bot.models import BotTrade
from datetime import date
today = date.today()
count = BotTrade.objects.filter(opened_at__date=today).count()
print(f"Trades today: {count}")
```

### Performance Data Not Calculating
Manually trigger calculation:
```bash
from apps.bot.models import BotPerformance
from datetime import date
perf_data = BotPerformance.calculate_daily_performance(bot_config, date.today())
print(perf_data)
```

## Database Schema

**New Tables:**
- bot_botconfig
- bot_bottrade
- bot_botperformance
- bot_botexecutionlog

**Key Indexes:**
- (bot_config, opened_at)
- (user, opened_at)
- (bot_config, period_type, period_end)
- (user, period_type)

