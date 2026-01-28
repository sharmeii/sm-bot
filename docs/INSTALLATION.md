# 📥 Installation Guide

Complete installation instructions for the Multi-Account Social Media Automation system.

---

## System Requirements

### Minimum Requirements
- **OS:** Windows 10 (64-bit) or higher
- **RAM:** 4 GB
- **Storage:** 2 GB free space
- **Internet:** Stable broadband connection

### Recommended Requirements
- **OS:** Windows 11 (64-bit)
- **RAM:** 8 GB or more
- **Storage:** 5 GB free space (for videos and cache)
- **Internet:** Stable high-speed connection

---

## Prerequisites

### 1. Python Installation

**Check if Python is installed:**
```bash
python --version
```

**If not installed:**
1. Download from https://www.python.org/downloads/
2. Download **Python 3.11.x** or **3.12.x**
3. Run installer
4. ✅ **IMPORTANT:** Check "Add Python to PATH"
5. Click "Install Now"

**Verify installation:**
```bash
python --version
pip --version
```

Should show Python 3.11+ and pip version.

### 2. PostgreSQL Installation

**Download:**
1. Go to https://www.postgresql.org/download/windows/
2. Download latest version (16.x recommended)
3. Run installer

**Installation steps:**
1. **Select Components:** 
   - ✅ PostgreSQL Server
   - ✅ pgAdmin 4
   - ✅ Command Line Tools
   - ❌ Stack Builder (optional)

2. **Data Directory:** Leave default
   ```
   C:\Program Files\PostgreSQL\16\data
   ```

3. **Password:** 
   - Create a strong password
   - **WRITE IT DOWN!** You'll need this

4. **Port:** Leave as `5432`

5. **Locale:** Leave as default

6. Finish installation (may take 5-10 minutes)

**Verify installation:**
```bash
psql --version
```

Should show: `psql (PostgreSQL) 16.x`

**First time setup:**
1. Open **pgAdmin 4** (installed with PostgreSQL)
2. It will ask for a master password (create one)
3. Click on **PostgreSQL 16** server
4. Enter the password you created during installation

### 3. BitBrowser Installation

**Download:**
1. Go to https://www.bitbrowser.net/
2. Download Windows version
3. Install BitBrowser

