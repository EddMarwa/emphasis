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
    referral_code VARCHAR(20) UNIQUE NOT NULL,
    referred_by VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (referred_by) REFERENCES users(user_id)
);

CREATE TABLE admin_users (
    admin_id VARCHAR(20) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    permissions TEXT[],
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE TABLE investments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    total_deposited DECIMAL(18, 2) DEFAULT 0.00,
    total_withdrawn DECIMAL(18, 2) DEFAULT 0.00,
    current_balance DECIMAL(18, 2) DEFAULT 0.00,
    total_profit DECIMAL(18, 2) DEFAULT 0.00,
    total_loss DECIMAL(18, 2) DEFAULT 0.00,
    active_investment DECIMAL(18, 2) DEFAULT 0.00,
    reserved_balance DECIMAL(18, 2) DEFAULT 0.00,
    roi_percentage DECIMAL(5, 2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(30) UNIQUE NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'KES',
    payment_method VARCHAR(50),
    payment_reference VARCHAR(255),
    status VARCHAR(20) DEFAULT 'pending',
    description TEXT,
    balance_before DECIMAL(18, 2),
    balance_after DECIMAL(18, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE deposits (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'KES',
    payment_method VARCHAR(50) NOT NULL,
    payment_reference VARCHAR(255),
    exchange_rate DECIMAL(10, 4) DEFAULT 1.00,
    amount_in_kes DECIMAL(18, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    confirmed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE withdrawals (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    amount DECIMAL(18, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'KES',
    payment_method VARCHAR(50) NOT NULL,
    destination_address VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    admin_approved_by VARCHAR(20),
    approved_at TIMESTAMP WITH TIME ZONE,
    processed_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (admin_approved_by) REFERENCES admin_users(admin_id)
);

CREATE TABLE bot_performance (
    id SERIAL PRIMARY KEY,
    performance_date DATE UNIQUE NOT NULL,
    total_trades INT DEFAULT 0,
    winning_trades INT DEFAULT 0,
    losing_trades INT DEFAULT 0,
    win_rate DECIMAL(5, 2) DEFAULT 0.00,
    total_profit DECIMAL(18, 2) DEFAULT 0.00,
    total_loss DECIMAL(18, 2) DEFAULT 0.00,
    net_profit DECIMAL(18, 2) DEFAULT 0.00,
    bot_status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bot_trades (
    id SERIAL PRIMARY KEY,
    trade_id VARCHAR(30) UNIQUE NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    trade_type VARCHAR(10) NOT NULL,
    entry_price DECIMAL(18, 8) NOT NULL,
    exit_price DECIMAL(18, 8),
    position_size DECIMAL(18, 8) NOT NULL,
    profit_loss DECIMAL(18, 2),
    status VARCHAR(20) DEFAULT 'open',
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    referrer_user_id VARCHAR(20) NOT NULL,
    referee_user_id VARCHAR(20) NOT NULL UNIQUE,
    referral_code VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    bonus_paid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (referrer_user_id) REFERENCES users(user_id),
    FOREIGN KEY (referee_user_id) REFERENCES users(user_id)
);

CREATE TABLE referral_bonuses (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    referral_id INTEGER NOT NULL,
    bonus_type VARCHAR(50) NOT NULL,
    bonus_amount DECIMAL(18, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (referral_id) REFERENCES referrals(id)
);

CREATE TABLE leaderboards (
    id SERIAL PRIMARY KEY,
    leaderboard_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    rank INTEGER NOT NULL,
    score DECIMAL(18, 2) DEFAULT 0.00,
    total_earnings DECIMAL(18, 2) DEFAULT 0.00,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE chat_conversations (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(30) UNIQUE NOT NULL,
    user_id VARCHAR(20),
    agent_id VARCHAR(20),
    status VARCHAR(20) DEFAULT 'open',
    priority VARCHAR(20) DEFAULT 'normal',
    subject TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (agent_id) REFERENCES admin_users(admin_id)
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    conversation_id VARCHAR(30) NOT NULL,
    sender_id VARCHAR(20) NOT NULL,
    sender_type VARCHAR(10) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    attachment_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES chat_conversations(conversation_id)
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    action_url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE training_videos (
    id SERIAL PRIMARY KEY,
    video_id VARCHAR(30) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_url VARCHAR(255) NOT NULL,
    thumbnail_url VARCHAR(255),
    category VARCHAR(50),
    duration INTEGER,
    order_index INTEGER,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE training_documents (
    id SERIAL PRIMARY KEY,
    document_id VARCHAR(30) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document_url VARCHAR(255) NOT NULL,
    document_type VARCHAR(50),
    category VARCHAR(50),
    file_size INTEGER,
    is_published BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_training_progress (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    video_id VARCHAR(30),
    document_id VARCHAR(30),
    progress_percentage DECIMAL(5, 2) DEFAULT 0.00,
    completed BOOLEAN DEFAULT FALSE,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (video_id) REFERENCES training_videos(video_id),
    FOREIGN KEY (document_id) REFERENCES training_documents(document_id)
);

CREATE TABLE suggestions (
    id SERIAL PRIMARY KEY,
    suggestion_id VARCHAR(30) UNIQUE NOT NULL,
    user_id VARCHAR(20),
    category VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    upvotes INTEGER DEFAULT 0,
    admin_response TEXT,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE kyc_documents (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    document_url VARCHAR(255) NOT NULL,
    verification_status VARCHAR(20) DEFAULT 'pending',
    rejection_reason TEXT,
    verified_by VARCHAR(20),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (verified_by) REFERENCES admin_users(admin_id)
);

CREATE TABLE security_logs (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    ip_address VARCHAR(45),
    device_info TEXT,
    location TEXT,
    status VARCHAR(20),
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE admin_actions (
    id SERIAL PRIMARY KEY,
    admin_id VARCHAR(20) NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    target_user_id VARCHAR(20),
    details TEXT,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES admin_users(admin_id),
    FOREIGN KEY (target_user_id) REFERENCES users(user_id)
);

CREATE TABLE platform_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value TEXT NOT NULL,
    description TEXT,
    updated_by VARCHAR(20),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (updated_by) REFERENCES admin_users(admin_id)
);

CREATE TABLE password_reset_tokens (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE verification_codes (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL,
    code VARCHAR(10) NOT NULL,
    code_type VARCHAR(20) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    verified BOOLEAN DEFAULT FALSE,
    attempts INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Initial Platform Settings
INSERT INTO platform_settings (setting_key, setting_value, description) VALUES
('platform_fee_percentage', '10', 'Percentage of profits taken as platform fee'),
('minimum_deposit', '100', 'Minimum deposit amount in KES'),
('minimum_withdrawal', '50', 'Minimum withdrawal amount in KES'),
('referral_bonus_referrer', '50', 'Bonus for referrer (KES)'),
('referral_bonus_referee', '20', 'Bonus for referee (KES)'),
('bot_status', 'active', 'Current bot status'),
('kyc_required_for_withdrawal', 'true', 'Whether KYC is required'),
('max_withdrawal_without_kyc', '5000', 'Max withdrawal without KYC (KES)');

-- Add Indexes for Performance
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_referral_code ON users(referral_code);
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
CREATE INDEX idx_transactions_type ON transactions(transaction_type);
CREATE INDEX idx_transactions_status ON transactions(status);

-- Auto-Update Trigger for Timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_investments_updated_at BEFORE UPDATE ON investments
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

