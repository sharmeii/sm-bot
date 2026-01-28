import time
import datetime
import random
import psycopg2
import sys
import config.db_config as db_config

# Import your bots
try:
    import bots.youtube_poster as youtube_poster
    import bots.linkedin_poster as linkedin_poster
    import bots.tiktok_poster as tiktok_poster
    import bots.pinterest_poster as pinterest_poster
    import bots.twitter_poster as twitter_poster
    import utils.force_reset as force_reset
except ImportError as e:
    print(f"ERROR: Missing bot file. {e}")
    sys.exit()

# Platform to bot mapping
BOT_MAP = {
    "YouTube Shorts": youtube_poster.run_youtube_bot,
    "LinkedIn Video": linkedin_poster.run_linkedin_bot,
    "TikTok": tiktok_poster.run_tiktok_bot,
    "Pinterest Idea": pinterest_poster.run_pinterest_bot,
    "Twitter": twitter_poster.run_twitter_bot
}

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        return conn
    except Exception as e:
        print(f"❌ Database Connection Failed: {e}")
        return None

def generate_random_time_today(min_hour, max_hour):
    """Generate a random time within specified hours for today"""
    now = datetime.datetime.now()
    
    # Calculate window
    window_start = now.replace(hour=min_hour, minute=0, second=0, microsecond=0)
    window_end = now.replace(hour=max_hour, minute=0, second=0, microsecond=0)
    
    # If window_start has passed, use current time
    if window_start < now:
        window_start = now
    
    # If entire window has passed today, schedule for tomorrow
    if window_start >= window_end:
        window_start = window_start + datetime.timedelta(days=1)
        window_start = window_start.replace(hour=min_hour, minute=0)
        window_end = window_start.replace(hour=max_hour, minute=0)
    
    # Calculate random time within the window
    total_minutes = int((window_end - window_start).total_seconds() / 60)
    
    if total_minutes <= 0:
        # Edge case: schedule for tomorrow
        scheduled = now + datetime.timedelta(days=1)
        scheduled = scheduled.replace(hour=min_hour, minute=random.randint(0, 59))
    else:
        random_minutes = random.randint(0, total_minutes)
        scheduled = window_start + datetime.timedelta(minutes=random_minutes)
    
    return scheduled

def create_schedules_for_job(conn, job_id):
    """Create randomized schedules for all enabled accounts"""
    cur = conn.cursor()
    
    # Get all enabled accounts
    cur.execute("""
        SELECT sa.id, sa.platform, sa.account_name, pw.min_hour, pw.max_hour
        FROM social_accounts sa
        JOIN platform_windows pw ON sa.platform = pw.platform
        WHERE sa.enabled = TRUE AND pw.enabled = TRUE
    """)
    
    accounts = cur.fetchall()
    
    if not accounts:
        print("   ⚠️ No enabled accounts found!")
        cur.close()
        return
    
    print(f"\n📅 Creating schedules for Job #{job_id} across {len(accounts)} accounts:")
    
    for account_id, platform, account_name, min_hour, max_hour in accounts:
        scheduled_time = generate_random_time_today(min_hour, max_hour)
        
        try:
            cur.execute("""
                INSERT INTO platform_schedules (queue_id, account_id, platform, scheduled_time, posted)
                VALUES (%s, %s, %s, %s, FALSE)
                ON CONFLICT (queue_id, account_id) DO NOTHING
            """, (job_id, account_id, platform, scheduled_time))
            
            print(f"   ✅ {platform} ({account_name}): {scheduled_time.strftime('%I:%M %p on %b %d')}")
        except Exception as e:
            print(f"   ⚠️ Failed to schedule {platform} ({account_name}): {e}")
    
    conn.commit()
    cur.close()

def fetch_next_pending_post(conn):
    """Fetch the next post that's ready to go"""
    cur = conn.cursor()
    
    query = """
        SELECT ps.id, ps.queue_id, ps.account_id, ps.platform, ps.scheduled_time,
               sq.video_path, sq.title, sq.description, sq.link,
               sa.account_name, sa.bitbrowser_profile_id
        FROM platform_schedules ps
        JOIN social_queue sq ON ps.queue_id = sq.id
        JOIN social_accounts sa ON ps.account_id = sa.id
        WHERE ps.posted = FALSE 
          AND ps.scheduled_time <= NOW()
          AND ps.retry_count < 3
          AND sa.enabled = TRUE
        ORDER BY ps.scheduled_time ASC
        LIMIT 1
    """
    
    cur.execute(query)
    row = cur.fetchone()
    cur.close()
    
    if row:
        return {
            "schedule_id": row[0],
            "queue_id": row[1],
            "account_id": row[2],
            "platform": row[3],
            "scheduled_time": row[4],
            "path": row[5],
            "title": row[6],
            "desc": row[7] or "",
            "link": row[8] or "",
            "account_name": row[9],
            "profile_id": row[10]
        }
    return None

