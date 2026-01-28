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
    
    # Clear existing text first (Ctrl+A, Delete)
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")
    
    for char in text:
        # Standard keystroke (50ms - 150ms)
        delay = random.uniform(0.05, 0.15)
        
        # Occasional "thinking" pause (every 15-25 chars)
        if random.random() < 0.05: 
            delay += random.uniform(0.3, 0.7)
            
        page.keyboard.type(char)
        time.sleep(delay)

def run_youtube_bot():
    ws_url = config.open_browser(config.YT_PROFILE_ID)
    if not ws_url:
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("Navigating to YouTube Studio...")
            page.goto("https://studio.youtube.com", timeout=60000)
            human_delay(3, 6) # Wait for dashboard to load

            # 1. Click Create
            print("Clicking Create...")
            page.get_by_role("button", name="Create", exact=True).click()
            human_delay(0.5, 1.5) # Quick pause for menu to drop down
            
            print("Clicking Upload videos...")
            page.get_by_role("menuitem", name="Upload videos").click()
            human_delay(2, 4) # Wait for modal

            # 2. Upload File
            print(f"Uploading file: {config.YT_VIDEO_PATH}")
            with page.expect_file_chooser() as fc_info:
                page.get_by_role("button", name="Select files").click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(config.YT_VIDEO_PATH)
            
            # Simulate waiting for the "Processing" bar
            print("Processing upload...")
            human_delay(6, 10) 

            # 3. Fill Title (Human Typing)
            print("Setting Title...")
            # Wait for the title box to actually be editable
            title_box = page.locator("#textbox").first
            title_box.wait_for(state="visible")
            
            # Use the human typing function
            type_like_human(page, "#textbox", config.YT_TITLE)
            
            human_delay(2, 4) # Review what was typed

            # 4. Handle "Not for Kids"
            print("Selecting 'Not made for kids'...")
            page.get_by_role("radio", name="No, it's not made for kids").first.click()
            human_delay(1, 2)

            # 5. Click Next, Next, Next...
            print("Clicking through steps...")
            for i in range(3):
                page.get_by_role("button", name="Next").first.click()
                human_delay(2, 4) # Pause between pages to "read" checks

            # 6. Set Visibility to Public
            print("Setting Public...")
            page.get_by_role("radio", name="Public").first.click()
            human_delay(1, 2)

            # 7. Publish
            print("Clicking Publish...")
            # Final hesitation
            human_delay(2, 3)
            page.get_by_role("button", name="Publish").first.click()

            # 8. Wait for "Video Published" Dialog
            print("Waiting for success dialog...")
            page.wait_for_selector("text=Video published", timeout=60000)
            print("SUCCESS: YouTube video done.")

        except Exception as e:
            print(f"YOUTUBE ERROR: {e}")
            page.screenshot(path="yt_error.png")

        finally:
            browser.close()
            config.close_browser(config.YT_PROFILE_ID)

if __name__ == "__main__":
    run_youtube_bot()