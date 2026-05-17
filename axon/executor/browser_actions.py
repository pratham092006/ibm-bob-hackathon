"""Browser automation module for AXON using Playwright.

Integrates Playwright browser automation into AXON's action system.
Provides high-level browser actions that can be called by the AI loop.

Author: Dev 2 (Ashish) - Executor & Safety
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, Playwright

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class BrowserAutomation:
    """Manages browser automation using Playwright.
    
    This class provides a singleton browser instance that can be controlled
    through AXON's action system. It maintains browser state across actions.
    """
    
    _instance = None
    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _page: Optional[Page] = None
    _loop: Optional[asyncio.AbstractEventLoop] = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one browser instance."""
        if cls._instance is None:
            cls._instance = super(BrowserAutomation, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize browser automation (only once due to singleton)."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            logger.info("BrowserAutomation initialized")
    
    async def _ensure_browser(self):
        """Ensure browser is launched and ready."""
        if self._browser is None or not self._browser.is_connected():
            logger.info("Launching browser...")
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(
                headless=False,  # Visible browser
                slow_mo=300      # Slow down for visibility
            )
            self._page = await self._browser.new_page()
            logger.info("Browser launched successfully")
    
    async def _ensure_page(self):
        """Ensure we have an active page."""
        await self._ensure_browser()
        if self._page is None or self._page.is_closed():
            self._page = await self._browser.new_page()
    
    async def navigate(self, url: str) -> bool:
        """Navigate to a URL.
        
        Args:
            url: The URL to navigate to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self._ensure_page()
            logger.info(f"Navigating to: {url}")
            await self._page.goto(url, wait_until="domcontentloaded")
            await self._page.wait_for_load_state("networkidle")
            logger.info(f"Successfully navigated to {url}")
            return True
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    async def click_element(self, selector: str, timeout: int = 10000) -> bool:
        """Click an element using a CSS selector.
        
        Args:
            selector: CSS selector for the element
            timeout: Maximum wait time in milliseconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self._ensure_page()
            logger.info(f"Clicking element: {selector}")
            element = self._page.locator(selector)
            await element.wait_for(state="visible", timeout=timeout)
            await element.click()
            logger.info(f"Successfully clicked: {selector}")
            return True
        except Exception as e:
            logger.error(f"Error clicking {selector}: {e}")
            return False
    
    async def type_text(self, selector: str, text: str, timeout: int = 10000) -> bool:
        """Type text into an element.
        
        Args:
            selector: CSS selector for the input element
            text: Text to type
            timeout: Maximum wait time in milliseconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self._ensure_page()
            logger.info(f"Typing into {selector}: {text}")
            element = self._page.locator(selector)
            await element.wait_for(state="visible", timeout=timeout)
            await element.fill(text)
            logger.info(f"Successfully typed into: {selector}")
            return True
        except Exception as e:
            logger.error(f"Error typing into {selector}: {e}")
            return False
    
    async def press_key(self, key: str) -> bool:
        """Press a keyboard key.
        
        Args:
            key: Key to press (e.g., 'Enter', 'Escape', '/')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self._ensure_page()
            logger.info(f"Pressing key: {key}")
            await self._page.keyboard.press(key)
            logger.info(f"Successfully pressed: {key}")
            return True
        except Exception as e:
            logger.error(f"Error pressing key {key}: {e}")
            return False
    
    async def wait_for_selector(self, selector: str, timeout: int = 10000) -> bool:
        """Wait for an element to appear.
        
        Args:
            selector: CSS selector for the element
            timeout: Maximum wait time in milliseconds
            
        Returns:
            bool: True if element appears, False otherwise
        """
        try:
            await self._ensure_page()
            logger.info(f"Waiting for selector: {selector}")
            await self._page.wait_for_selector(selector, timeout=timeout)
            logger.info(f"Selector found: {selector}")
            return True
        except Exception as e:
            logger.error(f"Timeout waiting for {selector}: {e}")
            return False
    
    async def get_text(self, selector: str) -> Optional[str]:
        """Get text content from an element.
        
        Args:
            selector: CSS selector for the element
            
        Returns:
            str: Text content or None if failed
        """
        try:
            await self._ensure_page()
            element = self._page.locator(selector)
            text = await element.text_content()
            logger.info(f"Got text from {selector}: {text[:50]}...")
            return text
        except Exception as e:
            logger.error(f"Error getting text from {selector}: {e}")
            return None
    
    async def screenshot(self, path: str) -> bool:
        """Take a screenshot of the current page.
        
        Args:
            path: File path to save screenshot
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            await self._ensure_page()
            logger.info(f"Taking screenshot: {path}")
            await self._page.screenshot(path=path)
            logger.info(f"Screenshot saved to: {path}")
            return True
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return False
    
    async def close_browser(self) -> bool:
        """Close the browser and cleanup resources.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self._browser:
                logger.info("Closing browser...")
                await self._browser.close()
                self._browser = None
                self._page = None
            if self._playwright:
                await self._playwright.stop()
                self._playwright = None
            logger.info("Browser closed successfully")
            return True
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
            return False


# Global browser instance
_browser_automation = BrowserAutomation()


def run_async(coro):
    """Helper to run async functions in sync context.
    
    Args:
        coro: Coroutine to run
        
    Returns:
        Result of the coroutine
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


# Synchronous wrappers for AXON's action system
def browser_navigate(url: str) -> bool:
    """Navigate to a URL (sync wrapper).
    
    Args:
        url: The URL to navigate to
        
    Returns:
        bool: True if successful, False otherwise
    """
    return run_async(_browser_automation.navigate(url))


def browser_click(selector: str, timeout: int = 10000) -> bool:
    """Click an element (sync wrapper).
    
    Args:
        selector: CSS selector for the element
        timeout: Maximum wait time in milliseconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    return run_async(_browser_automation.click_element(selector, timeout))


def browser_type(selector: str, text: str, timeout: int = 10000) -> bool:
    """Type text into an element (sync wrapper).
    
    Args:
        selector: CSS selector for the input element
        text: Text to type
        timeout: Maximum wait time in milliseconds
        
    Returns:
        bool: True if successful, False otherwise
    """
    return run_async(_browser_automation.type_text(selector, text, timeout))


def browser_press_key(key: str) -> bool:
    """Press a keyboard key (sync wrapper).
    
    Args:
        key: Key to press (e.g., 'Enter', 'Escape', '/')
        
    Returns:
        bool: True if successful, False otherwise
    """
    return run_async(_browser_automation.press_key(key))


def browser_wait(selector: str, timeout: int = 10000) -> bool:
    """Wait for an element to appear (sync wrapper).
    
    Args:
        selector: CSS selector for the element
        timeout: Maximum wait time in milliseconds
        
    Returns:
        bool: True if element appears, False otherwise
    """
    return run_async(_browser_automation.wait_for_selector(selector, timeout))


def browser_get_text(selector: str) -> Optional[str]:
    """Get text content from an element (sync wrapper).
    
    Args:
        selector: CSS selector for the element
        
    Returns:
        str: Text content or None if failed
    """
    return run_async(_browser_automation.get_text(selector))


def browser_screenshot(path: str) -> bool:
    """Take a screenshot (sync wrapper).
    
    Args:
        path: File path to save screenshot
        
    Returns:
        bool: True if successful, False otherwise
    """
    return run_async(_browser_automation.screenshot(path))


def browser_close() -> bool:
    """Close the browser (sync wrapper).
    
    Returns:
        bool: True if successful, False otherwise
    """
    return run_async(_browser_automation.close_browser())

# Made with Bob
