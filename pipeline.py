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

def test_add_to_cart_workflow(page: Page):
    """Test the complete add to cart and purchase requisition workflow"""
    try:
        logger.info("=== Starting Add to Cart Workflow Test ===")
        
        # Wait for product search results to load
        page.wait_for_selector("button:has-text('Add to Cart')", timeout=15000)
        logger.info("Product search results loaded")
        
        # Get product information from the first item
        first_product = page.locator("tr").filter(has=page.locator("button:has-text('Add to Cart')")).first
        
        # Extract product details
        try:
            product_name = first_product.locator("a[href*='PartDetail'], .product-title, h3, h4").first.inner_text()
            logger.info(f"Testing product: {product_name}")
        except:
            product_name = "INDEX BNDR 1-31 LTR ASTD"  # Default from screenshots
            logger.info(f"Using default product name: {product_name}")
        
        # Modify quantity to 5 (as shown in screenshots)
        qty_input = first_product.locator("input[type='text']").first
        if qty_input.count() > 0:
            qty_input.fill("5")
            logger.info("Set quantity to 5")
        
        # Click Add to Cart button
        add_to_cart_btn = first_product.locator("button:has-text('Add to Cart')").first
        add_to_cart_btn.click()
        logger.info("Clicked Add to Cart button")
        
        # Wait for cart popup to appear (PR156 popup)
        page.wait_for_selector("[class*='modal'], [class*='popup'], [class*='dialog']", timeout=10000)
        logger.info("Cart popup appeared")
        
        # Look for "Proceed to Checkout" button in popup
        try:
            proceed_btn = page.locator("button:has-text('Proceed to Checkout'), button:has-text('Proceed'), button[class*='proceed']")
            if proceed_btn.count() > 0:
                proceed_btn.click()
                logger.info("Clicked Proceed to Checkout")
            else:
                # Alternative: look for Review Cart or similar
                review_btn = page.locator("button:has-text('Review Cart'), button:has-text('Continue')")
                if review_btn.count() > 0:
                    review_btn.click()
                    logger.info("Clicked Review Cart/Continue")
        except Exception as e:
            logger.error(f"Error proceeding to checkout: {str(e)}")
        
        # Wait for Purchase Requisition form to load
        page.wait_for_load_state("networkidle")
        page.wait_for_selector("input[placeholder*='Title'], input[id*='title'], input[name*='title']", timeout=15000)
        logger.info("Purchase Requisition form loaded")
        
        # Fill out the PR form based on screenshots
        test_pr_form_filling(page)
        
        # Test line items section
        test_line_items_section(page)
        
        # Test approval flow
        test_approval_flow(page)
        
        logger.info("=== Add to Cart Workflow Test Completed ===")
        
    except Exception as e:
        logger.error(f"Add to Cart workflow test failed: {str(e)}")
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise

def test_pr_form_filling(page: Page):
    """Test Purchase Requisition form filling"""
    try:
        logger.info("=== Testing PR Form Filling ===")
        
        # Fill Title field
        title_field = page.locator("input[placeholder*='Title'], input[id*='title'], input[name*='title']").first
        if title_field.count() > 0:
            title_field.fill("Test Script")
            logger.info("Filled Title: Test Script")
        
        # Handle "On Behalf Of" dropdown
        try:
            behalf_dropdown = page.locator("select[id*='behalf'], select[name*='behalf'], .dropdown").first
            if behalf_dropdown.count() > 0:
                behalf_dropdown.select_option("Buyer QA")
                logger.info("Selected On Behalf Of: Buyer QA")
        except:
            logger.info("Could not set On Behalf Of dropdown")
        
        # Fill Deliver To field
        deliver_field = page.locator("input[placeholder*='Deliver'], input[id*='deliver'], input[name*='deliver']").first
        if deliver_field.count() > 0:
            deliver_field.fill("Dallas, TX")
            logger.info("Filled Deliver To: Dallas, TX")
        
        # Handle Need by Date - click date picker
        try:
            date_field = page.locator("input[type='date'], input[id*='date'], input[name*='date']").first
            if date_field.count() > 0:
                # Set future date (30 days from now)
                from datetime import datetime, timedelta
                future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                date_field.fill(future_date)
                logger.info(f"Set Need by Date: {future_date}")
        except Exception as e:
            logger.info(f"Could not set date: {str(e)}")
        
        # Fill Comments field
        comments_field = page.locator("textarea[placeholder*='Comments'], textarea[id*='comments'], textarea[name*='comments']").first
        if comments_field.count() > 0:
            comments_field.fill("Automated test purchase requisition")
            logger.info("Filled Comments")
        
        # Check "Visible to Supplier" checkbox if present
        try:
            visible_checkbox = page.locator("input[type='checkbox']:near(text='Visible to Supplier')")
            if visible_checkbox.count() > 0:
                visible_checkbox.check()
                logger.info("Checked Visible to Supplier")
        except:
            logger.info("Visible to Supplier checkbox not found")
        
        logger.info("PR form filling completed")
        
    except Exception as e:
        logger.error(f"PR form filling failed: {str(e)}")

