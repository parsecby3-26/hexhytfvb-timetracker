-- Comprehensive Supabase Database Migration
-- Run this in Supabase SQL Editor to ensure all tables have the correct schema
-- This file contains all necessary ALTER TABLE statements

-- =========================================
-- Users Table - Add Missing Columns
-- =========================================
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_reset_token_expires TIMESTAMP;

-- Verify users table has all required columns
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- =========================================
-- Time Entries Table - Verify Structure
-- =========================================
-- These should already exist from 0001_initial_migration.py
-- But this verifies they are present
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'time_entries' 
ORDER BY ordinal_position;

-- =========================================
-- Projects Table - Verify Structure
-- =========================================
SELECT column_name, data_type, is_nullable
FROM information_schema.columns 
WHERE table_name = 'projects' 
ORDER BY ordinal_position;
