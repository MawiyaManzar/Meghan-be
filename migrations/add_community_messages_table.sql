-- Migration: Add community_messages table
-- This table stores real-time community chat messages (Discord-style)

-- Create community_messages table
CREATE TABLE IF NOT EXISTS community_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    community_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES problem_communities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Create indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_community_messages_community_id ON community_messages(community_id);
CREATE INDEX IF NOT EXISTS idx_community_messages_user_id ON community_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_community_messages_created_at ON community_messages(created_at);
