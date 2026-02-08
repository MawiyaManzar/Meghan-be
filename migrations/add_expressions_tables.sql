-- Migration: Add MicroExpression and EmpathyResponse tables
-- Run this script to add the new tables for Task 6: Micro Expressions Feature

-- Create micro_expressions table
CREATE TABLE IF NOT EXISTS micro_expressions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    community_id INTEGER,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (community_id) REFERENCES problem_communities(id) ON DELETE SET NULL
);

-- Create index on created_at for faster queries
CREATE INDEX IF NOT EXISTS idx_micro_expressions_created_at ON micro_expressions(created_at);

-- Create index on user_id for faster user queries
CREATE INDEX IF NOT EXISTS idx_micro_expressions_user_id ON micro_expressions(user_id);

-- Create index on community_id for faster community filtering
CREATE INDEX IF NOT EXISTS idx_micro_expressions_community_id ON micro_expressions(community_id);

-- Create empathy_responses table
CREATE TABLE IF NOT EXISTS empathy_responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expression_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expression_id) REFERENCES micro_expressions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create index on created_at for faster queries
CREATE INDEX IF NOT EXISTS idx_empathy_responses_created_at ON empathy_responses(created_at);

-- Create index on expression_id for faster expression queries
CREATE INDEX IF NOT EXISTS idx_empathy_responses_expression_id ON empathy_responses(expression_id);

-- Create index on user_id for faster user queries
CREATE INDEX IF NOT EXISTS idx_empathy_responses_user_id ON empathy_responses(user_id);
