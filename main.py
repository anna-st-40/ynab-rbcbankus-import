from playwright.sync_api import sync_playwright, Playwright
import json
from datetime import datetime, timedelta
import os
import traceback
from time import sleep

def fetch_rbc_credentials(file_path):
    """Fetch RBC credentials from a JSON file."""

    with open(file_path, 'r') as file:
        data = json.load(file)['RBC']
        return data['username'], data['password']

def fetch_rbc_security_question(file_path, question):
    """Fetch security question answers from a JSON file."""

    with open(file_path, 'r') as file:
        data = json.load(file)["RBC"]["security-questions"]
        return data[question]

def fetch_ynab_credentials(file_path):
    """Fetch YNAB credentials from a JSON file."""

    with open(file_path, 'r') as file:
        data = json.load(file)['YNAB']
        return data['email'], data['password']

def fetch_ynab_ids(file_path):
    """Fetch YNAB budget & account IDS from a JSON file."""

    with open(file_path, 'r') as file:
        data = json.load(file)
        return data['budget-id'], data['account-id']

def get_transactions(playwright: Playwright, credentials_path, download_path):
    try:
        # Launch browser
        browser = playwright.chromium.launch()
        page = browser.new_page()

        # Navigate to bank login page
        page.goto("https://www1.rbcbank.com/cgi-bin/rbaccess/rbunxcgi?F6=1&F7=NS&F21=IB&F22=CN&REQUEST=CenturaClientSignin&LANGUAGE=ENGLISH")

        # Perform login
        username, password = fetch_rbc_credentials(credentials_path)
        page.fill("#K1", username)
        page.fill("#Q1", password)
        page.click('input[name="Sign In"]')
        page.screenshot(path="1.png")

        # Answer security questions
        question = page.inner_html('label[for="USERID"]')
        answer = fetch_rbc_security_question(credentials_path, question)
        page.fill("#pvqAnswer", answer)
        page.click('input[name="continue"]')
        page.screenshot(path="2.png")

        # Handle "Sign-in Protection Alert" if needed
        if page.query_selector('h1:has-text("Sign-in Protection Alert")'):
            page.screenshot(path="sign-in-protection.png")
            page.click('input[name="keep"]')
            print("Sign-in Protection Alert has been triggered. A screenshot has been taken and saved at sign-in-protection.png")

        # Navigate to transaction download
        page.click(".account-card-name")
        page.click(".download-activity")
        page.screenshot(path="3.png")

        # Get dates
        with open('last_imported.txt') as f:
            last_imported_date = f.read().strip()
        tomorrow_date = (datetime.today() + timedelta(days=1)).strftime('%Y-%m-%d')

        # Fill out download form
        page.fill("#formInputStartDate", last_imported_date)
        page.fill("#formInputEndDate", tomorrow_date)
        page.click("#formInputFormatTypeQuicken")
        page.screenshot(path="4.png")

        # Click the button that triggers the download
        with page.expect_download() as download_info:
            page.click("#submitButton")
        
        # Save the download
        download = download_info.value
        global download_filename
        download_filename = download.suggested_filename
        download.save_as(os.path.join(download_path, download_filename))
        print(f"Downloaded file saved as: {os.path.join(download_path, download.suggested_filename)}")

    except:
        # Take a screenshot if an error occurs
        page.screenshot(path="rbc_error.png")
        print("Something went wrong with the RBC part.")
        print(traceback.format_exc())

    finally:
        browser.close()

def upload_to_ynab(playwright: Playwright, credentials_path, transactions_filename, budget_id, account_id):
    try:
        # Launch browser
        browser = playwright.chromium.launch()
        page = browser.new_page()

        # Navigate to YNAB login page
        page.goto(f"https://app.ynab.com/{budget_id}/accounts/{account_id}")

        # Perform login
        email, password = fetch_ynab_credentials(credentials_path)
        page.fill("#request_data_email", email)
        page.fill("#request_data_password", password)
        page.click('#login')

        sleep(5)
        page.screenshot(path="a.png")

        # Import file
        page.click(".accounts-toolbar-file-import-transactions")
        page.set_input_files('input[type="file"]', os.path.join('transaction_downloads', transactions_filename))
        sleep(5)
        page.screenshot(path="b.png")
        page.click('.modal-overlay.active button:text("Import")')

        # Check that import was successful
        if page.query_selector('div:text("Import Successful")'):
            page.click('.modal-overlay.active button:text("OK")')
            page.screenshot(path="success.png")
        else:
            page.screenshot(path="error.png")
            print(f'Did not get "Import Successful" message. Please see screenshot error.png')
        
    except:
        # Take a screenshot if an error occurs
        page.screenshot(path="ynab_error.png")
        print("Something went wrong with the YNAB part.")
        print(traceback.format_exc())

    finally:
        browser.close()

with sync_playwright() as playwright:
    budget_id, account_id = fetch_ynab_ids("secret.json")
    download_path = os.path.join(os.getcwd(), 'transaction_downloads')
    get_transactions(playwright, "secret.json", download_path)
    upload_to_ynab(playwright, "secret.json", download_filename, budget_id, account_id)