# 📅 Daily Usage Guide

How to use the Multi-Account Social Media Automation system every day.

---

## ⏰ Daily Workflow (2-5 Minutes)

### Morning Routine

**Step 1: Add Today's Video (30 seconds)**

```bash
python core/add_video.py
```

Follow the prompts:
```
Enter full path to video file: C:\Videos\todays_video.mp4
Enter title/caption: Amazing Cat Does Tricks! 🐱
Enter description: Watch this! #cats #amazing #shorts
Enter link: (press Enter to skip)
```

**Step 2: Start the Scheduler (10 seconds)**

```bash
python core/db_scheduler.py
```

**Step 3: Let it run!** ☕

The system will automatically:
- Post to all your accounts
- At different random times throughout the day
- With human-like delays between posts

---

## 📊 Monitoring (Optional)

### Check Current Status

```bash
python core/view_queue.py
```

**Output:**
```
📊 SOCIAL MEDIA QUEUE STATUS
============================
🎬 Job #5: Amazing Cat Does Tricks!
   📊 Progress: 6/10 accounts posted
   Status by Account:

      YouTube Shorts:
         • Cat Videos Channel: ✅ Posted
         • Pet Fun Channel: ⏳ Scheduled 2:15 PM

      Twitter:
         • @catvideos: ✅ Posted
         • @petfunny: ✅ Posted

      LinkedIn:
         • John Smith: ✅ Posted
         • Jane Doe: ⏳ Scheduled 3:45 PM
```

### See What's Coming Up

```bash
python core/view_queue.py --upcoming
```

**Output:**
```
📅 UPCOMING SCHEDULED POSTS
===========================
⏰ In 15 minutes
   🎬 Job #5: Amazing Cat Does Tricks!
   📱 Platform: YouTube Shorts
   👤 Account: Pet Fun Channel
   🕐 Scheduled: Jan 26, 02:15 PM

⏰ In 2 hours
   🎬 Job #5: Amazing Cat Does Tricks!
   📱 Platform: LinkedIn Video
   👤 Account: Jane Doe
   🕐 Scheduled: Jan 26, 03:45 PM
```

### View Statistics

```bash
python core/view_queue.py --stats
```

**Output:**
```
📈 STATISTICS
=============
Total Videos:        5
Total Accounts:      10
Possible Posts:      50
Completed Posts:     42
Pending Posts:       8
Due in Next Hour:    2
```

---

## 🎥 Adding Videos

### Method 1: Interactive (Recommended)

```bash
python core/add_video.py
```

**Best for:** Adding 1-3 videos quickly

### Method 2: Batch SQL

Open pgAdmin → Query Tool:

```sql
INSERT INTO social_queue (video_path, title, description)
VALUES 
    ('C:\Videos\monday.mp4', 'Monday Motivation! 💪', '#motivation #monday'),
    ('C:\Videos\tuesday.mp4', 'Tutorial Tuesday! 🎓', '#tutorial #learning'),
    ('C:\Videos\wednesday.mp4', 'Wisdom Wednesday! 🧠', '#wisdom #tips');
```

**Best for:** Adding 5+ videos at once

### Method 3: Prepare Night Before

Add videos the night before:

```sql
INSERT INTO social_queue (video_path, title, description)
VALUES ('C:\Videos\tomorrow.mp4', 'Tomorrows Video!', 'Content here');
```

The scheduler will automatically create schedules for tomorrow.

---

## 🛑 Stopping the Scheduler

### Normal Stop

In the terminal where `db_scheduler.py` is running:

**Press `Ctrl + C`**

**Output:**
```
^C
Scheduler stopped.
```

### Force Stop

If `Ctrl + C` doesn't work:

1. **Close the terminal window**
2. Or open Task Manager (`Ctrl + Shift + Esc`)
3. Find **Python**
4. Click **End Task**

---

## 📱 Managing Accounts

### View All Accounts

```bash
python core/view_queue.py --accounts
```

Or:

```bash
python core/account_manager.py
```

Select option `2`

### Add New Account

```bash
python core/account_manager.py
```

1. Select option `1`
2. Choose platform
3. Enter account name
4. Enter BitBrowser Profile ID
5. Confirm

### Temporarily Disable Account

**Option A: Interactive**
```bash
python core/account_manager.py
```
Select option `3`

**Option B: SQL**
```sql
UPDATE social_accounts SET enabled = FALSE WHERE id = 5;
```

### Re-enable Account

```sql
UPDATE social_accounts SET enabled = TRUE WHERE id = 5;
```

---

## 🎯 Common Daily Tasks

### Check Last Posted Time

```sql
SELECT 
    sa.account_name,
    sa.platform,
    MAX(ps.posted_at) as last_post
FROM platform_schedules ps
JOIN social_accounts sa ON ps.account_id = sa.id
WHERE ps.posted = TRUE
GROUP BY sa.account_name, sa.platform
ORDER BY last_post DESC;
```

### See Today's Posts

```sql
SELECT 
    sq.title,
    sa.platform,
    sa.account_name,
    ps.posted,
    TO_CHAR(ps.scheduled_time, 'HH12:MI AM') as time
FROM platform_schedules ps
JOIN social_queue sq ON ps.queue_id = sq.id
JOIN social_accounts sa ON ps.account_id = sa.id
WHERE DATE(ps.scheduled_time) = CURRENT_DATE
ORDER BY ps.scheduled_time;
```

