import time
import random
from playwright.sync_api import sync_playwright
import config.config as config

# --- HUMAN HELPER FUNCTIONS ---
def human_delay(min_seconds=1.5, max_seconds=4.0):
    sleep_time = random.uniform(min_seconds, max_seconds)
    time.sleep(sleep_time)

def type_like_human(page, selector, text):
    try:
        page.locator(selector).first.click()
    except:
        pass
    for char in text:
        delay = random.uniform(0.05, 0.15)
        if random.random() < 0.1: delay += random.uniform(0.2, 0.5)
        page.keyboard.type(char)
        time.sleep(delay)

def run_tiktok_bot():
    ws_url = config.open_browser(config.TT_PROFILE_ID)
    if not ws_url: return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("Navigating to TikTok Upload...")
            page.goto("https://www.tiktok.com/creator-center/upload", timeout=60000)
            human_delay(5, 8)

            # 1. Upload Media
            print(f"Uploading media: {config.TT_MEDIA_PATH}")
            try:
                page.locator("input[type='file']").first.set_input_files(config.TT_MEDIA_PATH)
                print("File injected.")
            except:
                page.frame_locator("iframe").first.locator("input[type='file']").first.set_input_files(config.TT_MEDIA_PATH)
                print("File injected (Iframe).")

            print("Waiting for video to process...")
            human_delay(8, 12)

            # 2. Caption
            print("Typing caption...")
            try:
                type_like_human(page, "div.public-DraftEditor-content", config.TT_CAPTION)
            except:
                page.keyboard.type(config.TT_CAPTION)
            human_delay(2, 4)

            # 3. Wait for Initial Check
            print("Waiting for Copyright Check...")
            page.mouse.wheel(0, 500)
            post_btn = page.locator("button:has-text('Post')").last
            
            for i in range(20):
                if not post_btn.is_disabled():
                    print("Main Post Button ready.")
                    break
                if i % 3 == 0: print(f"Waiting... {i*3}s")
                time.sleep(3)

            # --- THE DOUBLE-TAP FIX ---
            print("Clicking Main Post Button...")
            post_btn.click()
            time.sleep(3) # Wait for popup to appear

            # Handle the "Post now" Popup
            try:
                post_now_btn = page.locator("button:has-text('Post now')")
                
                if post_now_btn.is_visible():
                    print("⚠️ Popup detected! Executing Double-Tap Strategy...")
                    
                    # CLICK 1
                    print("Clicking 'Post now' (1st time)...")
                    post_now_btn.click()
                    time.sleep(2)
                    
                    # CLICK 2 (If still there)
                    if post_now_btn.is_visible():
                        print("Clicking 'Post now' (2nd time)...")
                        post_now_btn.click()
                        time.sleep(2)
                    else:
                        print("Popup disappeared after 1st click.")

            except Exception as e:
                print(f"Popup handling error: {e}")

            # Final Verification Loop
            print("Verifying success...")
            for i in range(5):
                # If we are redirected, it worked
                if "upload" not in page.url:
                    print("✅ Success! Redirected to new page.")
                    break
                
                # If the Manage Posts text appears, it worked
                if page.locator("text=Manage your posts").is_visible():
                    print("✅ Success! Found 'Manage your posts'.")
                    break

                # If the 'Post' button is STILL visible and enabled, try clicking it one last time
                if post_btn.is_visible() and not post_btn.is_disabled():
                    print("⚠️ Main Post button still here. Clicking it again...")
                    post_btn.click()
                
                time.sleep(3)
            
            # Final Safety Wait
            time.sleep(2)

        except Exception as e:
            print(f"TIKTOK ERROR: {e}")
            page.screenshot(path="tiktok_error.png")

        finally:
            browser.close()
            config.close_browser(config.TT_PROFILE_ID)

if __name__ == "__main__":
    run_tiktok_bot()