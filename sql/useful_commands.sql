-- See all pending posts
SELECT * FROM pending_posts;

-- Count accounts
SELECT platform, COUNT(*) FROM social_accounts GROUP BY platform;

-- Reset all schedules
DELETE FROM platform_schedules WHERE posted = FALSE;

-- See errors
SELECT platform, error_message FROM platform_schedules WHERE retry_count > 0;