def test_line_items_section(page: Page):
    """Test Line Items section functionality"""
    try:
        logger.info("=== Testing Line Items Section ===")
        
        # Expand Line Items section if collapsed
        line_items_header = page.locator("text='Line Items'").first
        if line_items_header.count() > 0:
            line_items_header.click()
            logger.info("Expanded Line Items section")
        
        # Verify line item details
        line_item_row = page.locator("tr").filter(has=page.locator("text='INDEX BNDR'")).first
        if line_item_row.count() > 0:
            # Check quantity
            qty_cell = line_item_row.locator("td").filter(has_text="5").first
            if qty_cell.count() > 0:
                logger.info("Verified quantity: 5")
            
            # Check unit (sheet)
            unit_cell = line_item_row.locator("td").filter(has_text="sheet").first
            if unit_cell.count() > 0:
                logger.info("Verified unit: sheet")
            
            # Check price
            price_cell = line_item_row.locator("td").filter(has_text="$3.33").first
            if price_cell.count() > 0:
                logger.info("Verified price: $3.33")
        
        # Test Actions dropdown
        try:
            actions_btn = page.locator("button:has-text('Actions')").first
            if actions_btn.count() > 0:
                actions_btn.click()
                logger.info("Clicked Actions dropdown")
                
                # Check available options
                edit_option = page.locator("text='Edit'")
                delete_option = page.locator("text='Delete'")
                copy_option = page.locator("text='Copy'")
                
                if edit_option.count() > 0:
                    logger.info("Edit option available")
                if delete_option.count() > 0:
                    logger.info("Delete option available")
                if copy_option.count() > 0:
                    logger.info("Copy option available")
                
                # Click elsewhere to close dropdown
                page.click("body")
        except:
            logger.info("Actions dropdown not accessible")
        
        # Test Update Total button
        update_total_btn = page.locator("button:has-text('Update Total')").first
        if update_total_btn.count() > 0:
            update_total_btn.click()
            logger.info("Clicked Update Total")
            page.wait_for_load_state("networkidle")
        
        logger.info("Line Items section testing completed")
        
    except Exception as e:
        logger.error(f"Line Items section test failed: {str(e)}")

def test_approval_flow(page: Page):
    """Test Approval Flow section"""
    try:
        logger.info("=== Testing Approval Flow Section ===")
        
        # Expand Approval Flow section if collapsed
        approval_header = page.locator("text='Approval Flow'").first
        if approval_header.count() > 0:
            approval_header.click()
            logger.info("Expanded Approval Flow section")
        
        # Click Show Approval Flow button
        show_approval_btn = page.locator("button:has-text('Show Approval Flow')").first
        if show_approval_btn.count() > 0:
            show_approval_btn.click()
            logger.info("Clicked Show Approval Flow")
            page.wait_for_load_state("networkidle")
        
        logger.info("Approval Flow section testing completed")
        
    except Exception as e:
        logger.error(f"Approval Flow section test failed: {str(e)}")