### Delete Old Videos

```sql
-- Delete videos older than 30 days
DELETE FROM social_queue 
WHERE created_at < NOW() - INTERVAL '30 days';
```

### Reset Failed Post

```sql
-- Reset retry count for a failed post
UPDATE platform_schedules 
SET retry_count = 0, posted = FALSE, error_message = NULL
WHERE id = 123;
```

---

## ⚠️ Things to Remember

### Daily Checklist

- [ ] Laptop plugged into power
- [ ] BitBrowser running (or will auto-start)
- [ ] Video file path is correct
- [ ] Video file exists and isn't corrupted
- [ ] Title/caption follows platform guidelines
- [ ] Scheduler started and running
- [ ] Check status at least once

### Best Practices

**✅ DO:**
- Add videos in the morning
- Use descriptive titles with emojis
- Include relevant hashtags
- Keep videos under 60 seconds
- Check status once or twice daily
- Let scheduler run uninterrupted

**❌ DON'T:**
- Add 20+ videos at once (looks spammy)
- Use same title/caption for all posts
- Stop scheduler mid-post
- Close BitBrowser while posting
- Put laptop to sleep
- Use copyrighted content

---

## 🔄 Weekly Routine

### Monday Morning
- Review last week's posts
- Plan this week's content
- Add first video

### Mid-Week Check (Wednesday)
- Check all accounts still logged in
- Review any failed posts
- Adjust posting times if needed

### Weekend Review
- Check statistics
- Clean up old videos (30+ days)
- Plan next week's content

---

## 📊 Monitoring Best Practices

### How Often to Check?

**Minimum:** Once per day
- Morning: After adding video
- Evening: Check if all posted

**Recommended:** 2-3 times per day
- Morning: Add video + verify schedules
- Afternoon: Check progress
- Evening: Verify completion

**Optimal:** Active monitoring
- Use `view_queue.py --upcoming` throughout day
- Check after each platform should have posted
- Address issues immediately

### What to Monitor

**Every Day:**
- Videos added successfully
- Schedules created (10+ posts)
- At least some posts completed
- No error messages

**Every Week:**
- Total posts made per account
- Success rate per platform
- Any patterns in failures
- Storage space remaining

---

## 💡 Pro Tips

### Tip 1: Prepare Videos in Bulk

Edit and save 5-7 videos on Sunday. Add them throughout the week:
```
Monday.mp4
Tuesday.mp4
Wednesday.mp4
...
```

### Tip 2: Use Consistent Naming

```
2024-01-26_Cat_Tricks.mp4
2024-01-27_Dog_Plays.mp4
```

Makes it easy to find videos later.

### Tip 3: Schedule-Ahead

Add tomorrow's video today:
```bash
python core/add_video.py
# Add video for tomorrow
```

Scheduler automatically spaces it throughout tomorrow.

### Tip 4: Set Reminders

Create Windows scheduled task:
- 8:00 AM: Reminder to add video
- 8:05 AM: Auto-start scheduler (optional)
- 6:00 PM: Reminder to check status

### Tip 5: Keep Logs

Create a simple spreadsheet:
```
Date       | Video Title           | YouTube | Twitter | LinkedIn | Notes
-----------|----------------------|---------|---------|----------|-------
2024-01-26 | Cat Tricks           | ✅      | ✅      | ✅       | Success
2024-01-27 | Dog Playing          | ✅      | ❌      | ✅       | Twitter failed
```

---

## 🆘 Quick Troubleshooting

### Scheduler not posting?
```bash
python force_reset.py
```

### Can't see status?
```bash
python core/view_queue.py --stats
```

### Video not added?
Check file path is correct and file exists.

### Posts stuck "pending"?
Check BitBrowser profiles are logged in.

### Need to re-schedule?
```sql
DELETE FROM platform_schedules WHERE posted = FALSE;
-- Restart scheduler to regenerate
```

---

## 📝 Example Daily Log

```
Monday, Jan 26, 2024
--------------------
08:00 AM - Added "Amazing Cat Video"
08:05 AM - Started scheduler
10:15 AM - Checked status: 3/10 posted ✅
02:30 PM - Checked status: 7/10 posted ✅
06:00 PM - All 10 posts completed ✅
06:05 PM - Stopped scheduler

Notes: Everything worked perfectly!
Video views after 24h: 1,250
```

---

## 🎯 Weekly Goals

Set realistic goals:

**Week 1:** 
- Post 5 videos
- Maintain 90%+ success rate
- Learn the system

**Week 2-4:**
- Post 7 videos per week
- Add more accounts
- Optimize posting times

**Month 2+:**
- Daily posting (7 videos/week)
- 10+ accounts active
- 95%+ success rate
- Automated workflow

---

## ✅ End of Day Checklist

Before stopping for the day:

- [ ] All scheduled posts for today completed
- [ ] Check for error screenshots (fix issues)
- [ ] Tomorrow's video prepared (optional)
- [ ] Scheduler stopped (or leave running overnight)
- [ ] Quick status check looks good
- [ ] No pending failures to address

---

**Daily usage guide complete!** 🎉

For issues, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

For questions, see [FAQ.md](FAQ.md)