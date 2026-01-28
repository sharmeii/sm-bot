import psycopg2
import config.db_config as db_config
from datetime import datetime

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

def view_queue_status():
    """Show all videos and their posting status by account"""
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    # Get all videos
    cur.execute("""
        SELECT id, title, video_path, created_at
        FROM social_queue
        ORDER BY created_at DESC
    """)
    
    videos = cur.fetchall()
    
    print("\n" + "=" * 100)
    print("📊 SOCIAL MEDIA QUEUE STATUS (MULTI-ACCOUNT)")
    print("=" * 100)
    
    if not videos:
        print("📭 Queue is empty. Add videos using add_video.py")
        print("=" * 100)
        cur.close()
        conn.close()
        return
    
    for video_id, title, path, created in videos:
        # Get posting status for this video across all accounts
        cur.execute("""
            SELECT 
                sa.platform,
                sa.account_name,
                ps.posted,
                ps.scheduled_time
            FROM social_accounts sa
            LEFT JOIN platform_schedules ps ON sa.id = ps.account_id AND ps.queue_id = %s
            WHERE sa.enabled = TRUE
            ORDER BY sa.platform, sa.account_name
        """, (video_id,))
        
        accounts_status = cur.fetchall()
        
        # Count completed
        total_accounts = len(accounts_status)
        completed = sum(1 for _, _, posted, _ in accounts_status if posted)
        
        print(f"\n🎬 Job #{video_id}: {title}")
        print(f"   📁 {path}")
        print(f"   📅 Added: {created.strftime('%b %d, %I:%M %p')}")
        print(f"   📊 Progress: {completed}/{total_accounts} accounts posted")
        print(f"   Status by Account:")
        
        current_platform = None
        for platform, account_name, posted, scheduled_time in accounts_status:
            if platform != current_platform:
                print(f"\n      {platform}:")
                current_platform = platform
            
            if posted:
                status = "✅ Posted"
            elif scheduled_time:
                status = f"⏳ Scheduled for {scheduled_time.strftime('%I:%M %p on %b %d')}"
            else:
                status = "❓ Not scheduled"
            
            print(f"         • {account_name}: {status}")
    
    print("\n" + "=" * 100)
    
    cur.close()
    conn.close()