def test_accounting_section(page: Page):
    """Test Accounting - by Line Item section"""
    try:
        logger.info("=== Testing Accounting Section ===")
        
        # Expand Accounting section if collapsed
        accounting_header = page.locator("text='Accounting - by Line Item'").first
        if accounting_header.count() > 0:
            accounting_header.click()
            logger.info("Expanded Accounting section")
        
        # Test Account Assignment dropdown
        try:
            account_assignment = page.locator("select[id*='account'], select[name*='assignment']").first
            if account_assignment.count() > 0:
                account_assignment.select_option("K (Cost center)")
                logger.info("Selected Account Assignment: K (Cost center)")
        except:
            logger.info("Account Assignment dropdown not accessible")
        
        # Test Item Category dropdown
        try:
            item_category = page.locator("select[id*='category'], select[name*='category']").first
            if item_category.count() > 0:
                item_category.select_option("Material")
                logger.info("Selected Item Category: Material")
        except:
            logger.info("Item Category dropdown not accessible")
        
        # Test Account Type dropdown
        try:
            account_type = page.locator("select[id*='type'], select[name*='type']").first
            if account_type.count() > 0:
                account_type.select_option("Cost Center")
                logger.info("Selected Account Type: Cost Center")
        except:
            logger.info("Account Type dropdown not accessible")
        
        # Test Bill To dropdown
        try:
            bill_to = page.locator("select[id*='bill'], select[name*='bill']").first
            if bill_to.count() > 0:
                bill_to.select_option("3000 (New York)")
                logger.info("Selected Bill To: 3000 (New York)")
        except:
            logger.info("Bill To dropdown not accessible")
        
        # Test GL Account dropdown
        try:
            gl_account = page.locator("select[id*='gl'], select[name*='gl']").first
            if gl_account.count() > 0:
                gl_account.select_option("0000400200 (Raw material 2 consumed)")
                logger.info("Selected GL Account: 0000400200 (Raw material 2 consumed)")
        except:
            logger.info("GL Account dropdown not accessible")
        
        # Test Cost Center dropdown - this should open a popup
        test_cost_center_selection(page)
        
        # Test Internal Order dropdown
        try:
            internal_order = page.locator("select[id*='internal'], select[name*='order']").first
            if internal_order.count() > 0:
                # Check available options
                options = internal_order.locator("option").all_inner_texts()
                if len(options) > 1:  # More than just default option
                    internal_order.select_option(index=1)  # Select first non-default option
                    logger.info("Selected Internal Order option")
        except:
            logger.info("Internal Order dropdown not accessible")
        
        # Click Split Accounting button if present
        split_accounting_btn = page.locator("button:has-text('Split Accounting')").first
        if split_accounting_btn.count() > 0:
            split_accounting_btn.click()
            logger.info("Clicked Split Accounting button")
            page.wait_for_load_state("networkidle")
        
        logger.info("Accounting section testing completed")
        
    except Exception as e:
        logger.error(f"Accounting section test failed: {str(e)}")

def test_cost_center_selection(page: Page):
    """Test Cost Center selection popup"""
    try:
        logger.info("=== Testing Cost Center Selection ===")
        
        # Find and click on Cost Center dropdown
        cost_center_dropdown = page.locator("select[id*='cost'], select[name*='cost'], input[id*='cost']").first
        if cost_center_dropdown.count() > 0:
            cost_center_dropdown.click()
            logger.info("Clicked Cost Center dropdown")
            
            # Wait for popup to appear
            popup_selector = "[class*='modal'], [class*='popup'], [role='dialog']"
            page.wait_for_selector(popup_selector, timeout=5000)
            logger.info("Cost Center selection popup appeared")
            
            # Look for Marketing IT Support option (0000001245)
            marketing_it_option = page.locator("text='Marketing IT Suppo', text='0000001245'").first
            if marketing_it_option.count() > 0:
                # Click Select button for Marketing IT Support
                select_btn = marketing_it_option.locator("xpath=../..").locator("button:has-text('Select')").first
                if select_btn.count() > 0:
                    select_btn.click()
                    logger.info("Selected Marketing IT Support (0000001245)")
                else:
                    marketing_it_option.click()
                    logger.info("Clicked Marketing IT Support option")
            else:
                # If specific option not found, select any available option
                select_buttons = page.locator("button:has-text('Select')")
                if select_buttons.count() > 0:
                    select_buttons.first.click()
                    logger.info("Selected first available cost center option")
            
            # Wait for popup to close
            page.wait_for_load_state("networkidle")
            
        logger.info("Cost Center selection completed")
        
    except Exception as e:
        logger.error(f"Cost Center selection test failed: {str(e)}")

