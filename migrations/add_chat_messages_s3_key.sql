-- Add optional S3 object key reference for voice/media-backed chat messages.
--
-- SQLite:
--   sqlite3 meghan.db < migrations/add_chat_messages_s3_key.sql
--
-- PostgreSQL:
--   psql "$DATABASE_URL" -f migrations/add_chat_messages_s3_key.sql

ALTER TABLE chat_messages
ADD COLUMN s3_key VARCHAR;
