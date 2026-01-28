import psycopg2
import config.db_config as db_config
import sys
import os


def add_video_to_queue(video_path, title, description="", link=""):
    """Add a new video to the posting queue"""
    
    # Validate file exists
    if not os.path.exists(video_path):
        print(f"❌ Error: File not found: {video_path}")
        return False
    
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        
        cur = conn.cursor()
        
        # Insert into queue
        cur.execute("""
            INSERT INTO social_queue 
            (video_path, title, description, link)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (video_path, title, description, link))
        
        job_id = cur.fetchone()[0]
        conn.commit()
        
        print("=" * 60)
        print("✅ VIDEO ADDED TO QUEUE")
        print("=" * 60)
        print(f"Job ID: #{job_id}")
        print(f"Title: {title}")
        print(f"File: {video_path}")
        print(f"Description: {description[:50]}..." if len(description) > 50 else f"Description: {description}")
        print("\n📅 The scheduler will automatically create random posting times")
        print("   for all platforms when it next runs.")
        print("=" * 60)
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database Error: {e}")
        return False

def interactive_add():
    """Interactive mode to add videos"""
    print("=" * 60)
    print("📹 ADD VIDEO TO SOCIAL MEDIA QUEUE")
    print("=" * 60)
    
    video_path = input("\nEnter full path to video file: ").strip().strip('"').strip("'")
    
    if not os.path.exists(video_path):
        print(f"❌ File not found: {video_path}")
        return
    
    title = input("Enter title/caption: ").strip()
    
    if not title:
        print("❌ Title cannot be empty")
        return
    
    description = input("Enter description (optional, press Enter to skip): ").strip()
    link = input("Enter link (optional, press Enter to skip): ").strip()
    
    add_video_to_queue(video_path, title, description, link)

def batch_add():
    """Example of batch adding multiple videos"""
    videos = [
        {
            "path": r"C:\Users\Sharmayn\Downloads\cat_video_1.mp4",
            "title": "Amazing Cat Does Backflip! 🐱",
            "desc": "You won't believe what this cat can do! #cats #amazing",
            "link": ""
        },
        {
            "path": r"C:\Users\Sharmayn\Downloads\cat_video_2.mp4",
            "title": "Funny Cat Compilation 😂",
            "desc": "The funniest cat moments ever! #funny #pets",
            "link": ""
        }
    ]
    
    print(f"\n📦 Batch adding {len(videos)} videos...\n")
    
    for v in videos:
        add_video_to_queue(v['path'], v['title'], v['desc'], v['link'])
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--batch":
            batch_add()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python add_video.py              # Interactive mode")
            print("  python add_video.py --batch      # Batch mode (edit script first)")
            print("  python add_video.py --help       # Show this help")
    else:
        interactive_add()