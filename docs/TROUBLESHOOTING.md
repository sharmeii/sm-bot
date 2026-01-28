# 🔧 Troubleshooting Guide

Solutions to common problems with the Multi-Account Social Media Automation system.

---

## 🚨 Quick Fixes

Try these first before diving into specific issues:

```bash
# 1. Reset browser
python force_reset.py

# 2. Check status
python core/view_queue.py --stats

# 3. View recent errors
```

```sql
SELECT platform, account_name, error_message, retry_count
FROM platform_schedules ps
JOIN social_accounts sa ON ps.account_id = sa.id
WHERE retry_count > 0
ORDER BY ps.scheduled_time DESC
LIMIT 10;
```

---

## 🗄️ Database Issues

### ❌ "Database connection failed"

**Symptoms:**
- Error when running any script
- "could not connect to server"

**Solutions:**

1. **Check PostgreSQL is running:**
   ```
   Services → PostgreSQL → Status should be "Running"
   ```

2. **Verify credentials in `db_config.py`:**
   ```python
   DB_PASS = "your_actual_password"  # Check this!
   ```

3. **Test connection:**
   ```bash
   psql -U postgres -d sm_bot
   # If this fails, password is wrong
   ```

4. **Check port:**
   ```bash
   netstat -an | findstr 5432
   # Should show PostgreSQL listening
   ```

---

### ❌ "relation 'social_accounts' does not exist"

**Cause:** Database tables not created

**Solution:**
```bash
# Run setup SQL in pgAdmin
# Open setup/setup.sql and execute it
```

---

### ❌ "column 'posted_youtube' does not exist"

**Cause:** Using old files with new database (or vice versa)

**Solution:**

**If you have old database, run migration:**
```bash
# In pgAdmin, run sql/migration.sql
```

**If fresh install:**
```bash
# Ensure you're using the updated files
# Replace view_queue.py with multi-account version
```

---

## 🌐 Browser Issues

### ❌ "Browser already open"

**Cause:** BitBrowser profile is still running from previous session

**Solutions:**

1. **Force reset:**
   ```bash
   python force_reset.py
   ```

2. **Manual fix:**
   - Open BitBrowser
   - Close all profiles
   - Wait 10 seconds
   - Try again

3. **Restart BitBrowser:**
   - Close BitBrowser completely
   - Reopen it
   - Run script again

---

### ❌ "Could not connect to BitBrowser"

**Symptoms:**
- "Connection Error"
- "BitBrowser Failed"

**Solutions:**

1. **Check BitBrowser is running:**
   - Open BitBrowser application
   - Should see it in system tray

2. **Verify API URL:**
   ```python
   # In config.py
   API_URL = "http://127.0.0.1:54345"  # Check port
   ```

3. **Check firewall:**
   - Allow BitBrowser through Windows Firewall
   - Try temporarily disabling antivirus

---

### ❌ "Profile not found"

**Cause:** Wrong BitBrowser Profile ID in database

**Solution:**

1. **Get correct Profile ID:**
   - Open BitBrowser
   - Right-click profile
   - Copy Profile ID

2. **Update database:**
   ```sql
   UPDATE social_accounts 
   SET bitbrowser_profile_id = 'correct_id_here'
   WHERE id = 5;
   ```

3. **Verify:**
   ```bash
   python core/view_queue.py --accounts
   ```

---

## 🤖 Posting Issues

### ❌ Posts stuck "Pending"

**Symptoms:**
- Scheduled time passed
- Still showing ⏳ in status
- Not posted yet

**Solutions:**

1. **Check scheduler is running:**
   ```bash
   # Should see output every 5 minutes
   python core/db_scheduler.py
   ```

2. **Check scheduled times:**
   ```bash
   python core/view_queue.py --upcoming
   ```
   
   If times are in the future, wait for them.

3. **Check account is enabled:**
   ```sql
   SELECT account_name, enabled FROM social_accounts;
   ```
   
   Enable if disabled:
   ```sql
   UPDATE social_accounts SET enabled = TRUE WHERE id = 5;
   ```

4. **Check session expired:**
   - Open BitBrowser
   - Open profile
   - Check if still logged into platform
   - Re-login if needed

---

