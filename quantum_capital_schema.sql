-- QUANTUM CAPITAL PLATFORM - DATABASE SCHEMA
-- Complete schema with 24 tables, indexes, triggers, and initial data
-- Execute in order from top to bottom

-- ============================================================================
-- TABLE 1: users
-- ============================================================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    country_code VARCHAR(5) DEFAULT 'KE',
    date_of_birth DATE,
    profile_picture VARCHAR(255),
    account_status VARCHAR(20) DEFAULT 'active',
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE,
    kyc_status VARCHAR(20) DEFAULT 'unverified',
    referral_code VARCHAR(20) UNIQUE,
    referred_by VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    CONSTRAINT fk_referred_by FOREIGN KEY (referred_by) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_referral_code ON users(referral_code);

COMMENT ON TABLE users IS 'Main users table with authentication and profile data';
COMMENT ON COLUMN users.user_id IS 'Unique user identifier format: KE-QC-00001';
COMMENT ON COLUMN users.account_status IS 'active, suspended, pending, closed';
COMMENT ON COLUMN users.kyc_status IS 'unverified, pending, verified, rejected';

-- ============================================================================
-- TABLE 2: admin_users
-- ============================================================================
CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    permissions TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_admin_users_admin_id ON admin_users(admin_id);

COMMENT ON TABLE admin_users IS 'Platform administrators and support staff';
COMMENT ON COLUMN admin_users.admin_id IS 'Unique admin identifier format: KE-ADM-00001';
COMMENT ON COLUMN admin_users.role IS 'admin, super_admin, support, trader';