**Setup:**
1. Open BitBrowser
2. Create profiles for each social media account
3. For each profile:
   - Right-click → **Copy Profile ID**
   - Save these IDs (you'll need them later)

---

## Application Installation

### Step 1: Download Project

**Option A: Clone from GitHub (Recommended)**
```bash
cd C:\Users\YourName\Desktop
git clone https://github.com/yourusername/social-media-automation.git
cd social-media-automation
```

**Option B: Download ZIP**
1. Go to GitHub repository
2. Click **Code** → **Download ZIP**
3. Extract to: `C:\Users\YourName\Desktop\social-media-automation`

### Step 2: Install Python Dependencies

Open Command Prompt in project folder:

```bash
cd C:\Users\YourName\Desktop\social-media-automation
pip install -r requirements.txt
```

This installs:
- `playwright` - Browser automation
- `psycopg2-binary` - PostgreSQL connection
- `requests` - API calls to BitBrowser

**Expected output:**
```
Successfully installed playwright-1.40.0 psycopg2-binary-2.9.9 requests-2.31.0
```

### Step 3: Install Playwright Browsers

```bash
playwright install chromium
```

**Expected output:**
```
Downloading Chromium 119.0.6045.9
Chromium 119.0.6045.9 downloaded to ...
```

This downloads ~150MB.

### Step 4: Create Configuration Files

**Create database config:**
```bash
copy config\db_config.py.example config\db_config.py
```

**Edit `config\db_config.py`:**
```python
DB_HOST = "localhost"
DB_NAME = "sm_bot"
DB_USER = "postgres"
DB_PASS = "your_password_from_postgresql_install"  # ⚠️ CHANGE THIS
DB_PORT = "5432"
```

**Create application config:**
```bash
copy config\config.py.example config\config.py
```

**Edit `config\config.py`:**
```python
SHARED_ID = "your_bitbrowser_profile_id"  # ⚠️ CHANGE THIS
```

---

## Database Setup

### Step 1: Create Database

**Using pgAdmin (Easier):**
1. Open **pgAdmin 4**
2. Connect to PostgreSQL server
3. Right-click **Databases**
4. Select **Create** → **Database**
5. **Name:** `sm_bot`
6. Click **Save**

**Using Command Line:**
```bash
psql -U postgres
# Enter your password
CREATE DATABASE sm_bot;
\q
```

### Step 2: Run Setup SQL

1. Open **pgAdmin 4**
2. Click on **sm_bot** database
3. Click **Tools** → **Query Tool**
4. Open `setup/setup.sql` in a text editor
5. **Edit Section 6** with your BitBrowser Profile IDs
6. Copy entire SQL
7. Paste in Query Tool
8. Click **Execute** (▶️) or press **F5**

**Expected output:**
```
Setup completed successfully!
```

### Step 3: Verify Database

In Query Tool, run:
```sql
SELECT * FROM accounts_overview;
```

Should show your accounts listed.

---

## Verification

### Test 1: Python Imports
```bash
python -c "import playwright; import psycopg2; import requests; print('All imports OK')"
```

Should print: `All imports OK`

### Test 2: Database Connection
```bash
python -c "import psycopg2; import db_config; conn = psycopg2.connect(host=db_config.DB_HOST, database=db_config.DB_NAME, user=db_config.DB_USER, password=db_config.DB_PASS, port=db_config.DB_PORT); print('Database connected!'); conn.close()"
```

Should print: `Database connected!`

### Test 3: Add Test Video
```bash
python core/add_video.py
```

Add a test video and verify it's added.

### Test 4: View Queue
```bash
python core/view_queue.py
```

Should show your test video.

---

## Common Installation Issues

### Issue: "pip is not recognized"

**Solution:**
```bash
# Use full path
C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe -m pip install -r requirements.txt

# Or add Python to PATH:
# System Properties → Environment Variables → Path → Add Python folder
```

### Issue: "psql: command not found"

**Solution:** Add PostgreSQL to PATH
1. Search Windows for "Environment Variables"
2. Click "Environment Variables"
3. Edit "Path" under System variables
4. Add: `C:\Program Files\PostgreSQL\16\bin`
5. Restart Command Prompt

### Issue: "role 'postgres' does not exist"

**Solution:** You may have used a different username during PostgreSQL installation. Check your installation settings or recreate user:
```sql
CREATE USER postgres WITH SUPERUSER PASSWORD 'your_password';
```

### Issue: Playwright download fails

**Solution:**
```bash
# Set environment variable first
set PLAYWRIGHT_BROWSERS_PATH=C:\playwright
playwright install chromium
```

### Issue: "ModuleNotFoundError: No module named 'psycopg2'"

**Solution:**
```bash
pip install psycopg2-binary
```

### Issue: Permission denied errors

**Solution:** Run Command Prompt as Administrator
1. Right-click Command Prompt
2. Select "Run as administrator"
3. Run installation commands again

---

## Directory Structure After Installation

```
social-media-automation/
├── config/
│   ├── config.py                 ✅ Created (your settings)
│   ├── config.py.example         📄 Template
│   ├── db_config.py              ✅ Created (your DB password)
│   └── db_config.py.example      📄 Template
│
├── core/
│   ├── db_scheduler.py           📄 Main scheduler
│   ├── add_video.py              📄 Add videos
│   ├── view_queue.py             📄 View status
│   └── account_manager.py        📄 Manage accounts
│
├── bots/
│   ├── youtube_poster.py         📄 YouTube bot
│   ├── linkedin_poster.py        📄 LinkedIn bot
│   ├── tiktok_poster.py          📄 TikTok bot
│   ├── pinterest_poster.py       📄 Pinterest bot
│   └── twitter_poster.py         📄 Twitter bot
│
├── setup/
│   └── setup.sql                 📄 Database setup
│
├── docs/
│   ├── INSTALLATION.md           📄 This file
│   ├── SETUP_GUIDE.md            📄 Setup guide
│   ├── DAILY_USAGE.md            📄 Daily usage
│   └── TROUBLESHOOTING.md        📄 Fix issues
│
├── README.md                      📄 Main readme
├── requirements.txt               📄 Python packages
└── .gitignore                     📄 Git ignore file
```

---

## Next Steps

✅ **Installation Complete!**

Now proceed to:
1. [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup steps
2. [DAILY_USAGE.md](DAILY_USAGE.md) - Learn how to use daily

---

## Uninstallation

If you need to remove the system:

### 1. Remove Python Packages
```bash
pip uninstall playwright psycopg2-binary requests -y
```

### 2. Remove Database
```sql
DROP DATABASE sm_bot;
```

### 3. Delete Project Folder
```bash
rmdir /s C:\Users\YourName\Desktop\social-media-automation
```

### 4. Optional: Uninstall Software
- Uninstall PostgreSQL via Windows Settings
- Uninstall Python via Windows Settings
- Uninstall BitBrowser

---

## Getting Help

**Installation Issues?**
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Verify all prerequisites are installed
3. Check error messages carefully
4. Try running commands as Administrator

**Still stuck?**
- Review this guide step-by-step
- Check Python and PostgreSQL versions
- Verify all paths are correct
- Ensure no typos in configuration files

---

**Installation guide complete!** 🎉 Proceed to [SETUP_GUIDE.md](SETUP_GUIDE.md) for next steps.