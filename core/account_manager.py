import psycopg2
import config.db_config as db_config

def add_account_interactive():
    """Interactive tool to add accounts"""
    
    print("\n" + "=" * 60)
    print("➕ ADD SOCIAL MEDIA ACCOUNT")
    print("=" * 60)
    
    # Platform selection
    platforms = {
        '1': 'YouTube Shorts',
        '2': 'Twitter',
        '3': 'LinkedIn Video',
        '4': 'TikTok',
        '5': 'Pinterest Idea'
    }
    
    print("\nSelect platform:")
    for key, name in platforms.items():
        print(f"  {key}. {name}")
    
    choice = input("\nEnter number (1-5): ").strip()
    
    if choice not in platforms:
        print("❌ Invalid choice!")
        return
    
    platform = platforms[choice]
    
    # Get account details
    account_name = input(f"\nEnter account name (e.g., 'Main Channel', '@username'): ").strip()
    
    if not account_name:
        print("❌ Account name cannot be empty!")
        return
    
    profile_id = input("\nEnter BitBrowser Profile ID: ").strip()
    
    if not profile_id:
        print("❌ Profile ID cannot be empty!")
        return
    
    # Confirm
    print("\n" + "=" * 60)
    print("CONFIRM:")
    print(f"  Platform: {platform}")
    print(f"  Account: {account_name}")
    print(f"  Profile ID: {profile_id}")
    print("=" * 60)
    
    confirm = input("\nAdd this account? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Cancelled.")
        return
    
    # Add to database
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO social_accounts (platform, account_name, bitbrowser_profile_id, enabled)
            VALUES (%s, %s, %s, TRUE)
            ON CONFLICT (platform, account_name) 
            DO UPDATE SET bitbrowser_profile_id = EXCLUDED.bitbrowser_profile_id
            RETURNING id
        """, (platform, account_name, profile_id))
        
        account_id = cur.fetchone()[0]
        conn.commit()
        
        print(f"\n✅ Account added successfully! (ID: {account_id})")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Database Error: {e}")

def list_accounts():
    """List all accounts"""
    
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        
        cur = conn.cursor()
        
        cur.execute("""
            SELECT id, platform, account_name, bitbrowser_profile_id, enabled
            FROM social_accounts
            ORDER BY platform, account_name
        """)
        
        rows = cur.fetchall()
        
        print("\n" + "=" * 80)
        print("📋 YOUR SOCIAL MEDIA ACCOUNTS")
        print("=" * 80)
        
        if not rows:
            print("\n📭 No accounts found. Add some using option 1!")
        else:
            current_platform = None
            for row in rows:
                account_id, platform, name, profile_id, enabled = row
                
                if platform != current_platform:
                    print(f"\n🎯 {platform}:")
                    current_platform = platform
                
                status = "✅ Active" if enabled else "⏸️  Disabled"
                profile_short = profile_id[:20] + "..." if len(profile_id) > 20 else profile_id
                print(f"   [{account_id}] {name} - {profile_short} - {status}")
        
        print("\n" + "=" * 80)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Database Error: {e}")

def toggle_account():
    """Enable/disable an account"""
    
    list_accounts()
    
    account_id = input("\nEnter account ID to enable/disable: ").strip()
    
    if not account_id.isdigit():
        print("❌ Invalid ID!")
        return
    
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        
        cur = conn.cursor()
        
        # Toggle
        cur.execute("""
            UPDATE social_accounts 
            SET enabled = NOT enabled
            WHERE id = %s
            RETURNING account_name, enabled
        """, (account_id,))
        
        result = cur.fetchone()
        
        if result:
            name, enabled = result
            status = "ENABLED" if enabled else "DISABLED"
            print(f"\n✅ Account '{name}' is now {status}")
            conn.commit()
        else:
            print(f"\n❌ Account ID {account_id} not found!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Database Error: {e}")

def delete_account():
    """Delete an account"""
    
    list_accounts()
    
    account_id = input("\nEnter account ID to DELETE: ").strip()
    
    if not account_id.isdigit():
        print("❌ Invalid ID!")
        return
    
    confirm = input(f"\n⚠️  Are you sure you want to delete account #{account_id}? (y/n): ").strip().lower()
    
    if confirm != 'y':
        print("❌ Cancelled.")
        return
    
    try:
        conn = psycopg2.connect(
            host=db_config.DB_HOST,
            database=db_config.DB_NAME,
            user=db_config.DB_USER,
            password=db_config.DB_PASS,
            port=db_config.DB_PORT
        )
        
        cur = conn.cursor()
        
        cur.execute("""
            DELETE FROM social_accounts 
            WHERE id = %s
            RETURNING account_name
        """, (account_id,))
        
        result = cur.fetchone()
        
        if result:
            name = result[0]
            print(f"\n✅ Account '{name}' deleted!")
            conn.commit()
        else:
            print(f"\n❌ Account ID {account_id} not found!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Database Error: {e}")

def main():
    while True:
        print("\n" + "=" * 60)
        print("🔧 MULTI-ACCOUNT MANAGER")
        print("=" * 60)
        print("\n1. Add new account")
        print("2. List all accounts")
        print("3. Enable/Disable account")
        print("4. Delete account")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            add_account_interactive()
        elif choice == '2':
            list_accounts()
        elif choice == '3':
            toggle_account()
        elif choice == '4':
            delete_account()
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("\n❌ Invalid choice!")

if __name__ == "__main__":
    main()