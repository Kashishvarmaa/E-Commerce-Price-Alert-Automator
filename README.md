# Amazon Price Tracker Automator

## Overview
The **Amazon Price Tracker Automator** is an automated script designed to track price and rating changes for products listed on Amazon. It scrapes product information from Amazon's product pages, compares it with stored values, and updates a Google Sheets document with the latest product details. Additionally, it generates an HTML email report that is sent to a designated email address, summarizing price and rating changes for the tracked products.

This project is ideal for individuals or businesses who want to track product price fluctuations and ratings over time without manual intervention.

## Features
- **Price and Rating Tracking**: Automatically tracks price and rating changes for selected Amazon products.
- **Google Sheets Integration**: Stores product details and updates the Google Sheets document with the latest information.
- **Email Report**: Generates and sends an email with an HTML report detailing product updates (price changes, rating changes).
- **Automation**: Fully automated with the ability to schedule and run at set intervals using macOS Automator.

## Requirements
- Python 3.x
- Google Sheets API credentials
- Amazon product links for tracking
- Email account for sending reports (Gmail recommended)
- Environment variables for email credentials
- `.env` file for managing sensitive information

### Dependencies
- `requests`
- `beautifulsoup4`
- `gspread`
- `oauth2client`
- `python-dotenv`
- `smtplib`
- `email.mime`
- `datetime`

You can install these dependencies using pip:

```bash
pip install requests beautifulsoup4 gspread oauth2client python-dotenv
```


## Setup

### 1. Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/yourusername/amazon-price-tracker-automator.git
cd amazon-price-tracker-automator
```
### 2. Google Sheets API

Follow these steps to set up the Google Sheets API:

1. Go to the [Google Developers Console](https://console.developers.google.com/).
2. Create a new project.
3. Enable the **Google Sheets API** for your project:
   - In the dashboard, click on **Enable APIs and Services**.
   - Search for **Google Sheets API** and click **Enable**.
4. Create credentials for a **Service Account**:
   - Go to **APIs & Services** → **Credentials**.
   - Click **Create Credentials** → **Service Account**.
   - Follow the prompts to create a new service account.
5. Download the **JSON key file** for the service account:
   - After creating the service account, click on the **Download** button to save the JSON key file to your machine.
6. Share your Google Sheet with the service account's email address:
   - Open the downloaded JSON file and find the **client_email** field.
   - Share your Google Sheet with this email address (make sure to give the email **Editor** permissions).

> **Note:** The `client_email` in the JSON file will look like this: `your-service-account@your-project-id.iam.gserviceaccount.com`.

### 3. Environment Variables

To securely store your email credentials, we use environment variables. 

1. Create a `.env` file in the project directory.
2. Add the following lines to your `.env` file:

```
EMAIL_USER=your-email@example.com
EMAIL_PASSWORD=your-email-password
```

Make sure to replace `your-email@example.com` and `your-email-password` with your actual email credentials.

> **Important:** For Gmail users, you may need to generate an **App Password** if you have 2-factor authentication enabled. You can generate this in your Google Account settings.

### 4.Install Dependencies

Before running the script, install the required dependencies. You can use `pip` to install them.

Install the dependencies by running:

```bash
pip install -r requirements.txt
```
Alternatively, you can manually install the dependencies with:
```
pip install requests beautifulsoup4 gspread oauth2client python-dotenv
```



## Running the Script

Once you’ve set up your environment variables and installed dependencies, you can run the script to start tracking product prices.

Run the script with the following command:
 ```
python amazon_price.py
```
This will:
- Scrape the product prices and ratings from the provided Amazon links
- Send an email report with the updates.
- Update the Google Sheets file with the latest data.



 ## Automating with macOS Automator

You can use macOS Automator to automate the script and run it at regular intervals.

Steps:
1. Open Automator on your Mac.
2. Create a new Calendar Alarm.
3. In the workflow, search for Run Shell Script.
4. In the Run Shell Script action, enter the following command (make sure to provide the correct path to your script):
 ```
python /path/to/your/project/amazon_price.py
```
5. Save the workflow. It will run automatically at the specified time based on your calendar settings.




 ## Troubleshooting

If you encounter issues, try the following steps:

1. Script Not Running
- 	Ensure all dependencies are installed by running pip install -r requirements.txt.
- 	Double-check that your .env file contains the correct email credentials.
- 	Verify that the Google Sheets API is correctly set up and the service account has access to your sheet.


2. Invalid Google Sheet API Credentials
- Make sure the service account’s email (client_email) is shared with your Google Sheet.
- Ensure the correct JSON key file is specified in the script (rpaautomatio-01d742083a67.json).


3. Email Not Sent
- Ensure that the EMAIL_USER and EMAIL_PASSWORD are set correctly in the .env file.
- If using Gmail, check that you have generated an App Password if 2-factor authentication is enabled.


4. Amazon Page Layout Changes
- If the script is not scraping the correct data, it could be due to changes in the Amazon product page layout. You may need to update the scraping selectors (e.g., .a-price .a-offscreen and .a-icon-alt) based on the new page structure.



