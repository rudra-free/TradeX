CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    admin_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    admin_add TEXT,
    admin_phone_no VARCHAR(15),
    admin_mail VARCHAR(100) UNIQUE,
    role VARCHAR(30) DEFAULT 'ADMIN',
    status ENUM('ACTIVE', 'INACTIVE', 'BLOCKED') DEFAULT 'ACTIVE',
    ip VARCHAR(45),
    login_ip VARCHAR(45),
    last_login DATETIME,
    is_deleted TINYINT(1) DEFAULT 0,
    created_by INT,
    updated_by INT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
 
CREATE TABLE users (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE,
    phone VARCHAR(20) UNIQUE,
    password_hash VARCHAR(255),

    login_type ENUM('normal', 'google', 'facebook', 'apple') DEFAULT 'normal',

    google_id VARCHAR(255) UNIQUE,
    facebook_id VARCHAR(255) UNIQUE,
    apple_id VARCHAR(255) UNIQUE,

    profile_image VARCHAR(255),
    last_login DATETIME,

    status ENUM('active', 'inactive', 'blocked') DEFAULT 'active',
    is_deleted TINYINT(1) DEFAULT 0,

    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100),
    pincode VARCHAR(20),

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP
);



CREATE TABLE apis (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    -- Basic API Details
    api_name VARCHAR(150) NOT NULL,
    slug VARCHAR(150) UNIQUE NOT NULL,
    category VARCHAR(100),

    -- API Usage Type
    access_type ENUM('free', 'paid', 'subscription') DEFAULT 'free',

    -- Subscription Info (nullable)
    subscription_start DATETIME,
    subscription_end DATETIME,

    -- Technical Details
    base_url VARCHAR(255) NOT NULL,
    api_key_hash VARCHAR(255),     -- store hashed/encrypted key
    rate_limit_per_min INT DEFAULT 60,
    status ENUM('active', 'inactive', 'deprecated') DEFAULT 'active',

    -- Optional Fields
    description TEXT,
    provider VARCHAR(150),

    -- Soft Delete
    is_deleted TINYINT(1) DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
        ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE transactions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    user_id BIGINT NOT NULL,

    -- PURPOSE
    type VARCHAR(50) NOT NULL COMMENT 'subscription | wallet_recharge | purchase | refund | others',

    -- OPTIONAL SUBSCRIPTION LINK
    plan_id INT NULL,

    -- AMOUNT DETAILS
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'INR',

    -- PAYMENT GATEWAY DETAILS
    payment_method VARCHAR(50) COMMENT 'UPI | Card | NetBanking | Wallet',
    provider VARCHAR(100) COMMENT 'Razorpay | Stripe | Paytm | Cashfree',
    transaction_ref VARCHAR(255),
    order_id VARCHAR(255),

    -- SECURITY & IDEMPOTENCY
    idempotency_key VARCHAR(100),
    verified BOOLEAN DEFAULT FALSE,
    verified_at DATETIME,
    failure_reason VARCHAR(255),

    -- STATUS
    status VARCHAR(50) NOT NULL COMMENT 'pending | success | failed | refunded',

    -- META
    ip_address VARCHAR(100),
    notes TEXT,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- CONSTRAINTS
    CONSTRAINT fk_txn_user FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY ux_gateway_txn (provider, transaction_ref),
    UNIQUE KEY ux_idempotency (idempotency_key)
);

CREATE TABLE wallet (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    -- USER LINK
    user_id BIGINT NOT NULL,

    -- ACCOUNT INFO
    account_number VARCHAR(50) UNIQUE NOT NULL,
    balance DECIMAL(15,2) DEFAULT 0.00,

    -- SECURITY
    pin_hash VARCHAR(255),
    secret_token VARCHAR(255),
    two_factor_enabled BOOLEAN DEFAULT FALSE,

    failed_attempts INT DEFAULT 0,
    last_failed_attempt DATETIME,

    -- FRAUD CONTROL
    is_frozen BOOLEAN DEFAULT FALSE,
    freeze_reason VARCHAR(255),

    daily_limit DECIMAL(15,2) DEFAULT 10000.00,
    monthly_limit DECIMAL(15,2) DEFAULT 100000.00,

    last_transaction_at DATETIME,

    -- STATUS
    status VARCHAR(20) DEFAULT 'active' COMMENT 'active | locked | closed | frozen',

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    -- CONSTRAINTS
    CONSTRAINT fk_wallet_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT chk_wallet_balance CHECK (balance >= 0)
);

CREATE TABLE user_subscriptions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,

    user_id BIGINT NOT NULL,
    plan_id INT NOT NULL,

    start_date DATETIME NOT NULL,
    end_date DATETIME NOT NULL,

    payment_status VARCHAR(50) NOT NULL COMMENT 'pending | paid | failed',
    transaction_id VARCHAR(255),

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- CONSTRAINTS
    CONSTRAINT fk_sub_user FOREIGN KEY (user_id) REFERENCES users(id),
    CONSTRAINT chk_subscription_dates CHECK (end_date > start_date)
);



CREATE INDEX idx_txn_user_status ON transactions(user_id, status);
CREATE INDEX idx_wallet_user ON wallet(user_id);
CREATE INDEX idx_active_subscription ON user_subscriptions(user_id, end_date);


CREATE TABLE subscription_plans (
    id INT PRIMARY KEY AUTO_INCREMENT,

    plan_name VARCHAR(100) NOT NULL COMMENT 'Free | Silver | Gold | Platinum',
    description TEXT,

    price DECIMAL(10,2) NOT NULL DEFAULT 0.00,

    -- OFFER DETAILS
    is_offer BOOLEAN DEFAULT FALSE,
    offer_name VARCHAR(255),
    offer_off DECIMAL(10,2),
    offer_start DATETIME,
    offer_end DATETIME,

    duration_days INT NOT NULL COMMENT '30 = monthly, 365 = yearly',

    is_active BOOLEAN DEFAULT TRUE,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

   
    CONSTRAINT chk_offer_dates CHECK (
        offer_start IS NULL OR offer_end > offer_start
    )
);

ALTER TABLE user_subscriptions
ADD CONSTRAINT fk_user_subscriptions_plan
FOREIGN KEY (plan_id)
REFERENCES subscription_plans(id)
ON DELETE RESTRICT
ON UPDATE CASCADE;

CREATE INDEX idx_active_plans ON subscription_plans(is_active);
CREATE INDEX idx_offer_dates ON subscription_plans(offer_start, offer_end);
