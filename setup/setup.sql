-- ====================================================================
-- MULTI-ACCOUNT SOCIAL MEDIA AUTOMATION - COMPLETE SETUP
-- ====================================================================
-- Run this ONCE in pgAdmin to setup everything
--
-- BEFORE RUNNING:
-- 1. Create database 'sm_bot' in pgAdmin
-- 2. Edit section 6 below with YOUR BitBrowser Profile IDs
-- 3. Execute this entire script
-- ====================================================================

-- 1. CREATE MAIN TABLES
-- ====================================================================

-- Video queue table
CREATE TABLE IF NOT EXISTS social_queue (
    id SERIAL PRIMARY KEY,
    video_path TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    link TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

-- Social media accounts table
CREATE TABLE IF NOT EXISTS social_accounts (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) NOT NULL,
    account_name VARCHAR(100) NOT NULL,
    bitbrowser_profile_id VARCHAR(100) NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, account_name)
);

-- Platform schedules table (tracks posting per account)
CREATE TABLE IF NOT EXISTS platform_schedules (
    id SERIAL PRIMARY KEY,
    queue_id INTEGER REFERENCES social_queue(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES social_accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50) NOT NULL,
    scheduled_time TIMESTAMP NOT NULL,
    posted BOOLEAN DEFAULT FALSE,
    posted_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    UNIQUE(queue_id, account_id)
);

-- Platform posting windows configuration
CREATE TABLE IF NOT EXISTS platform_windows (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) UNIQUE NOT NULL,
    min_hour INTEGER NOT NULL CHECK (min_hour >= 0 AND min_hour < 24),
    max_hour INTEGER NOT NULL CHECK (max_hour >= 0 AND max_hour < 24),
    min_delay_minutes INTEGER DEFAULT 30,
    max_delay_minutes INTEGER DEFAULT 180,
    enabled BOOLEAN DEFAULT TRUE
);

-- 2. CREATE INDEXES FOR PERFORMANCE
-- ====================================================================

CREATE INDEX IF NOT EXISTS idx_platform_schedules_posted 
ON platform_schedules(posted, scheduled_time);

CREATE INDEX IF NOT EXISTS idx_platform_schedules_account 
ON platform_schedules(account_id);

CREATE INDEX IF NOT EXISTS idx_social_accounts_platform 
ON social_accounts(platform, enabled);

-- 3. INSERT PLATFORM SETTINGS (9 AM - 5 PM DEFAULT)
-- ====================================================================

INSERT INTO platform_windows (platform, min_hour, max_hour, min_delay_minutes, max_delay_minutes) 
VALUES 
    ('YouTube Shorts', 9, 17, 30, 180),
    ('LinkedIn Video', 9, 17, 30, 180),
    ('TikTok', 9, 17, 30, 180),
    ('Pinterest Idea', 9, 17, 30, 180),
    ('Twitter', 9, 17, 30, 180)
ON CONFLICT (platform) 
DO UPDATE SET 
    min_hour = EXCLUDED.min_hour,
    max_hour = EXCLUDED.max_hour,
    min_delay_minutes = EXCLUDED.min_delay_minutes,
    max_delay_minutes = EXCLUDED.max_delay_minutes;

-- 4. CREATE HELPFUL VIEWS
-- ====================================================================

-- View to see all accounts with stats
CREATE OR REPLACE VIEW accounts_overview AS
SELECT 
    sa.id,
    sa.platform,
    sa.account_name,
    sa.bitbrowser_profile_id,
    sa.enabled,
    COUNT(ps.id) FILTER (WHERE ps.posted = TRUE) as posts_made,
    COUNT(ps.id) FILTER (WHERE ps.posted = FALSE) as posts_pending
FROM social_accounts sa
LEFT JOIN platform_schedules ps ON sa.id = ps.account_id
GROUP BY sa.id, sa.platform, sa.account_name, sa.bitbrowser_profile_id, sa.enabled
ORDER BY sa.platform, sa.account_name;

