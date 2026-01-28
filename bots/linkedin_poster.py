import time
import random
from playwright.sync_api import sync_playwright
import config.config as config

# --- HUMAN HELPER FUNCTIONS ---
def human_delay(min_seconds=1.5, max_seconds=4.0):
    """Sleeps for a random amount of time to mimic human hesitation."""
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)

def type_like_human(page, selector, text):
    """Types text one character at a time with variable speed."""
    # Click the element first to focus
    page.locator(selector).first.click()
    
    for char in text:
        # Most keys take 50ms-150ms
        delay = random.uniform(0.05, 0.15)
        
        # Occasionally pause for "thinking" (every 10-20 chars)
        if random.random() < 0.08: 
            delay += random.uniform(0.3, 0.8)
            
        page.keyboard.type(char)
        time.sleep(delay)

def run_linkedin_bot():
    print("--- Opening Profile (LinkedIn) ---")
    try:
        ws_url = config.open_browser(config.LI_PROFILE_ID)
    except Exception as e:
        print(f"SKIPPING: Could not open browser. {e}")
        return

    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp(ws_url)
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else context.new_page()

            print("Navigating to LinkedIn...")
            page.goto("https://www.linkedin.com/feed/", timeout=60000)
            human_delay(3, 6) # Wait for feed to load

            # 2. Trigger "Video" Mode
            print("Clicking 'Video' button...")
            try:
                page.locator("button:has-text('Video')").first.click()
            except:
                print("Video button fallback...")
                page.locator(".share-box-feed-entry__trigger").click()
            
            human_delay(2, 4)

            # 3. Upload Media (Direct Injection)
            print(f"Uploading media: {config.LI_MEDIA_PATH}")
            try:
                page.locator("input[type='file']").first.set_input_files(config.LI_MEDIA_PATH)
                print("File injected successfully.")
            except Exception as e:
                print(f"Upload failed: {e}")
                return

            # 4. Handle 'Editor' Preview Screen
            print("Waiting for 'Next' button...")
            try:
                next_btn = page.locator("button span:has-text('Next')").first
                next_btn.wait_for(state="visible", timeout=30000)
                
                # Human pause before clicking Next
                human_delay(1.5, 3.0) 
                next_btn.click()
                print("Clicked 'Next' on preview screen.")
            except:
                print("No 'Next' button found. Moving on...")

            human_delay(2, 4)

            # 5. Fill Caption (Human Typing)
            print("Typing caption...")
            try:
                # We use the new human typing function here
                type_like_human(page, "div.ql-editor", config.LI_CAPTION)
            except:
                # Fallback if specific editor not found
                page.keyboard.type(config.LI_CAPTION)

            human_delay(2, 5) # Reviewing the post

            # 6. Click Post
            print("Clicking Post...")
            post_btn = page.locator("button.share-actions__primary-action")
            
            # Wait for button to be clickable
            for i in range(10):
                if not post_btn.is_disabled():
                    break
                time.sleep(1)
            
            # Final hesitation before committing
            human_delay(1, 2)
            post_btn.click()

            # 7. Verification
            print("Waiting for confirmation...")
            try:
                page.wait_for_selector("text=Post successful", timeout=15000)
                print("SUCCESS: LinkedIn post submitted.")
            except:
                if not page.locator("div.ql-editor").is_visible():
                     print("SUCCESS: Post modal closed (Implicit Success).")
                else:
                     print("WARNING: Modal still open. Post might have failed.")

        except Exception as e:
            print(f"LINKEDIN ERROR: {e}")
            page.screenshot(path="linkedin_error.png")

        finally:
            config.close_browser(config.LI_PROFILE_ID)

if __name__ == "__main__":
    run_linkedin_bot()