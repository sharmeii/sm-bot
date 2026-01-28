import psycopg2
import config.db_config as db_config

def setup_database():
    """Create all required tables and views"""
    
    print("\n" + "=" * 70)
    print("🔧 SETTING UP DATABASE SCHEMA")
    print("=" * 70)
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        
        cur = conn.cursor()
        
        # 1. Create social_queue table
        print("\n📦 Creating social_queue table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS social_queue (
                id SERIAL PRIMARY KEY,
                video_path TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                link TEXT,
                posted_youtube BOOLEAN DEFAULT FALSE,
                posted_facebook BOOLEAN DEFAULT FALSE,
                posted_linkedin BOOLEAN DEFAULT FALSE,
                posted_tiktok BOOLEAN DEFAULT FALSE,
                posted_pinterest BOOLEAN DEFAULT FALSE,
                posted_twitter BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        print("   ✅ social_queue created")
        
        # 2. Create platform_schedules table
        print("\n📅 Creating platform_schedules table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS platform_schedules (
                id SERIAL PRIMARY KEY,
                queue_id INTEGER REFERENCES social_queue(id) ON DELETE CASCADE,
                platform VARCHAR(50) NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                posted BOOLEAN DEFAULT FALSE,
                posted_at TIMESTAMP,
                error_message TEXT,
                retry_count INTEGER DEFAULT 0,
                UNIQUE(queue_id, platform)
            )
        """)
        print("   ✅ platform_schedules created")
        
        # 3. Create platform_windows table
        print("\n⚙️  Creating platform_windows table...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS platform_windows (
                id SERIAL PRIMARY KEY,
                platform VARCHAR(50) UNIQUE NOT NULL,
                min_hour INTEGER NOT NULL CHECK (min_hour >= 0 AND min_hour < 24),
                max_hour INTEGER NOT NULL CHECK (max_hour >= 0 AND max_hour < 24),
                min_delay_minutes INTEGER DEFAULT 30,
                max_delay_minutes INTEGER DEFAULT 180,
                enabled BOOLEAN DEFAULT TRUE
            )
        """)
        print("   ✅ platform_windows created")
        
        # 4. Insert default platform windows
        print("\n🎯 Inserting default platform settings...")
        cur.execute("""
            INSERT INTO platform_windows (platform, min_hour, max_hour, min_delay_minutes, max_delay_minutes) 
            VALUES 
                ('YouTube Shorts', 8, 22, 30, 240),
                ('LinkedIn Video', 9, 17, 45, 180),
                ('TikTok', 10, 23, 30, 200),
                ('Pinterest Idea', 11, 21, 60, 240),
                ('Twitter', 9, 22, 30, 180)
            ON CONFLICT (platform) DO NOTHING
        """)
        rows = cur.rowcount
        print(f"   ✅ {rows} platform settings added")
        
        # 5. Create pending_posts view
        print("\n👀 Creating pending_posts view...")
        cur.execute("""
            CREATE OR REPLACE VIEW pending_posts AS
            SELECT 
                sq.id,
                sq.title,
                sq.video_path,
                ps.platform,
                ps.scheduled_time,
                ps.posted,
                ps.retry_count
            FROM social_queue sq
            JOIN platform_schedules ps ON sq.id = ps.queue_id
            WHERE ps.posted = FALSE 
                AND ps.scheduled_time <= NOW()
            ORDER BY ps.scheduled_time ASC
        """)
        print("   ✅ pending_posts view created")
        
        # 6. Create queue_status view
        print("\n📊 Creating queue_status view...")
        cur.execute("""
            CREATE OR REPLACE VIEW queue_status AS
            SELECT 
                id,
                title,
                posted_youtube,
                posted_linkedin,
                posted_tiktok,
                posted_pinterest,
                posted_twitter,
                CASE 
                    WHEN posted_youtube AND posted_linkedin AND posted_tiktok 
                         AND posted_pinterest AND posted_twitter THEN 'Complete'
                    ELSE 'In Progress'
                END as status,
                created_at
            FROM social_queue
            ORDER BY created_at DESC
        """)
        print("   ✅ queue_status view created")
        
        # Commit all changes
        conn.commit()
        
        # 7. Verify setup
        print("\n🔍 Verifying setup...")
        
        cur.execute("SELECT COUNT(*) FROM social_queue")
        queue_count = cur.fetchone()[0]
        print(f"   📦 social_queue: {queue_count} videos")
        
        cur.execute("SELECT COUNT(*) FROM platform_schedules")
        schedule_count = cur.fetchone()[0]
        print(f"   📅 platform_schedules: {schedule_count} schedules")
        
        cur.execute("SELECT COUNT(*) FROM platform_windows")
        window_count = cur.fetchone()[0]
        print(f"   ⚙️  platform_windows: {window_count} platforms configured")
        
        cur.close()
        conn.close()
        
        print("\n" + "=" * 70)
        print("✅ DATABASE SETUP COMPLETE!")
        print("=" * 70)
        print("\n📝 Next steps:")
        print("   1. Add videos: python add_video.py")
        print("   2. Or insert via SQL: see direct_sql_guide")
        print("   3. Start scheduler: python db_scheduler.py")
        print("\n" + "=" * 70)
        
        return True
        
    except psycopg2.Error as e:
        print(f"\n❌ Database Error: {e}")
        print(f"\n💡 Make sure:")
        print(f"   1. PostgreSQL is running")
        print(f"   2. Database 'sm_bot' exists")
        print(f"   3. Credentials in db_config.py are correct")
        return False
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

def check_database_exists():
    """Check if the sm_bot database exists"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database="postgres",  # Connect to default database
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        # Check if sm_bot exists
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_config.DB_NAME,))
        exists = cur.fetchone() is not None
        
        cur.close()
        conn.close()
        
        return exists
        
    except Exception as e:
        print(f"❌ Could not check database: {e}")
        return False

def create_database():
    """Create the sm_bot database if it doesn't exist"""
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database="postgres",
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        conn.autocommit = True
        cur = conn.cursor()
        
        print(f"\n🔨 Creating database '{db_config.DB_NAME}'...")
        cur.execute(f"CREATE DATABASE {db_config.DB_NAME}")
        print(f"   ✅ Database '{db_config.DB_NAME}' created")
        
        cur.close()
        conn.close()
        return True
        
    except psycopg2.errors.DuplicateDatabase:
        print(f"   ℹ️  Database '{db_config.DB_NAME}' already exists")
        return True
    except Exception as e:
        print(f"   ❌ Failed to create database: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("🚀 SOCIAL MEDIA AUTOMATION - DATABASE SETUP")
    print("=" * 70)
    
    # Step 1: Check/Create Database
    if not check_database_exists():
        print(f"\n⚠️  Database '{db_config.DB_NAME}' does not exist")
        response = input(f"Create it now? (y/n): ").lower()
        
        if response == 'y':
            if not create_database():
                print("\n❌ Setup failed. Please create the database manually in pgAdmin.")
                sys.exit(1)
        else:
            print("\n❌ Setup cancelled. Please create the database first:")
            print(f"   1. Open pgAdmin")
            print(f"   2. Right-click 'Databases' → Create → Database")
            print(f"   3. Name: {db_config.DB_NAME}")
            print(f"   4. Run this script again")
            sys.exit(1)
    else:
        print(f"\n✅ Database '{db_config.DB_NAME}' found")
    
    # Step 2: Create Tables
    if setup_database():
        print("\n🎉 Setup successful! You're ready to go!")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)