-- Migration: Add mode column to conversations table
-- Allows Talk vs Plan mode differentiation for chat conversations
-- Run: sqlite3 meghan.db < migrations/add_conversation_mode.sql

ALTER TABLE conversations ADD COLUMN mode TEXT DEFAULT 'talk';

-- Backfill existing rows to ensure they have the default mode
UPDATE conversations SET mode = 'talk' WHERE mode IS NULL;
