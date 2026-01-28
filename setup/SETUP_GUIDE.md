# 🔧 Setup Guide - Multi-Account Social Media Automation

Complete step-by-step guide to get your automation system running.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:

- [ ] Windows 10/11 computer
- [ ] Python 3.8 or higher installed
- [ ] PostgreSQL 12 or higher installed
- [ ] BitBrowser installed and running
- [ ] 2+ social media accounts per platform
- [ ] Admin access to your computer

---

## Step 1: Install Python Dependencies

Open Command Prompt and run:

```bash
cd C:\Users\YourName\Desktop\social-media-automation
pip install -r requirements.txt
playwright install chromium
```

**Expected output:**
```
Successfully installed playwright-1.40.0 psycopg2-binary-2.9.9 requests-2.31.0
Chromium 119.0.6045.9 downloaded
```

**Troubleshooting:**
- If `pip` not found: Add Python to PATH or use `python -m pip`
- If permission error: Run Command Prompt as Administrator

---

## Step 2: Install and Configure PostgreSQL

### 2.1 Install PostgreSQL

1. Download from https://www.postgresql.org/download/windows/
2. Run installer
3. During installation:
   - **Port:** Leave as `5432`
   - **Password:** Create a strong password (WRITE IT DOWN!)
   - **Locale:** Leave default

4. Finish installation

### 2.2 Verify Installation

Open Command Prompt:
```bash
psql --version
```

Should show: `psql (PostgreSQL) 16.x`

### 2.3 Create Database

**Option A: Using pgAdmin (Recommended)**

1. Open **pgAdmin 4** (installed with PostgreSQL)
2. Connect to PostgreSQL (enter your password)
3. Right-click **Databases** → **Create** → **Database**
4. Name: `sm_bot`
5. Click **Save**

**Option B: Using Command Line**

```bash
psql -U postgres
# Enter password
CREATE DATABASE sm_bot;
\q
```

---

## Step 3: Configure Application Settings

### 3.1 Create Database Config

1. Copy the example file:
   ```bash
   copy config\db_config.py.example config\db_config.py
   ```

2. Edit `config\db_config.py`:
   ```python
   DB_HOST = "localhost"
   DB_NAME = "sm_bot"
   DB_USER = "postgres"
   DB_PASS = "your_actual_password_here"  # ⚠️ CHANGE THIS!
   DB_PORT = "5432"
   ```

### 3.2 Get BitBrowser Profile IDs

For **each social media account**:

1. Open **BitBrowser**
2. Find the profile for that account
3. **Right-click** on the profile
4. Select **Copy Profile ID**
5. Save it in a text file

**Example:**
```
YouTube Channel 1:    4cebbcecea9b405ab12cee77046bd3d3
YouTube Channel 2:    7afbbcecea9b405ab12cee77046bd999
Twitter @catvideos:   9dfbbcecea9b405ab12cee77046bd888
Twitter @petfunny:    2efbbcecea9b405ab12cee77046bd777
LinkedIn John:        abc123profile456xyz
LinkedIn Jane:        def789profile012xyz
TikTok @cats:         tiktok_prof_001
TikTok @pets:         tiktok_prof_002
Pinterest Cats:       pinterest_001
Pinterest Pets:       pinterest_002
```

### 3.3 Create Application Config

1. Copy the example file:
   ```bash
   copy config\config.py.example config\config.py
   ```

2. Edit `config\config.py`:
   ```python
   SHARED_ID = "4cebbcecea9b405ab12cee77046bd3d3"  # Your main profile ID
   ```

---

## Step 4: Run Database Setup SQL

### 4.1 Prepare Setup SQL

1. Open `setup/setup.sql` in a text editor
2. Find **Section 6: ADD YOUR ACCOUNTS**
3. Replace `'YOUR_PROFILE_ID_HERE'` with your actual BitBrowser Profile IDs

**Example:**
```sql
-- Before:
('YouTube Shorts', 'YouTube Account 1', 'YOUR_PROFILE_ID_HERE', TRUE),

-- After:
('YouTube Shorts', 'Cat Videos Channel', '4cebbcecea9b405ab12cee77046bd3d3', TRUE),
```

### 4.2 Execute Setup SQL

1. Open **pgAdmin 4**
2. Connect to your server
3. Click on **sm_bot** database
4. Click **Tools** → **Query Tool**
5. Copy entire contents of `setup/setup.sql`
6. Paste into Query Tool
7. Click **Execute** (▶️ button) or press **F5**

**Expected output:**
```
Setup completed successfully!
```

You should see tables created and accounts listed.

### 4.3 Verify Setup

In the same Query Tool, run:
```sql
SELECT * FROM accounts_overview;
```

Should show all your accounts with their profile IDs.

---

## Step 5: Login to All Social Media Accounts

**IMPORTANT:** You must login manually ONCE for each account!

For each BitBrowser profile:

