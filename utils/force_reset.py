import requests
import time
import config.config as config

def force_reset(profile_id=None):
    """
    Force close and reopen a BitBrowser profile.
    If no profile_id is given, uses the SHARED_ID from config.
    """
    if profile_id is None:
        profile_id = config.SHARED_ID
    
    print(f"--- FORCE RESET FOR PROFILE: {profile_id} ---")

    # Step 1: Force Close
    print("Step 1: Sending CLOSE command...")
    try:
        close_resp = requests.post(
            f"{config.API_URL}/browser/close", 
            json={"id": profile_id},
            timeout=10
        ).json()
        print(f"   Response: {close_resp.get('msg', 'Closed')}")
    except Exception as e:
        print(f"   Close failed (this is OK if already closed): {e}")

    # Step 2: Wait for cleanup
    print("Step 2: Waiting 5 seconds for BitBrowser cleanup...")
    time.sleep(5)

    # Step 3: Try to open (optional - most bots open it themselves)
    # We don't open here because each bot does it via config.open_browser()
    print("Step 3: Reset complete. Profile ready for next use.")
    print("=" * 50)

def force_reset_all_platforms():
    """
    Reset all platform profiles (useful if you have separate profiles).
    Since you're using SHARED_ID for all, this just resets once.
    """
    print("\n" + "=" * 50)
    print("🔄 RESETTING ALL PLATFORM PROFILES")
    print("=" * 50)
    
    # Get unique profile IDs
    profiles = {
        config.YT_PROFILE_ID,
        config.LI_PROFILE_ID,
        config.TT_PROFILE_ID,
        config.PIN_PROFILE_ID,
        config.TWITTER_PROFILE_ID
    }
    
    for profile_id in profiles:
        force_reset(profile_id)
        time.sleep(2)  # Small delay between resets
    
    print("\n✅ All profiles reset successfully!")
    print("=" * 50)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--all":
            force_reset_all_platforms()
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python force_reset.py           # Reset shared profile")
            print("  python force_reset.py --all     # Reset all platform profiles")
            print("  python force_reset.py --help    # Show this help")
        else:
            # Reset specific profile by ID
            force_reset(sys.argv[1])
    else:
        # Default: reset shared profile
        force_reset()