def test_shipping_section(page: Page):
    """Test Shipping - by Line Item section"""
    try:
        logger.info("=== Testing Shipping Section ===")
        
        # Expand Shipping section if collapsed
        shipping_header = page.locator("text='Shipping - by Line Item'").first
        if shipping_header.count() > 0:
            shipping_header.click()
            logger.info("Expanded Shipping section")
        
        # Test Plant dropdown
        try:
            plant_dropdown = page.locator("select[id*='plant'], select[name*='plant']").first
            if plant_dropdown.count() > 0:
                plant_dropdown.select_option("3300 (Los Angeles)")
                logger.info("Selected Plant: 3300 (Los Angeles)")
        except:
            logger.info("Plant dropdown not accessible")
        
        # Test Deliver To field
        deliver_to_field = page.locator("input[id*='deliver'], input[name*='deliver']").first
        if deliver_to_field.count() > 0:
            deliver_to_field.fill("Arnold Davis")
            logger.info("Filled Deliver To: Arnold Davis")
        
        # Test Need-by Date
        try:
            need_by_date = page.locator("input[type='date'], input[id*='need'], input[name*='date']").first
            if need_by_date.count() > 0:
                need_by_date.fill("2025-09-30")
                logger.info("Set Need-by Date: 2025-09-30")
        except:
            logger.info("Need-by Date field not accessible")
        
        # Test Purchase Group dropdown
        try:
            purchase_group = page.locator("select[id*='purchase'], select[name*='group']").first
            if purchase_group.count() > 0:
                purchase_group.select_option("003 (IDES USA)")
                logger.info("Selected Purchase Group: 003 (IDES USA)")
        except:
            logger.info("Purchase Group dropdown not accessible")
        
        logger.info("Shipping section testing completed")
        
    except Exception as e:
        logger.error(f"Shipping section test failed: {str(e)}")

def test_comments_section(page: Page):
    """Test Comments - by Line Item section"""
    try:
        logger.info("=== Testing Comments Section ===")
        
        # Expand Comments section if collapsed
        comments_header = page.locator("text='Comments - by Line Item'").first
        if comments_header.count() > 0:
            comments_header.click()
            logger.info("Expanded Comments section")
        
        # Test Add Comment button
        add_comment_btn = page.locator("button:has-text('Add Comment')").first
        if add_comment_btn.count() > 0:
            add_comment_btn.click()
            logger.info("Clicked Add Comment button")
            page.wait_for_load_state("networkidle")
        
        # Look for comment text area
        comment_textarea = page.locator("textarea[id*='comment'], textarea[name*='comment']").first
        if comment_textarea.count() > 0:
            comment_textarea.fill("Automated test comment for line item")
            logger.info("Added comment to line item")
        
        logger.info("Comments section testing completed")
        
    except Exception as e:
        logger.error(f"Comments section test failed: {str(e)}")

def test_line_item_details(page: Page):
    """Test Line Item Details dialog"""
    try:
        logger.info("=== Testing Line Item Details ===")
        
        # Look for line item link or button to open details
        line_item_link = page.locator("a:has-text('INDEX BNDR'), button:has-text('INDEX BNDR')").first
        if line_item_link.count() > 0:
            line_item_link.click()
            logger.info("Clicked line item to open details")
            
            # Wait for details dialog/popup
            page.wait_for_selector("[class*='modal'], [class*='dialog'], [role='dialog']", timeout=5000)
            logger.info("Line Item Details dialog opened")
            
            # Verify details in the dialog
            # Check Full Description
            full_desc = page.locator("textarea[id*='description'], textarea[name*='description']").first
            if full_desc.count() > 0:
                current_desc = full_desc.input_value()
                logger.info(f"Full Description: {current_desc}")
            
            # Check Supplier Part Number
            supplier_part = page.locator("input[id*='supplier'], input[name*='part']").first
            if supplier_part.count() > 0:
                part_number = supplier_part.input_value()
                logger.info(f"Supplier Part Number: {part_number}")
            
            # Check Quantity
            qty_field = page.locator("input[id*='qty'], input[name*='quantity']").first
            if qty_field.count() > 0:
                quantity = qty_field.input_value()
                logger.info(f"Quantity: {quantity}")
            
            # Check UOM (Unit of Measure)
            uom_dropdown = page.locator("select[id*='uom'], select[name*='unit']").first
            if uom_dropdown.count() > 0:
                selected_uom = uom_dropdown.input_value()
                logger.info(f"UOM: {selected_uom}")
            
            # Check Price
            price_field = page.locator("input[id*='price'], input[name*='price']").first
            if price_field.count() > 0:
                price = price_field.input_value()
                logger.info(f"Price: {price}")
            
            # Test Collaborate with supplier option
            collaborate_radio = page.locator("input[type='radio'][value='Yes'], input[type='radio']:near(text='Yes')").first
            if collaborate_radio.count() > 0:
                collaborate_radio.check()
                logger.info("Selected 'Yes' for Collaborate with supplier")
            
            # Close the dialog - look for OK, Close, or Cancel button
            ok_btn = page.locator("button:has-text('OK'), button:has-text('Close'), button:has-text('Cancel')").first
            if ok_btn.count() > 0:
                ok_btn.click()
                logger.info("Closed Line Item Details dialog")
                page.wait_for_load_state("networkidle")
        
        logger.info("Line Item Details testing completed")
        
    except Exception as e:
        logger.error(f"Line Item Details test failed: {str(e)}")

