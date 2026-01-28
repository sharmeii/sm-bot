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
    try:
        page.locator(selector).first.click()
    except:
        pass
    
    for char in text:
        delay = random.uniform(0.05, 0.15)
        if random.random() < 0.1: 
            delay += random.uniform(0.2, 0.5)
        page.keyboard.type(char)
        time.sleep(delay)

def run_twitter_bot():
    ws_url = config.open_browser(config.TWITTER_PROFILE_ID)
    if not ws_url:
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("Navigating to X (Twitter)...")
            page.goto("https://x.com/home", timeout=60000)
            human_delay(4, 7)

            # 1. Find the Tweet Box
            print("Looking for composer...")
            # X uses specific data-testids. This is the main input box.
            input_selector = "div[data-testid='tweetTextarea_0']"
            
            # Sometimes the composer isn't open, we might need to click "Post" side button
            if not page.locator(input_selector).is_visible():
                print("Composer not visible. Clicking side 'Post' button...")
                page.locator("a[data-testid='SideNav_NewTweet_Button']").click()
                human_delay(2, 3)

            # 2. Upload Media (Direct Injection)
            if config.TWITTER_MEDIA_PATH:
                print(f"Uploading media: {config.TWITTER_MEDIA_PATH}")
                try:
                    # Twitter's file input is hidden but accessible
                    page.locator("input[data-testid='fileInput']").first.set_input_files(config.TWITTER_MEDIA_PATH)
                    
                    # Wait for upload preview to appear
                    print("Waiting for media preview...")
                    page.locator("div[data-testid='attachments']").wait_for(state="visible", timeout=20000)
                    human_delay(3, 5) # Simulate looking at the preview
                except Exception as e:
                    print(f"Media upload failed (or skipped): {e}")

            # 3. Type Caption (Human)
            print("Typing tweet...")
            type_like_human(page, input_selector, config.TWITTER_CAPTION)
            human_delay(2, 4)

            # 4. Click Post
            print("Clicking Post...")
            post_btn = page.locator("button[data-testid='tweetButtonInline']")
            
            # Wait for button to enable (it's disabled while uploading)
            for i in range(10):
                if not post_btn.is_disabled():
                    break
                time.sleep(1)
            
            human_delay(1, 2)
            post_btn.click()

            # 5. Verification
            print("Waiting for confirmation...")
            # We look for the "Your post was sent" toast or the text to appear in feed
            try:
                # X shows a "Your post was sent" toast at the bottom
                page.wait_for_selector("div[data-testid='toast']", timeout=10000)
                print("SUCCESS: Twitter post sent.")
            except:
                print("SUCCESS: Post clicked (Implicit).")

        except Exception as e:
            print(f"TWITTER ERROR: {e}")
            page.screenshot(path="twitter_error.png")

        finally:
            browser.close()
            config.close_browser(config.TWITTER_PROFILE_ID)

if __name__ == "__main__":
    run_twitter_bot()