### ❌ Post failed with error

**Check error message:**

```bash
python core/view_queue.py
```

Or SQL:
```sql
SELECT error_message FROM platform_schedules WHERE retry_count > 0;
```

**Common errors:**

| Error Message | Cause | Solution |
|--------------|-------|----------|
| "timeout" | Page took too long | Retry or check internet |
| "selector not found" | Platform UI changed | Wait for bot update |
| "file not found" | Wrong video path | Fix path in database |
| "login required" | Session expired | Re-login in BitBrowser |

---

### ❌ Some accounts post, others don't

**Diagnosis:**

```sql
SELECT 
    sa.account_name,
    COUNT(*) FILTER (WHERE ps.posted = TRUE) as success,
    COUNT(*) FILTER (WHERE ps.posted = FALSE) as failed
FROM platform_schedules ps
JOIN social_accounts sa ON ps.account_id = sa.id
GROUP BY sa.account_name
ORDER BY failed DESC;
```

**Solutions:**

1. **Re-login to failed accounts:**
   - Open BitBrowser
   - Open that account's profile
   - Navigate to platform
   - Re-login

2. **Check profile ID is correct:**
   ```sql
   SELECT * FROM social_accounts WHERE account_name = 'failing_account';
   ```

3. **Test manually:**
   - Open that profile in BitBrowser
   - Try posting manually
   - If manual works, bot should too

---

## ⏰ Scheduling Issues

### ❌ All posts schedule for tomorrow

**Cause:** Posting window has passed for today

**Solution:**

```sql
-- Set to post rest of today
UPDATE platform_windows 
SET min_hour = EXTRACT(HOUR FROM NOW())::INTEGER,
    max_hour = 23;

-- Delete bad schedules
DELETE FROM platform_schedules WHERE posted = FALSE;

-- Restart scheduler to regenerate
```

---

### ❌ Posts too close together

**Symptom:** All posts within 30 minutes

**Solution:**

```sql
-- Increase spacing
UPDATE platform_windows 
SET min_delay_minutes = 60,
    max_delay_minutes = 240;

-- Delete and regenerate
DELETE FROM platform_schedules WHERE posted = FALSE;
```

---

### ❌ No schedules created

**Diagnosis:**

```sql
SELECT COUNT(*) FROM platform_schedules;
-- Should be: (number of videos) × (number of accounts)
```

**If 0:**

```bash
# Check accounts exist
python core/view_queue.py --accounts

# If no accounts, add them
python core/account_manager.py
```

**If accounts exist but no schedules:**

```bash
# Start scheduler - it auto-creates schedules
python core/db_scheduler.py
```

---

## 💻 Script Errors

### ❌ "No module named 'playwright'"

**Solution:**
```bash
pip install playwright psycopg2-binary requests
playwright install chromium
```

---

### ❌ "No module named 'db_config'"

**Cause:** Running script from wrong directory

**Solution:**
```bash
# Always run from project root
cd C:\Users\YourName\Desktop\social-media-automation
python core/add_video.py
```

---

### ❌ Import errors in Python scripts

**Solution:**

