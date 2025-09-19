from playwright.sync_api import sync_playwright
import pytest
from playwright.sync_api import Page, expect
from datetime import datetime
from common_env import (
    load_env, get_logger
)
today = datetime.now().strftime("%m/%d/%Y")
import time
from common_env import get_buyer_url, get_buyer_user, get_buyer_password
logger = get_logger(log_file="test.log")
load_env()
#from dotenv import load_dotenv
URL = get_buyer_url()
username = get_buyer_user()
password = get_buyer_password()

def test_contracts_login(page: Page):  # - pytest provides the 'page' fixture
    """Use the page fixture provided by pytest-playwright"""
    try:
        #
        logger.info("=== Starting Contracts Login Test ===")
        logger.info("Launching browser...")
        logger.info(f"Navigating to: {URL}")
        page.goto(URL, wait_until="domcontentloaded")
        logger.info("Filling login form...")
        page.wait_for_selector("input[name='UserName']", state="visible", timeout=15000)
        page.fill("input[name='UserName']", username)
        page.fill("input[name='Password']", password)
        page.locator("input[type='submit']").click()
        page.wait_for_load_state("networkidle")
        logger.info("Clicking Sign In button...")
        print("Logged in, Page title:", page.title())
        #page.click('button:has-text("OK")')
        #page.wait_for_load_state("networkidle")
        #page.wait_for_selector("#suuz").click()
        #page.get_by_role("link", name="Requisition").click()
        print(page.locator("input").all_text_contents())
        print(page.locator("input").all_inner_texts())
        print(page.locator("input").count())
        
        page.wait_for_load_state("networkidle")
        page.fill("input.w-chInput[type='text']", "Apex")
        page.press("input.w-chInput[type='text']", "Enter")
        page.wait_for_load_state("networkidle")
        
        # Set quantity to 5 and add to cart
        page.fill("input[type='text'][value='1']", "5")
        page.click("button.w-btn.w-btn-primary")
        page.wait_for_load_state("networkidle")
    except Exception as e:
        # 10. Log errors
        logger.error(f"Test failed with error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        # Log stack trace for debugging
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise  # Re-raise the exception to fail the test
