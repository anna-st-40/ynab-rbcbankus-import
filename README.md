# RBC Bank (U.S) to YNAB

This Python script automatically pushes transactions from your RBC Bank (U.S) account to YNAB budgeting software, using the Playwright library for web automation.

## Features

- **Automated Transaction Import**: Fetches transactions from RBC and imports them into YNAB.
- **Secure Credentials Handling**: Utilizes a JSON file to locally store and manage your RBC and YNAB credentials.

## Getting Started

### Prerequisites

- Python 3.x
- Playwright library - https://playwright.dev/python/docs/intro

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/anna-st-40/ynab-rbcbankus-import
   cd ynab-rbcbankus-import
   ```

2. **Install Playwright**
   ```bash
   pip install playwright==1.44.0
   playwright install
   ```

3. **Set up your credentials**

   Create a `secret.json` file in the project directory with the following structure (also supplied in `sample_secret.json`):

   ```json
   {
       "RBC": {
           "username": "your_rbc_username",
           "password": "your_rbc_password",
           "security-questions": {
               "question1": "answer1",
               "question2": "answer2",
               "question3": "answer3"
           }
       },
       "YNAB": {
           "email": "your_ynab_email",
           "password": "your_ynab_password"
       },
       "budget-id": "your_ynab_budget_id",
       "account-id": "your_ynab_account_id"
   }
   ```

### Usage

Run the main script to import transactions:

```bash
python main.py
```

## Files

- **main.py**: The main script to execute the synchronization process.
- **sample_secret.json**: A sample credentials file (ensure your actual credentials file is named ```secret.json```).
- **last_imported.txt**: Tracks the date of the last imported transaction. *Note: This does not currently get updated, so all imports will start from whatever date is in this file and not change unless changed manually. YNAB discards transactions imported multiple times, so this should not pose a huge issue.*

## Configuration

Ensure your `secret.json` file is correctly configured with your RBC and YNAB account details. This file should not be shared or exposed publicly to protect your sensitive information.

## Reporting Issues
If you have any other issues or suggestions, go to https://github.com/anna-st-40/ynab-rbcbankus-import/issues and create an issue if one doesn't already exist.