1. Open **BitBrowser**
2. Open the profile
3. Navigate to the social media platform
4. **Login** with username/password
5. **Stay logged in** - don't log out!
6. Close the browser

The automation will use these saved sessions.

### Platforms to Login:

- [ ] YouTube Studio: `https://studio.youtube.com`
- [ ] Twitter/X: `https://x.com`
- [ ] LinkedIn: `https://www.linkedin.com`
- [ ] TikTok: `https://www.tiktok.com`
- [ ] Pinterest: `https://www.pinterest.com`

---

## Step 6: Test the Setup

### 6.1 Add a Test Video

```bash
python core/add_video.py
```

When prompted:
```
Enter full path to video file: C:\Videos\test.mp4
Enter title/caption: Test Video - Please Ignore
Enter description: Testing automation system
Enter link: (press Enter)
```

**Expected output:**
```
✅ VIDEO ADDED TO QUEUE
Job ID: #1
```

### 6.2 Check Schedules Were Created

```bash
python core/view_queue.py --upcoming
```

**Expected output:**
```
📅 UPCOMING SCHEDULED POSTS
===========================
⏰ In 15 minutes
   🎬 Job #1: Test Video
   📱 Platform: YouTube Shorts
   👤 Account: Cat Videos Channel
   🕐 Scheduled: Jan 26, 10:15 AM

⏰ In 22 minutes
   🎬 Job #1: Test Video
   📱 Platform: Twitter
   👤 Account: @catvideos
   🕐 Scheduled: Jan 26, 10:22 AM
```

You should see multiple posts scheduled!

### 6.3 Start the Scheduler

```bash
python core/db_scheduler.py
```

**Expected output:**
```
🤖 MULTI-ACCOUNT SOCIAL MEDIA SCHEDULER
========================================
Features:
  ✅ Multiple accounts per platform
  ✅ Random posting times per account
  ✅ Smart retry logic
  ✅ Auto-schedule new videos
========================================
⏰ No posts ready. Next check in 5 minutes...
```

Let it run until at least one post is made.

### 6.4 Verify First Post

After the first scheduled time passes:

```bash
python core/view_queue.py
```

Should show at least one ✅ posted.

---

## Step 7: Configure Posting Times (Optional)

If you want to customize when posts happen:

```sql
-- All platforms: 8 AM to 6 PM
UPDATE platform_windows 
SET min_hour = 8, max_hour = 18;

-- YouTube mornings only
UPDATE platform_windows 
SET min_hour = 8, max_hour = 12
WHERE platform = 'YouTube Shorts';

-- TikTok evenings only
UPDATE platform_windows 
SET min_hour = 17, max_hour = 23
WHERE platform = 'TikTok';
```

---

## Step 8: Setup Auto-Start (Optional)

To run the scheduler automatically when Windows starts:

1. Create `start_scheduler.bat`:
   ```batch
   @echo off
   cd C:\Users\YourName\Desktop\social-media-automation
   python core/db_scheduler.py
   pause
   ```

2. Press `Win + R`
3. Type: `shell:startup`
4. Copy `start_scheduler.bat` into that folder

Now the scheduler starts automatically when you login!

---

## Verification Checklist

Before going live with real content:

- [ ] PostgreSQL running (check Services)
- [ ] Database `sm_bot` created
- [ ] Tables created successfully
- [ ] All accounts added to database
- [ ] BitBrowser Profile IDs correct
- [ ] Logged into all social media accounts
- [ ] Test video added successfully
- [ ] Schedules created (10+ posts)
- [ ] Scheduler started successfully
- [ ] At least one test post succeeded
- [ ] Can see status with `view_queue.py`

---

## Common Setup Issues

### Issue: "psql: command not found"
PostgreSQL not in PATH. Use full path:
```bash
"C:\Program Files\PostgreSQL\16\bin\psql" -U postgres
```

### Issue: "role 'postgres' does not exist"
During installation, you set a different user. Check PostgreSQL installer settings.

### Issue: "database sm_bot does not exist"
You skipped Step 2.3. Create the database in pgAdmin.

### Issue: "No module named 'playwright'"
```bash
pip install -r requirements.txt
```

### Issue: "YOUR_PROFILE_ID_HERE in accounts"
You forgot to edit Section 6 in `setup.sql` with real profile IDs.

### Issue: Accounts show but scheduler doesn't post
Check BitBrowser is running and profiles are logged in.

---

## Next Steps

✅ **Setup Complete!** 

Now read:
- [DAILY_USAGE.md](DAILY_USAGE.md) - How to use daily
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Fix common issues
- [FAQ.md](FAQ.md) - Frequently asked questions

---

## Need Help?

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Run: `python core/view_queue.py --stats`
3. Check error screenshots in your folder
4. Review SQL query results in pgAdmin

---

**Setup completed!** 🎉 You're ready to automate your social media! 🚀