Make sure all files are in same directory (don't organize into subfolders unless you update imports).

---

## 📁 File Issues

### ❌ "File not found" when adding video

**Solutions:**

1. **Check path is correct:**
   ```bash
   dir "C:\Videos\my_video.mp4"
   ```

2. **Use full path, not relative:**
   ```
   ❌ Wrong: Videos\video.mp4
   ✅ Correct: C:\Users\YourName\Videos\video.mp4
   ```

3. **Check for quotes in path:**
   ```sql
   -- If path has quotes, remove them
   UPDATE social_queue 
   SET video_path = REPLACE(video_path, '"', '')
   WHERE id = 5;
   ```

---

### ❌ Video plays but doesn't upload

**Possible causes:**

1. **Video format not supported:**
   - Convert to MP4 H.264
   - Use HandBrake or similar tool

2. **File too large:**
   - YouTube: Max 256 GB (but <15 GB recommended)
   - TikTok: Max 287.6 MB
   - Twitter: Max 512 MB

3. **File corrupted:**
   - Try playing in VLC
   - Re-export if corrupted

---

## 🔐 Account Issues

### ❌ Account keeps logging out

**Solutions:**

1. **In BitBrowser, enable:**
   - Save cookies
   - Save session
   - Don't clear cache

2. **Check "Remember me"** when logging in

3. **Disable 2FA** (or use 2FA in BitBrowser profile)

---

### ❌ "Account suspended" or "Action blocked"

**Cause:** Platform detected automation or policy violation

**Solutions:**

1. **Reduce posting frequency:**
   ```sql
   UPDATE platform_windows 
   SET min_delay_minutes = 120,
       max_delay_minutes = 480;
   ```

2. **Reduce number of accounts**

3. **Check platform policies:**
   - No copyrighted content
   - Follow community guidelines
   - Don't spam

4. **Appeal to platform** if wrongly suspended

---

## 💾 Performance Issues

### ❌ Scheduler is slow

**Solutions:**

1. **Check disk space:**
   ```bash
   # Need at least 2 GB free
   ```

2. **Close unnecessary programs**

3. **Add more RAM** (8 GB+ recommended)

4. **Check CPU usage in Task Manager**

---

### ❌ Database queries slow

**Solutions:**

```sql
-- Rebuild indexes
REINDEX DATABASE sm_bot;

-- Vacuum database
VACUUM ANALYZE;

-- Delete old data
DELETE FROM social_queue 
WHERE created_at < NOW() - INTERVAL '60 days';
```

---

## 🖼️ Error Screenshots

The system saves screenshots when errors occur:

```
yt_error.png       - YouTube errors
linkedin_error.png - LinkedIn errors
tiktok_error.png   - TikTok errors
pinterest_error.png - Pinterest errors
twitter_error.png  - Twitter errors
```

**How to use them:**

1. Open the screenshot
2. Look for error messages on screen
3. Check if login page (session expired)
4. Check if error popup

---

## 🔄 Reset Everything

### Nuclear Option: Fresh Start

**⚠️ This deletes all data!**

```sql
-- Backup first!
-- pg_dump -U postgres sm_bot > backup.sql

-- Delete all data
DELETE FROM platform_schedules;
DELETE FROM social_queue;
DELETE FROM social_accounts;

-- Reset ID counters
ALTER SEQUENCE social_queue_id_seq RESTART WITH 1;
ALTER SEQUENCE social_accounts_id_seq RESTART WITH 1;
ALTER SEQUENCE platform_schedules_id_seq RESTART WITH 1;

-- Re-add accounts
-- (run your account setup again)
```

---

## 📞 Getting Help

### Before asking for help:

1. ✅ Check this troubleshooting guide
2. ✅ Check [FAQ.md](FAQ.md)
3. ✅ Run diagnostic commands
4. ✅ Check error screenshots
5. ✅ Try the quick fixes at top

### When reporting issues, include:

```bash
# 1. Python version
python --version

# 2. Error message (full text)

# 3. What you were doing

# 4. Screenshots if relevant

# 5. Database stats
python core/view_queue.py --stats

# 6. Accounts status
python core/view_queue.py --accounts
```

---

## 🛠️ Diagnostic Commands

### Check Everything

```bash
# Python environment
python --version
pip list

# Database connection
python -c "import psycopg2; import db_config; conn = psycopg2.connect(host=db_config.DB_HOST, database=db_config.DB_NAME, user=db_config.DB_USER, password=db_config.DB_PASS); print('DB OK')"

# Files exist
dir config\config.py
dir config\db_config.py

# Stats
python core/view_queue.py --stats
```

### Database Health Check

```sql
-- Table row counts
SELECT 
    'Videos' as table_name, COUNT(*) as rows FROM social_queue
UNION ALL
SELECT 'Accounts', COUNT(*) FROM social_accounts
UNION ALL
SELECT 'Schedules', COUNT(*) FROM platform_schedules;

-- Recent errors
SELECT * FROM platform_schedules 
WHERE error_message IS NOT NULL 
ORDER BY id DESC LIMIT 5;

-- Pending vs completed
SELECT 
    posted,
    COUNT(*) as count
FROM platform_schedules
GROUP BY posted;
```

---

**Troubleshooting guide complete!** 🎉

Still stuck? Check [FAQ.md](FAQ.md) for more answers.