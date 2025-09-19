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

URL = get_buyer_url()
username = get_buyer_user()
password = get_buyer_password()

def test_contracts_login(page: Page):
    """Simple test based on working code"""
    try:
        # Login
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
        
        # Search for Apex - simple working version
        page.wait_for_load_state("networkidle")
        page.fill("input.w-chinput[type='text']", "Apex")
        page.press("input.w-chinput[type='text']", "Enter")
        page.wait_for_load_state("networkidle")
        logger.info("Searched for Apex")
        
        # Add to Cart
        test_add_to_cart(page)
        
        # Fill Purchase Requisition
        test_purchase_requisition(page)
        
        # Test other sections
        test_line_items(page)
        test_accounting(page)
        test_shipping(page)
        test_final_actions(page)
        
        # Keep browser open
        while True:
            pass
            
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise

def test_add_to_cart(page: Page):
    """Simple add to cart test"""
    try:
        logger.info("=== Testing Add to Cart ===")
        
        # Wait for Add to Cart button
        page.wait_for_selector("button.w-btn.w-btn-primary.w-btn-small", timeout=10000)
        logger.info("Found Add to Cart button")
        
        # Set quantity to 5
        qty_input = page.locator("input[type='text']").first
        if qty_input.count() > 0:
            qty_input.fill("5")
            logger.info("Set quantity to 5")
        
        # Click Add to Cart
        page.locator("button.w-btn.w-btn-primary.w-btn-small").first.click()
        logger.info("Clicked Add to Cart")
        
        # Wait for cart popup and proceed
        time.sleep(2)
        proceed_btn = page.locator("a#checkout")
        if proceed_btn.count() > 0:
            proceed_btn.click()
            logger.info("Clicked Proceed to Checkout")
        
        page.wait_for_load_state("networkidle")
        logger.info("Add to Cart completed")
        
    except Exception as e:
        logger.error(f"Add to Cart failed: {str(e)}")

def test_purchase_requisition(page: Page):
    """Test PR form filling"""
    try:
        logger.info("=== Testing Purchase Requisition Form ===")
        
        # Fill Title
        title_input = page.locator("input[id*='title'], input[name*='title']").first
        if title_input.count() > 0:
            title_input.fill("Test Script")
            logger.info("Filled Title")
        
        # Fill Deliver To
        deliver_input = page.locator("input[id*='deliver'], input[name*='deliver']").first
        if deliver_input.count() > 0:
            deliver_input.fill("Dallas, TX")
            logger.info("Filled Deliver To")
        
        # Fill Comments
        comments_input = page.locator("textarea[id*='comment'], textarea[name*='comment']").first
        if comments_input.count() > 0:
            comments_input.fill("Automated test purchase requisition")
            logger.info("Filled Comments")
        
        logger.info("Purchase Requisition form completed")
        
    except Exception as e:
        logger.error(f"Purchase Requisition failed: {str(e)}")

def test_line_items(page: Page):
    """Test Line Items section"""
    try:
        logger.info("=== Testing Line Items ===")
        
        # Expand Line Items if needed
        line_items_header = page.locator("text='Line Items'").first
        if line_items_header.count() > 0:
            line_items_header.click()
            logger.info("Expanded Line Items")
        
        # Test Update Total button
        update_btn = page.locator("button:has-text('Update Total')").first
        if update_btn.count() > 0:
            update_btn.click()
            logger.info("Clicked Update Total")
            page.wait_for_load_state("networkidle")
        
        logger.info("Line Items testing completed")
        
    except Exception as e:
        logger.error(f"Line Items failed: {str(e)}")

def test_accounting(page: Page):
    """Test Accounting section"""
    try:
        logger.info("=== Testing Accounting ===")
        
        # Expand Accounting section
        accounting_header = page.locator("text='Accounting - by Line Item'").first
        if accounting_header.count() > 0:
            accounting_header.click()
            logger.info("Expanded Accounting section")
        
        # Set Account Assignment
        account_dropdown = page.locator("select[id*='account']").first
        if account_dropdown.count() > 0:
            account_dropdown.select_option("K (Cost center)")
            logger.info("Selected Account Assignment")
        
        # Set Cost Center
        cost_center_input = page.locator("select[id*='cost'], input[id*='cost']").first
        if cost_center_input.count() > 0:
            cost_center_input.click()
            # If popup appears, select first option
            time.sleep(1)
            select_btn = page.locator("button:has-text('Select')").first
            if select_btn.count() > 0:
                select_btn.click()
                logger.info("Selected Cost Center")
        
        logger.info("Accounting testing completed")
        
    except Exception as e:
        logger.error(f"Accounting failed: {str(e)}")

def test_shipping(page: Page):
    """Test Shipping section"""
    try:
        logger.info("=== Testing Shipping ===")
        
        # Expand Shipping section
        shipping_header = page.locator("text='Shipping - by Line Item'").first
        if shipping_header.count() > 0:
            shipping_header.click()
            logger.info("Expanded Shipping section")
        
        # Set Plant
        plant_dropdown = page.locator("select[id*='plant']").first
        if plant_dropdown.count() > 0:
            plant_dropdown.select_option("3300 (Los Angeles)")
            logger.info("Selected Plant")
        
        # Set Deliver To
        deliver_input = page.locator("input[id*='deliver']").first
        if deliver_input.count() > 0:
            deliver_input.fill("Arnold Davis")
            logger.info("Filled Deliver To")
        
        logger.info("Shipping testing completed")
        
    except Exception as e:
        logger.error(f"Shipping failed: {str(e)}")

def test_final_actions(page: Page):
    """Test final buttons"""
    try:
        logger.info("=== Testing Final Actions ===")
        
        # Save button
        save_btn = page.locator("button:has-text('Save')").first
        if save_btn.count() > 0:
            save_btn.click()
            logger.info("Clicked Save")
            page.wait_for_load_state("networkidle")
        
        # Check Submit button (don't click)
        submit_btn = page.locator("button:has-text('Submit')").first
        if submit_btn.count() > 0:
            logger.info("Submit button found (not clicking)")
        
        logger.info("Final actions completed")
        
    except Exception as e:
        logger.error(f"Final actions failed: {str(e)}")
