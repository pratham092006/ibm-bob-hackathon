"""
GitHub Search Automation Script
================================
A clean, modular Playwright automation example for the AXON project.

This script demonstrates automated browser interaction by:
1. Navigating to GitHub
2. Searching for "React"
3. Sorting results by "Most stars"

Usage:
    python axon/github_search_automation.py

Requirements:
    - playwright>=1.40.0
    - Run 'playwright install chromium' after installing playwright
"""

import asyncio
import time
from playwright.async_api import async_playwright, Page, Browser, Playwright


async def launch_browser(playwright: Playwright) -> Browser:
    """
    Launch a visible Chrome/Chromium browser instance.
    
    Args:
        playwright: Playwright instance
        
    Returns:
        Browser: Launched browser instance
    """
    print("[*] Launching Chrome browser...")
    browser = await playwright.chromium.launch(
        headless=False,  # Visible browser
        slow_mo=500      # Slow down actions for visibility
    )
    return browser


async def navigate_to_github(page: Page) -> None:
    """
    Navigate to GitHub homepage and wait for page to load.
    
    Args:
        page: Playwright page instance
    """
    print("[*] Navigating to GitHub...")
    await page.goto("https://github.com", wait_until="domcontentloaded")
    await page.wait_for_load_state("networkidle")
    print("[OK] GitHub homepage loaded")


async def search_for_react(page: Page) -> None:
    """
    Find the search bar, type "React", and submit the search.
    
    Args:
        page: Playwright page instance
    """
    print("[*] Searching for 'React'...")
    
    # Try multiple approaches to find and use the search
    try:
        # Approach 1: Try the search button/trigger
        search_trigger = page.locator('button[data-target="qbsearch-input.inputButtonText"]')
        await search_trigger.wait_for(state="visible", timeout=5000)
        await search_trigger.click()
        
        # Wait for the search input to appear
        search_input = page.locator('#query-builder-test')
        await search_input.wait_for(state="visible", timeout=5000)
        await search_input.fill("React")
        await search_input.press("Enter")
        
    except Exception as e:
        print(f"[*] First approach failed, trying alternative method: {str(e)[:50]}...")
        
        # Approach 2: Try direct search input (fallback)
        # Press "/" to open search (GitHub keyboard shortcut)
        await page.keyboard.press("/")
        await page.wait_for_timeout(1000)
        
        # Type in the search query
        await page.keyboard.type("React")
        await page.keyboard.press("Enter")
    
    # Wait for search results page to load
    await page.wait_for_load_state("networkidle")
    print("[OK] Search results loaded")


async def sort_by_most_stars(page: Page) -> None:
    """
    Click the sort dropdown and select "Most stars" option.
    
    Args:
        page: Playwright page instance
    """
    print("[*] Sorting by most stars...")
    
    try:
        # Approach 1: Try the sort button and dropdown
        sort_button = page.locator('button:has-text("Sort")')
        await sort_button.wait_for(state="visible", timeout=10000)
        await sort_button.click()
        
        # Wait for dropdown menu to appear and click "Most stars"
        most_stars_option = page.locator('a[href*="sort=stars"]').first
        await most_stars_option.wait_for(state="visible", timeout=5000)
        await most_stars_option.click()
        
    except Exception as e:
        print(f"[*] Sort button approach failed, trying URL navigation: {str(e)[:50]}...")
        
        # Approach 2: Navigate directly to sorted URL
        current_url = page.url
        if '?' in current_url:
            sorted_url = current_url + '&s=stars&o=desc'
        else:
            sorted_url = current_url + '?s=stars&o=desc'
        
        await page.goto(sorted_url)
    
    # Wait for sorted results to load
    await page.wait_for_load_state("networkidle")
    print("[OK] Results sorted by most stars")


async def keep_browser_open(duration: int = 5) -> None:
    """
    Keep the browser open for a specified duration.
    
    Args:
        duration: Time in seconds to keep browser open
    """
    print(f"[*] Keeping browser open for {duration} seconds...")
    time.sleep(duration)


async def run_automation() -> None:
    """
    Main automation workflow that orchestrates all steps.
    """
    async with async_playwright() as playwright:
        browser = None
        try:
            # Step 1: Launch browser
            browser = await launch_browser(playwright)
            page = await browser.new_page()
            
            # Step 2: Navigate to GitHub
            await navigate_to_github(page)
            
            # Step 3: Search for "React"
            await search_for_react(page)
            
            # Step 4: Sort by most stars
            await sort_by_most_stars(page)
            
            # Step 5: Keep browser open
            await keep_browser_open(5)
            
            print("\n[SUCCESS] Automation completed successfully!")
            
        except Exception as e:
            print(f"\n[ERROR] Error during automation: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            raise
            
        finally:
            # Clean up: Close browser
            if browser:
                print("[*] Closing browser...")
                await browser.close()


def main():
    """
    Entry point for the script.
    """
    print("=" * 60)
    print("GitHub Search Automation - AXON Project")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(run_automation())
    except KeyboardInterrupt:
        print("\n[WARNING] Automation interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {str(e)}")
        raise


if __name__ == "__main__":
    main()

# Made with Bob