def update_post_status(conn, schedule_id, success=True, error_msg=None):
    """Update schedule status"""
    cur = conn.cursor()
    
    try:
        if success:
            cur.execute("""
                UPDATE platform_schedules 
                SET posted = TRUE, posted_at = NOW()
                WHERE id = %s
            """, (schedule_id,))
            print(f"   💾 Database updated: Post marked as DONE")
        else:
            cur.execute("""
                UPDATE platform_schedules 
                SET retry_count = retry_count + 1,
                    error_message = %s
                WHERE id = %s
            """, (error_msg, schedule_id))
            print(f"   ⚠️ Retry count incremented. Error: {error_msg}")
        
        conn.commit()
    except Exception as e:
        print(f"   ❌ Failed to update DB: {e}")
        conn.rollback()
    finally:
        cur.close()

def check_for_new_jobs(conn):
    """Check for jobs that don't have schedules yet and create them"""
    cur = conn.cursor()
    
    query = """
        SELECT sq.id 
        FROM social_queue sq
        WHERE NOT EXISTS (
            SELECT 1 FROM platform_schedules ps WHERE ps.queue_id = sq.id
        )
    """
    
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    
    for row in rows:
        job_id = row[0]
        print(f"\n🆕 New job detected: #{job_id}")
        create_schedules_for_job(conn, job_id)

def inject_config_for_platform(platform, job_data, profile_id):
    """Inject job data and profile ID into bot modules"""
    
    # Import config here to modify it
    import config.config as config
    
    if platform == "YouTube Shorts":
        config.YT_TITLE = job_data['title']
        config.YT_DESC = job_data['desc']
        config.YT_VIDEO_PATH = job_data['path']
        config.YT_PROFILE_ID = profile_id
    
    elif platform == "LinkedIn Video":
        config.LI_CAPTION = job_data['title']
        config.LI_MEDIA_PATH = job_data['path']
        config.LI_PROFILE_ID = profile_id
    
    elif platform == "TikTok":
        config.TT_CAPTION = job_data['title']
        config.TT_MEDIA_PATH = job_data['path']
        config.TT_PROFILE_ID = profile_id
    
    elif platform == "Pinterest Idea":
        config.PIN_TITLE = job_data['title']
        config.PIN_DESCRIPTION = job_data['desc']
        config.PIN_MEDIA_PATH = job_data['path']
        config.PIN_PROFILE_ID = profile_id
        config.PIN_BOARD = "Cats"
    
    elif platform == "Twitter":
        config.TWITTER_CAPTION = job_data['title']
        config.TWITTER_MEDIA_PATH = job_data['path']
        config.TWITTER_PROFILE_ID = profile_id

def main():
    print("=" * 60)
    print("🤖 MULTI-ACCOUNT SOCIAL MEDIA SCHEDULER")
    print("=" * 60)
    print("Features:")
    print("  ✅ Multiple accounts per platform")
    print("  ✅ Random posting times per account")
    print("  ✅ Smart retry logic")
    print("  ✅ Auto-schedule new videos")
    print("=" * 60)
    
    while True:
        conn = get_db_connection()
        if not conn:
            print("⏳ Retrying database connection in 60s...")
            time.sleep(60)
            continue
        
        # Check for new jobs first
        check_for_new_jobs(conn)
        
        # Fetch next ready post
        post = fetch_next_pending_post(conn)
        
        if not post:
            conn.close()
            print(f"\n⏰ No posts ready. Next check in 5 minutes... ({datetime.datetime.now().strftime('%I:%M %p')})")
            time.sleep(300)
            continue
        
        platform = post['platform']
        print(f"\n🎬 POSTING NOW")
        print(f"   Platform: {platform}")
        print(f"   Account: {post['account_name']}")
        print(f"   Profile ID: {post['profile_id'][:20]}...")
        print(f"   Job ID: #{post['queue_id']}")
        print(f"   Title: {post['title']}")
        print(f"   Scheduled: {post['scheduled_time'].strftime('%I:%M %p')}")
        print(f"   Actual: {datetime.datetime.now().strftime('%I:%M %p')}")
        
        # Get bot function
        if platform not in BOT_MAP:
            print(f"   ❌ Unknown platform: {platform}")
            conn.close()
            continue
        
        bot_func = BOT_MAP[platform]
        
        # Inject config with the specific profile ID
        inject_config_for_platform(platform, post, post['profile_id'])
        
        # Try force reset
        try:
            force_reset.force_reset(post['profile_id'])
        except:
            pass
        
        # Wait a bit before posting (human behavior)
        wait_time = random.randint(10, 30)
        print(f"   ⏳ Waiting {wait_time}s before posting...")
        time.sleep(wait_time)
        
        # Execute bot
        success = False
        error_msg = None
        
        try:
            bot_func()
            success = True
            print(f"   ✅ {platform} ({post['account_name']}) posted successfully!")
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ {platform} ({post['account_name']}) failed: {e}")
        
        # Update database
        update_post_status(conn, post['schedule_id'], success, error_msg)
        
        conn.close()
        
        # Random delay before next post (2-8 minutes)
        delay = random.randint(120, 480)
        print(f"\n💤 Next check in {delay//60} minutes...")
        time.sleep(delay)

if __name__ == "__main__":
    main()