-- ============================================================================
-- TABLE 3: investments
-- ============================================================================
CREATE TABLE investments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    total_deposited DECIMAL(15, 2) DEFAULT 0.00,
    total_withdrawn DECIMAL(15, 2) DEFAULT 0.00,
    current_balance DECIMAL(15, 2) DEFAULT 0.00,
    total_profit DECIMAL(15, 2) DEFAULT 0.00,
    total_loss DECIMAL(15, 2) DEFAULT 0.00,
    active_investment DECIMAL(15, 2) DEFAULT 0.00,
    reserved_balance DECIMAL(15, 2) DEFAULT 0.00,
    roi_percentage DECIMAL(5, 2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_investments_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_investments_user_id ON investments(user_id);

COMMENT ON TABLE investments IS 'User investment portfolio and balance tracking';
COMMENT ON COLUMN investments.active_investment IS 'Amount currently in active trading';
COMMENT ON COLUMN investments.reserved_balance IS 'Amount not in active trading';

-- ============================================================================
-- TABLE 4: transactions
-- ============================================================================
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'KES',
    payment_method VARCHAR(50),
    payment_reference VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    description TEXT,
    balance_before DECIMAL(15, 2),
    balance_after DECIMAL(15, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP,
    CONSTRAINT fk_transactions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_created_at ON transactions(created_at);

COMMENT ON TABLE transactions IS 'All financial transactions on the platform';
COMMENT ON COLUMN transactions.transaction_id IS 'Unique transaction ID format: TXN-20260111-000001';
COMMENT ON COLUMN transactions.transaction_type IS 'deposit, withdrawal, profit, loss, fee, bonus, referral_bonus';
COMMENT ON COLUMN transactions.status IS 'pending, completed, failed, cancelled';

-- ============================================================================
-- TABLE 5: deposits
-- ============================================================================
CREATE TABLE deposits (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'KES',
    payment_method VARCHAR(50) NOT NULL,
    payment_reference VARCHAR(100),
    exchange_rate DECIMAL(10, 4),
    amount_in_kes DECIMAL(15, 2),
    status VARCHAR(20) DEFAULT 'pending',
    confirmed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_deposits_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_deposits_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
);

CREATE INDEX idx_deposits_user_id ON deposits(user_id);
CREATE INDEX idx_deposits_status ON deposits(status);

COMMENT ON TABLE deposits IS 'Deposit transaction details';
COMMENT ON COLUMN deposits.payment_method IS 'mpesa, usdt_trc20, usdt_erc20, bitcoin';

-- ============================================================================
-- TABLE 6: withdrawals
-- ============================================================================
CREATE TABLE withdrawals (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'KES',
    payment_method VARCHAR(50) NOT NULL,
    destination_address VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    admin_approved_by VARCHAR(20),
    approved_at TIMESTAMP,
    processed_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_withdrawals_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_withdrawals_transaction FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE
);

CREATE INDEX idx_withdrawals_user_id ON withdrawals(user_id);
CREATE INDEX idx_withdrawals_status ON withdrawals(status);

COMMENT ON TABLE withdrawals IS 'Withdrawal transaction details';
COMMENT ON COLUMN withdrawals.destination_address IS 'Phone number for M-Pesa or wallet address for crypto';

-- ============================================================================
-- TABLE 7: bot_performance
-- ============================================================================
CREATE TABLE bot_performance (
    id SERIAL PRIMARY KEY,
    performance_date DATE NOT NULL UNIQUE,
    total_trades INTEGER DEFAULT 0,
    winning_trades INTEGER DEFAULT 0,
    losing_trades INTEGER DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0.00,
    total_profit DECIMAL(15, 2) DEFAULT 0.00,
    total_loss DECIMAL(15, 2) DEFAULT 0.00,
    net_profit DECIMAL(15, 2) DEFAULT 0.00,
    bot_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bot_performance_date ON bot_performance(performance_date);

COMMENT ON TABLE bot_performance IS 'Daily bot trading performance summary';
COMMENT ON COLUMN bot_performance.bot_status IS 'active, inactive, maintenance';

-- ============================================================================
-- TABLE 8: bot_trades
-- ============================================================================
CREATE TABLE bot_trades (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(50) UNIQUE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    entry_price DECIMAL(15, 6) NOT NULL,
    exit_price DECIMAL(15, 6),
    position_size DECIMAL(15, 2) NOT NULL,
    profit_loss DECIMAL(15, 2),
    status VARCHAR(20) DEFAULT 'open',
    opened_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE INDEX idx_bot_trades_symbol ON bot_trades(symbol);
CREATE INDEX idx_bot_trades_status ON bot_trades(status);
CREATE INDEX idx_bot_trades_opened_at ON bot_trades(opened_at);

COMMENT ON TABLE bot_trades IS 'Individual bot trade records';
COMMENT ON COLUMN bot_trades.symbol IS 'Trading symbol: Volatility 75, Crash 500, Boom 1000, etc.';
COMMENT ON COLUMN bot_trades.trade_type IS 'buy, sell';
COMMENT ON COLUMN bot_trades.status IS 'open, closed, cancelled';

-- ============================================================================
-- TABLE 9: referrals
-- ============================================================================
CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_user_id VARCHAR(20) NOT NULL,
    referee_user_id VARCHAR(20) NOT NULL,
    referral_code VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    bonus_paid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    CONSTRAINT fk_referrals_referrer FOREIGN KEY (referrer_user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_referrals_referee FOREIGN KEY (referee_user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_referrals_referrer ON referrals(referrer_user_id);
CREATE INDEX idx_referrals_referee ON referrals(referee_user_id);

COMMENT ON TABLE referrals IS 'Tracks user referrals';
COMMENT ON COLUMN referrals.status IS 'pending, completed, cancelled';

-- ============================================================================
-- TABLE 10: referral_bonuses
-- ============================================================================
CREATE TABLE referral_bonuses (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    referral_id INTEGER NOT NULL,
    bonus_type VARCHAR(20) NOT NULL,
    bonus_amount DECIMAL(15, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_referral_bonuses_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_referral_bonuses_referral FOREIGN KEY (referral_id) REFERENCES referrals(id) ON DELETE CASCADE
);

CREATE INDEX idx_referral_bonuses_user_id ON referral_bonuses(user_id);

COMMENT ON TABLE referral_bonuses IS 'Referral bonus distribution';
COMMENT ON COLUMN referral_bonuses.bonus_type IS 'referrer_bonus, referee_bonus';
COMMENT ON COLUMN referral_bonuses.status IS 'pending, paid, cancelled';

-- ============================================================================
-- TABLE 11: leaderboards
-- ============================================================================
CREATE TABLE leaderboards (
    id SERIAL PRIMARY KEY,
    leaderboard_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    rank INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total_earnings DECIMAL(15, 2) DEFAULT 0.00,
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_leaderboards_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_leaderboards_type ON leaderboards(leaderboard_type);
CREATE INDEX idx_leaderboards_rank ON leaderboards(rank);

COMMENT ON TABLE leaderboards IS 'Referral leaderboard rankings';
COMMENT ON COLUMN leaderboards.leaderboard_type IS 'referral_weekly, referral_monthly, referral_all_time';

-- ============================================================================
-- TABLE 12: chat_conversations
-- ============================================================================
CREATE TABLE chat_conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    agent_id VARCHAR(20),
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'normal',
    subject VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP,
    CONSTRAINT fk_chat_conversations_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_chat_conversations_user_id ON chat_conversations(user_id);
CREATE INDEX idx_chat_conversations_status ON chat_conversations(status);

COMMENT ON TABLE chat_conversations IS 'Support chat conversation sessions';
COMMENT ON COLUMN chat_conversations.status IS 'open, closed, waiting';
COMMENT ON COLUMN chat_conversations.priority IS 'low, normal, high, urgent';

-- ============================================================================
-- TABLE 13: chat_messages
-- ============================================================================
CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(50) NOT NULL,
    sender_id VARCHAR(20) NOT NULL,
    sender_type VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    attachment_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_chat_messages_conversation FOREIGN KEY (conversation_id) REFERENCES chat_conversations(conversation_id) ON DELETE CASCADE
);

CREATE INDEX idx_chat_messages_conversation_id ON chat_messages(conversation_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);

COMMENT ON TABLE chat_messages IS 'Individual chat messages';
COMMENT ON COLUMN chat_messages.sender_type IS 'user, admin';

-- ============================================================================
-- TABLE 14: notifications
-- ============================================================================
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notifications_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);

COMMENT ON TABLE notifications IS 'User notifications';
COMMENT ON COLUMN notifications.notification_type IS 'deposit, withdrawal, profit, security, referral';

-- ============================================================================
-- TABLE 15: training_videos
-- ============================================================================
CREATE TABLE training_videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_url VARCHAR(500) NOT NULL,
    thumbnail_url VARCHAR(500),
    category VARCHAR(100),
    duration INTEGER,
    order_index INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_training_videos_category ON training_videos(category);
CREATE INDEX idx_training_videos_is_published ON training_videos(is_published);

COMMENT ON TABLE training_videos IS 'Educational training videos';
COMMENT ON COLUMN training_videos.category IS 'getting_started, deposits, trading, withdrawals';
COMMENT ON COLUMN training_videos.duration IS 'Video duration in seconds';

-- ============================================================================
-- TABLE 16: training_documents
-- ============================================================================
CREATE TABLE training_documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(50) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_url VARCHAR(500) NOT NULL,
    document_type VARCHAR(20),
    category VARCHAR(100),
    file_size INTEGER,
    is_published BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_training_documents_category ON training_documents(category);

COMMENT ON TABLE training_documents IS 'Educational training documents';
COMMENT ON COLUMN training_documents.document_type IS 'pdf, docx, txt';
COMMENT ON COLUMN training_documents.file_size IS 'File size in bytes';

-- ============================================================================
-- TABLE 17: user_training_progress
-- ============================================================================
CREATE TABLE user_training_progress (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    video_id VARCHAR(50),
    document_id VARCHAR(50),
    progress_percentage INTEGER DEFAULT 0,
    completed BOOLEAN DEFAULT FALSE,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_training_progress_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_user_training_progress_user_id ON user_training_progress(user_id);

COMMENT ON TABLE user_training_progress IS 'Tracks user progress through training materials';

-- ============================================================================
-- TABLE 18: suggestions
-- ============================================================================
CREATE TABLE suggestions (
    id SERIAL PRIMARY KEY,
    suggestion_id VARCHAR(50) UNIQUE NOT NULL,
    user_id VARCHAR(20),
    category VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    upvotes INTEGER DEFAULT 0,
    admin_response TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP,
    CONSTRAINT fk_suggestions_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_suggestions_status ON suggestions(status);
CREATE INDEX idx_suggestions_category ON suggestions(category);

COMMENT ON TABLE suggestions IS 'User feedback and suggestions';
COMMENT ON COLUMN suggestions.category IS 'bug, feature, improvement, general';
COMMENT ON COLUMN suggestions.status IS 'pending, reviewed, accepted, implemented, rejected';

-- ============================================================================
-- TABLE 19: kyc_documents
-- ============================================================================
CREATE TABLE kyc_documents (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_url VARCHAR(500) NOT NULL,
    verification_status VARCHAR(20) DEFAULT 'pending',
    rejection_reason TEXT,
    verified_by VARCHAR(20),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_kyc_documents_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_kyc_documents_user_id ON kyc_documents(user_id);
CREATE INDEX idx_kyc_documents_status ON kyc_documents(verification_status);

COMMENT ON TABLE kyc_documents IS 'KYC verification documents';
COMMENT ON COLUMN kyc_documents.document_type IS 'national_id, passport, selfie, address_proof';
COMMENT ON COLUMN kyc_documents.verification_status IS 'pending, verified, rejected';

-- ============================================================================
-- TABLE 20: security_logs
-- ============================================================================
CREATE TABLE security_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20),
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    device_info TEXT,
    location VARCHAR(255),
    status VARCHAR(20),
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_security_logs_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL
);

CREATE INDEX idx_security_logs_user_id ON security_logs(user_id);
CREATE INDEX idx_security_logs_event_type ON security_logs(event_type);
CREATE INDEX idx_security_logs_created_at ON security_logs(created_at);

COMMENT ON TABLE security_logs IS 'Security event audit log';
COMMENT ON COLUMN security_logs.event_type IS 'login, logout, failed_login, password_change, 2fa';
COMMENT ON COLUMN security_logs.status IS 'success, failed';

-- ============================================================================
-- TABLE 21: admin_actions
-- ============================================================================
CREATE TABLE admin_actions (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(20) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    target_user_id VARCHAR(20),
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_admin_actions_admin FOREIGN KEY (admin_id) REFERENCES admin_users(admin_id) ON DELETE CASCADE
);

CREATE INDEX idx_admin_actions_admin_id ON admin_actions(admin_id);
CREATE INDEX idx_admin_actions_created_at ON admin_actions(created_at);

COMMENT ON TABLE admin_actions IS 'Admin action audit trail';
COMMENT ON COLUMN admin_actions.action_type IS 'user_suspend, withdrawal_approve, kyc_verify, etc.';

-- ============================================================================
-- TABLE 22: platform_settings
-- ============================================================================
CREATE TABLE platform_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_by VARCHAR(20),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_platform_settings_key ON platform_settings(setting_key);

COMMENT ON TABLE platform_settings IS 'Platform configuration and settings';

-- ============================================================================
-- TABLE 23: password_reset_tokens
-- ============================================================================
CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_password_reset_tokens_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX idx_password_reset_tokens_user_id ON password_reset_tokens(user_id);

COMMENT ON TABLE password_reset_tokens IS 'Password reset token management';

-- ============================================================================
-- TABLE 24: verification_codes
-- ============================================================================
CREATE TABLE verification_codes (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    code VARCHAR(10) NOT NULL,
    code_type VARCHAR(20) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_verification_codes_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE INDEX idx_verification_codes_user_id ON verification_codes(user_id);
CREATE INDEX idx_verification_codes_code ON verification_codes(code);

COMMENT ON TABLE verification_codes IS 'Email and phone verification codes';
COMMENT ON COLUMN verification_codes.code_type IS 'email, phone';

-- ============================================================================
-- AUTO-UPDATE TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to users table
CREATE TRIGGER update_users_updated_at 
BEFORE UPDATE ON users
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to investments table
CREATE TRIGGER update_investments_updated_at 
BEFORE UPDATE ON investments
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to training_videos table
CREATE TRIGGER update_training_videos_updated_at 
BEFORE UPDATE ON training_videos
FOR EACH ROW 
EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL PLATFORM SETTINGS
-- ============================================================================

INSERT INTO platform_settings (setting_key, setting_value, description) VALUES
('platform_fee_percentage', '10', 'Percentage of profits taken as platform fee'),
('minimum_deposit', '100', 'Minimum deposit amount in KES'),
('minimum_withdrawal', '50', 'Minimum withdrawal amount in KES'),
('referral_bonus_referrer', '50', 'Bonus amount for user who refers in KES'),
('referral_bonus_referee', '20', 'Bonus amount for new user who signs up in KES'),
('bot_status', 'active', 'Current bot operational status: active, inactive, maintenance'),
('kyc_required_for_withdrawal', 'true', 'Whether KYC verification is required for withdrawals'),
('max_withdrawal_without_kyc', '5000', 'Maximum withdrawal amount without KYC verification in KES'),
('maintenance_mode', 'false', 'Platform maintenance mode flag'),
('support_email', 'support@quantumcapital.com', 'Platform support email address'),
('platform_launch_date', '2026-01-11', 'Official platform launch date');
