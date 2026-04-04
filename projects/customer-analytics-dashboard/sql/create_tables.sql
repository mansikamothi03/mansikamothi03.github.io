-- Customer Analytics Dashboard - Database Schema

CREATE TABLE customers (
    customer_id     SERIAL PRIMARY KEY,
    email           VARCHAR(255) UNIQUE NOT NULL,
    name            VARCHAR(255),
    signup_date     DATE NOT NULL,
    plan_type       VARCHAR(50),
    country         VARCHAR(100),
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE events (
    event_id        SERIAL PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(customer_id),
    event_type      VARCHAR(100) NOT NULL,
    event_date      TIMESTAMP NOT NULL,
    page            VARCHAR(255),
    session_id      VARCHAR(100),
    properties      JSONB
);

CREATE TABLE subscriptions (
    subscription_id SERIAL PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(customer_id),
    plan_type       VARCHAR(50),
    start_date      DATE NOT NULL,
    end_date        DATE,
    mrr             DECIMAL(10,2),
    status          VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE churn_predictions (
    prediction_id   SERIAL PRIMARY KEY,
    customer_id     INTEGER REFERENCES customers(customer_id),
    churn_score     DECIMAL(5,4),
    predicted_at    TIMESTAMP DEFAULT NOW(),
    features        JSONB
);

-- Indexes for performance
CREATE INDEX idx_events_customer_id ON events(customer_id);
CREATE INDEX idx_events_event_date ON events(event_date);
CREATE INDEX idx_subscriptions_customer_id ON subscriptions(customer_id);
CREATE INDEX idx_churn_customer_id ON churn_predictions(customer_id);