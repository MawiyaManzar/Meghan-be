-- Add persisted weekly insight table for A4 schema alignment.
-- Safe to re-run due IF NOT EXISTS clauses.

CREATE TABLE IF NOT EXISTS weekly_wellbeing_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    summary_text TEXT NOT NULL,
    risk_tier VARCHAR NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_weekly_wellbeing_insights_user_id
    ON weekly_wellbeing_insights(user_id);

CREATE INDEX IF NOT EXISTS idx_weekly_wellbeing_insights_week_start
    ON weekly_wellbeing_insights(week_start);