-- View to see pending posts ready to post now
CREATE OR REPLACE VIEW pending_posts AS
SELECT 
    ps.id,
    sq.id as video_id,
    sq.title,
    sa.platform,
    sa.account_name,
    sa.bitbrowser_profile_id,
    ps.scheduled_time,
    ps.retry_count
FROM platform_schedules ps
JOIN social_queue sq ON ps.queue_id = sq.id
JOIN social_accounts sa ON ps.account_id = sa.id
WHERE ps.posted = FALSE 
    AND ps.scheduled_time <= NOW()
    AND sa.enabled = TRUE
ORDER BY ps.scheduled_time ASC;

-- View to see queue status by account
CREATE OR REPLACE VIEW queue_status_by_account AS
SELECT 
    sq.id as video_id,
    sq.title,
    sa.platform,
    sa.account_name,
    ps.posted,
    ps.scheduled_time
FROM social_queue sq
CROSS JOIN social_accounts sa
LEFT JOIN platform_schedules ps ON sq.id = ps.queue_id AND sa.id = ps.account_id
WHERE sa.enabled = TRUE
ORDER BY sq.id, sa.platform, sa.account_name;

-- 5. CREATE USEFUL FUNCTIONS
-- ====================================================================

-- Function to get posting stats
CREATE OR REPLACE FUNCTION get_posting_stats()
RETURNS TABLE (
    stat_name TEXT,
    stat_value BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 'Total Videos'::TEXT, COUNT(*)::BIGINT FROM social_queue
    UNION ALL
    SELECT 'Total Accounts'::TEXT, COUNT(*)::BIGINT FROM social_accounts WHERE enabled = TRUE
    UNION ALL
    SELECT 'Posts Completed'::TEXT, COUNT(*)::BIGINT FROM platform_schedules WHERE posted = TRUE
    UNION ALL
    SELECT 'Posts Pending'::TEXT, COUNT(*)::BIGINT FROM platform_schedules WHERE posted = FALSE
    UNION ALL
    SELECT 'Posts Due Now'::TEXT, COUNT(*)::BIGINT FROM platform_schedules 
        WHERE posted = FALSE AND scheduled_time <= NOW();
END;
$$ LANGUAGE plpgsql;

-- 6. ADD YOUR ACCOUNTS
-- ====================================================================
-- ⚠️ IMPORTANT: EDIT THIS SECTION WITH YOUR ACTUAL PROFILE IDs!
-- 
-- How to get Profile IDs:
-- 1. Open BitBrowser
-- 2. Right-click each profile → Copy Profile ID
-- 3. Replace 'YOUR_PROFILE_ID_HERE' below
-- ====================================================================

-- YouTube Accounts
INSERT INTO social_accounts (platform, account_name, bitbrowser_profile_id, enabled)
VALUES 
    ('YouTube Shorts', 'YouTube Account 1', 'YOUR_PROFILE_ID_HERE', TRUE),
    ('YouTube Shorts', 'YouTube Account 2', 'YOUR_PROFILE_ID_HERE', TRUE)
ON CONFLICT (platform, account_name) 
DO UPDATE SET bitbrowser_profile_id = EXCLUDED.bitbrowser_profile_id;

-- Twitter Accounts
INSERT INTO social_accounts (platform, account_name, bitbrowser_profile_id, enabled)
VALUES 
    ('Twitter', 'Twitter Account 1', 'YOUR_PROFILE_ID_HERE', TRUE),
    ('Twitter', 'Twitter Account 2', 'YOUR_PROFILE_ID_HERE', TRUE)
ON CONFLICT (platform, account_name) 
DO UPDATE SET bitbrowser_profile_id = EXCLUDED.bitbrowser_profile_id;

-- LinkedIn Accounts
INSERT INTO social_accounts (platform, account_name, bitbrowser_profile_id, enabled)
VALUES 
    ('LinkedIn Video', 'LinkedIn Account 1', 'YOUR_PROFILE_ID_HERE', TRUE),
    ('LinkedIn Video', 'LinkedIn Account 2', 'YOUR_PROFILE_ID_HERE', TRUE)
ON CONFLICT (platform, account_name) 
DO UPDATE SET bitbrowser_profile_id = EXCLUDED.bitbrowser_profile_id;

-- TikTok Accounts
INSERT INTO social_accounts (platform, account_name, bitbrowser_profile_id, enabled)
VALUES 
    ('TikTok', 'TikTok Account 1', 'YOUR_PROFILE_ID_HERE', TRUE),
    ('TikTok', 'TikTok Account 2', 'YOUR_PROFILE_ID_HERE', TRUE)
ON CONFLICT (platform, account_name) 
DO UPDATE SET bitbrowser_profile_id = EXCLUDED.bitbrowser_profile_id;

-- Pinterest Accounts
INSERT INTO social_accounts (platform, account_name, bitbrowser_profile_id, enabled)
VALUES 
    ('Pinterest Idea', 'Pinterest Account 1', 'YOUR_PROFILE_ID_HERE', TRUE),
    ('Pinterest Idea', 'Pinterest Account 2', 'YOUR_PROFILE_ID_HERE', TRUE)
ON CONFLICT (platform, account_name) 
DO UPDATE SET bitbrowser_profile_id = EXCLUDED.bitbrowser_profile_id;

-- 7. VERIFY SETUP
-- ====================================================================

-- Show setup summary
SELECT 'Setup completed successfully!' as status;

-- Show all tables created
SELECT 
    schemaname,
    tablename,
    CASE 
        WHEN tablename = 'social_queue' THEN 'Stores videos to post'
        WHEN tablename = 'social_accounts' THEN 'Stores your accounts'
        WHEN tablename = 'platform_schedules' THEN 'Tracks posting schedules'
        WHEN tablename = 'platform_windows' THEN 'Posting time windows'
    END as description
FROM pg_tables
WHERE schemaname = 'public' 
    AND tablename IN ('social_queue', 'social_accounts', 'platform_schedules', 'platform_windows')
ORDER BY tablename;

-- Show accounts added
SELECT 
    platform,
    account_name,
    LEFT(bitbrowser_profile_id, 20) || '...' as profile_id,
    CASE WHEN enabled THEN '✅ Active' ELSE '⏸️  Disabled' END as status
FROM social_accounts
ORDER BY platform, account_name;

-- Show platform settings
SELECT 
    platform,
    LPAD(min_hour::TEXT, 2, '0') || ':00 - ' || LPAD(max_hour::TEXT, 2, '0') || ':00' as posting_window,
    min_delay_minutes || ' - ' || max_delay_minutes || ' min' as random_delay,
    CASE WHEN enabled THEN '✅ Active' ELSE '⏸️  Disabled' END as status
FROM platform_windows
ORDER BY platform;

-- Show quick stats
SELECT * FROM get_posting_stats();

-- ====================================================================
-- SETUP COMPLETE!
-- ====================================================================
-- 
-- ⚠️ BEFORE RUNNING THE BOT:
-- 1. Make sure you edited section 6 with your BitBrowser Profile IDs
-- 2. Login to each account in BitBrowser (one time)
-- 3. Verify accounts show above with correct profile IDs
--
-- NEXT STEPS:
-- 1. Add a video: python add_video.py
-- 2. Start scheduler: python db_scheduler.py
-- 3. Check status: python view_queue.py
--
-- USEFUL COMMANDS:
-- - View accounts: python view_queue.py --accounts
-- - View upcoming: python view_queue.py --upcoming
-- - View stats: python view_queue.py --stats
-- - Manage accounts: python account_manager.py
-- ====================================================================