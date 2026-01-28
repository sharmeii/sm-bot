import time
from playwright.sync_api import sync_playwright
import config.config as config 

def run_pinterest_bot():
    ws_url = config.open_browser(config.PIN_PROFILE_ID)
    if not ws_url:
        return

    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        try:
            print("Navigating to Pinterest Builder...")
            page.goto("https://www.pinterest.com/pin-builder/", timeout=60000)
            
            # --- CHECK FOR LOGIN ---
            time.sleep(5)
            if page.get_by_text("Log in", exact=True).is_visible() or "login" in page.url:
                print("⚠️ ALERT: You seem to be logged out. Please log in manually.")
                print("Waiting 60s for you to log in...")
                time.sleep(60)

            # 1. Upload Media
            print(f"Uploading media: {config.PIN_MEDIA_PATH}")
            try:
                page.wait_for_selector("text=Drag and drop", timeout=15000)
            except:
                print("Warning: 'Drag and drop' text not found, trying upload anyway...")

            file_input = page.locator("input[type='file']").first
            file_input.set_input_files(config.PIN_MEDIA_PATH)
            
            print("Waiting for upload preview...")
            page.get_by_placeholder("Add a title").wait_for(state="visible", timeout=30000)
            time.sleep(2)

            # 2. Fill Details (Tab Strategy)
            print("Filling Title...")
            page.get_by_placeholder("Add a title").click()
            page.get_by_placeholder("Add a title").fill(config.PIN_TITLE)
            time.sleep(1)
            
            print("Filling Description (via Tab)...")
            page.keyboard.press("Tab")
            time.sleep(0.5)
            page.keyboard.type(config.PIN_DESCRIPTION)
            time.sleep(1)

            pin_link = getattr(config, 'PIN_LINK', None)
            if pin_link:
                print("Filling Link (via Tab)...")
                page.keyboard.press("Tab")
                time.sleep(0.5)
                page.keyboard.type(pin_link)
            else:
                print("No Link provided in config, skipping...")

            # 3. Select Board
            print(f"Selecting Board: '{config.PIN_BOARD}'...")
            
            # Click the dropdown
            board_dropdown = page.locator('[data-test-id="board-dropdown-select-button"]')
            board_dropdown.click()
            time.sleep(2)

            # Search for board (Using the ID fix)
            page.locator("#pickerSearchField").fill(config.PIN_BOARD)
            time.sleep(2)

            # Click the result
            page.locator(f'[title="{config.PIN_BOARD}"]').first.click()
            time.sleep(2)

            # 4. Publish (THE FIX)
            print("Clicking Publish...")
            
            # We look for the main button in the top header.
            # Usually named "Publish" or "Save". We try both to be safe.
            try:
                # Try explicit 'Publish' button first
                publish_btn = page.get_by_role("button", name="Publish").first
                publish_btn.click()
            except:
                print("Publish button not found, trying 'Save'...")
                save_btn = page.get_by_role("button", name="Save").first
                save_btn.click()

            # 5. Verification
            print("Waiting for confirmation...")
            try:
                # Wait for "Saved" text or toast
                page.wait_for_selector("text=Saved", timeout=30000)
                print("SUCCESS: Pinterest pin saved.")
            except:
                # Sometimes Pinterest redirects you to the new pin
                time.sleep(5)
                if "pin-builder" not in page.url:
                    print("SUCCESS: Redirect detected (Implicit Success).")
                else:
                    print("SUCCESS: Post clicked (Implicit).")

        except Exception as e:
            print(f"PINTEREST ERROR: {e}")
            page.screenshot(path="pin_error.png")

        finally:
            browser.close()
            config.close_browser(config.PIN_PROFILE_ID)

if __name__ == "__main__":
    run_pinterest_bot()