def view_upcoming_posts():
    """Show scheduled posts with account info"""
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            sq.id, 
            sq.title, 
            sa.platform, 
            sa.account_name,
            ps.scheduled_time, 
            ps.posted, 
            ps.retry_count
        FROM platform_schedules ps
        JOIN social_queue sq ON ps.queue_id = sq.id
        JOIN social_accounts sa ON ps.account_id = sa.id
        WHERE ps.posted = FALSE AND sa.enabled = TRUE
        ORDER BY ps.scheduled_time ASC
        LIMIT 20
    """)
    
    rows = cur.fetchall()
    
    print("\n" + "=" * 100)
    print("📅 UPCOMING SCHEDULED POSTS")
    print("=" * 100)
    
    if not rows:
        print("📭 No upcoming posts scheduled.")
        print("=" * 100)
        cur.close()
        conn.close()
        return
    
    now = datetime.now()
    
    for row in rows:
        job_id, title, platform, account_name, scheduled, posted, retries = row
        
        # Calculate time until post
        time_diff = scheduled - now
        
        if time_diff.total_seconds() < 0:
            status = "⚡ READY NOW"
        elif time_diff.total_seconds() < 3600:
            mins = int(time_diff.total_seconds() / 60)
            status = f"⏰ In {mins} minutes"
        elif time_diff.total_seconds() < 86400:
            hours = int(time_diff.total_seconds() / 3600)
            status = f"⏰ In {hours} hours"
        else:
            days = int(time_diff.total_seconds() / 86400)
            status = f"📆 In {days} days"
        
        retry_info = f" (Retry #{retries})" if retries > 0 else ""
        
        print(f"\n{status}")
        print(f"   🎬 Job #{job_id}: {title[:50]}...")
        print(f"   📱 Platform: {platform}")
        print(f"   👤 Account: {account_name}")
        print(f"   🕐 Scheduled: {scheduled.strftime('%b %d, %I:%M %p')}{retry_info}")
    
    print("\n" + "=" * 100)
    
    cur.close()
    conn.close()

def view_stats():
    """Show overall statistics"""
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    # Total videos
    cur.execute("SELECT COUNT(*) FROM social_queue")
    total_videos = cur.fetchone()[0]
    
    # Total accounts
    cur.execute("SELECT COUNT(*) FROM social_accounts WHERE enabled = TRUE")
    total_accounts = cur.fetchone()[0]
    
    # Total possible posts (videos × accounts)
    total_possible = total_videos * total_accounts
    
    # Completed posts
    cur.execute("SELECT COUNT(*) FROM platform_schedules WHERE posted = TRUE")
    completed = cur.fetchone()[0]
    
    # Pending posts
    cur.execute("SELECT COUNT(*) FROM platform_schedules WHERE posted = FALSE")
    pending = cur.fetchone()[0]
    
    # Posts in next hour
    cur.execute("""
        SELECT COUNT(*) FROM platform_schedules 
        WHERE posted = FALSE 
          AND scheduled_time <= NOW() + INTERVAL '1 hour'
    """)
    next_hour = cur.fetchone()[0]
    
    # Accounts breakdown
    cur.execute("""
        SELECT platform, COUNT(*) 
        FROM social_accounts 
        WHERE enabled = TRUE 
        GROUP BY platform 
        ORDER BY platform
    """)
    accounts_by_platform = cur.fetchall()
    
    print("\n" + "=" * 60)
    print("📈 STATISTICS")
    print("=" * 60)
    print(f"Total Videos:        {total_videos}")
    print(f"Total Accounts:      {total_accounts}")
    print(f"Possible Posts:      {total_possible}")
    print(f"Completed Posts:     {completed}")
    print(f"Pending Posts:       {pending}")
    print(f"Due in Next Hour:    {next_hour}")
    print("\n📊 Accounts by Platform:")
    for platform, count in accounts_by_platform:
        print(f"   • {platform}: {count} account(s)")
    print("=" * 60)
    
    cur.close()
    conn.close()

def view_accounts():
    """Show all accounts and their status"""
    conn = get_db_connection()
    if not conn:
        return
    
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id,
            platform,
            account_name,
            bitbrowser_profile_id,
            enabled,
            (SELECT COUNT(*) FROM platform_schedules ps WHERE ps.account_id = sa.id AND ps.posted = TRUE) as posts_made,
            (SELECT COUNT(*) FROM platform_schedules ps WHERE ps.account_id = sa.id AND ps.posted = FALSE) as posts_pending
        FROM social_accounts sa
        ORDER BY platform, account_name
    """)
    
    rows = cur.fetchall()
    
    print("\n" + "=" * 100)
    print("👥 YOUR ACCOUNTS")
    print("=" * 100)
    
    if not rows:
        print("📭 No accounts found. Add some using account_manager.py!")
        print("=" * 100)
        cur.close()
        conn.close()
        return
    
    current_platform = None
    for row in rows:
        account_id, platform, name, profile_id, enabled, posts_made, posts_pending = row
        
        if platform != current_platform:
            print(f"\n🎯 {platform}:")
            current_platform = platform
        
        status = "✅ Active" if enabled else "⏸️  Disabled"
        profile_short = profile_id[:20] + "..." if len(profile_id) > 20 else profile_id
        
        print(f"   [{account_id}] {name}")
        print(f"       Profile: {profile_short}")
        print(f"       Status: {status}")
        print(f"       Posts: {posts_made} completed, {posts_pending} pending")
    
    print("\n" + "=" * 100)
    
    cur.close()
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--upcoming":
            view_upcoming_posts()
        elif sys.argv[1] == "--stats":
            view_stats()
        elif sys.argv[1] == "--accounts":
            view_accounts()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python view_queue.py              # Show all videos and status")
            print("  python view_queue.py --upcoming   # Show upcoming scheduled posts")
            print("  python view_queue.py --stats      # Show statistics")
            print("  python view_queue.py --accounts   # Show all accounts")
            print("  python view_queue.py --help       # Show this help")
    else:
        view_queue_status()
        view_upcoming_posts()
        view_stats()