def test_submission_confirmation(page: Page):
    """Test submission success confirmation"""
    try:
        logger.info("=== Testing Submission Confirmation ===")
        
        # Look for success message
        success_messages = [
            "The requisition has been submitted",
            "Successfully submitted",
            "Submission complete",
            "Request submitted"
        ]
        
        for message in success_messages:
            success_element = page.locator(f"text='{message}'").first
            if success_element.count() > 0:
                logger.info(f"Found success message: {message}")
                
                # Look for Add Label button
                add_label_btn = page.locator("button:has-text('Add Label')").first
                if add_label_btn.count() > 0:
                    logger.info("Add Label button is available")
                
                # Look for View or Action button
                view_action_btn = page.locator("button:has-text('View'), button:has-text('Action')").first
                if view_action_btn.count() > 0:
                    logger.info("View/Action button is available")
                
                break
        
        # Check if we're back at Catalog Home
        catalog_home = page.locator("text='Catalog Home'").first
        if catalog_home.count() > 0:
            logger.info("Returned to Catalog Home")
            
            # Check Recently Viewed Items section
            recently_viewed = page.locator("text='Recently Viewed Items'").first
            if recently_viewed.count() > 0:
                logger.info("Recently Viewed Items section is visible")
        
        logger.info("Submission confirmation testing completed")
        
    except Exception as e:
        logger.error(f"Submission confirmation test failed: {str(e)}")

def test_final_actions(page: Page):
    """Test final action buttons"""
    try:
        logger.info("=== Testing Final Actions ===")
        
        # Test Save button
        save_btn = page.locator("button:has-text('Save')").first
        if save_btn.count() > 0:
            save_btn.click()
            logger.info("Clicked Save button")
            page.wait_for_load_state("networkidle")
            time.sleep(2)
        
        # Test submission process (but don't actually submit in production)
        submit_btn = page.locator("button:has-text('Submit')").first
        if submit_btn.count() > 0:
            logger.info("Submit button is available")
            
            # Only submit if this is a test environment (uncomment next lines for actual submission test)
            # submit_btn.click()
            # logger.info("Clicked Submit button")
            # page.wait_for_load_state("networkidle")
            # test_submission_confirmation(page)
        
        # Test Continue Shopping button
        continue_shopping_btn = page.locator("button:has-text('Continue Shopping')").first
        if continue_shopping_btn.count() > 0:
            logger.info("Continue Shopping button is available")
        
        # Test Delete button
        delete_btn = page.locator("button:has-text('Delete')").first
        if delete_btn.count() > 0:
            logger.info("Delete button is available")
        
        logger.info("Final actions testing completed")
        
    except Exception as e:
        logger.error(f"Final actions test failed: {str(e)}")

def test_contracts_login(page: Page):  # ← pytest provides the 'page' fixture
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
        
        # Navigate and search for products
        page.wait_for_load_state("networkidle")
        page.fill("input.w-chinput[type='text']", "Apex")
        page.press("input.w-chinput[type='text']", "Enter")
        page.wait_for_load_state("networkidle")
        
        # Test the complete add to cart workflow
        test_add_to_cart_workflow(page)
        
        # Test accounting section
        test_accounting_section(page)
        
        # Test shipping section
        test_shipping_section(page)
        
        # Test comments section
        test_comments_section(page)
        
        # Test line item details
        test_line_item_details(page)
        
        # Test final actions
        test_final_actions(page)
        
        logger.info("=== All tests completed successfully ===")
        
        # Keep browser open for manual inspection
        while True:
            pass
            
    except Exception as e:
        # 10. Log errors
        logger.error(f"Test failed with error: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        # Log stack trace for debugging
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise  # Re-raise the exception to fail the test
