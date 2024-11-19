import requests
from bs4 import BeautifulSoup
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access email credentials from environment variables
sender_email = os.getenv('EMAIL_USER')
password = os.getenv('EMAIL_PASSWORD')

# Google Sheets API authentication
json_keyfile = '/Users/kashishvarmaa/Documents/5 Sem/RPA /Amazon Price Tracker/rpaautomatio-01d742083a67.json'  # Path to your JSON key file
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, scope)
gc = gspread.authorize(credentials)

# Open Google Sheet by name or URL
worksheet = gc.open("product_tracker").sheet1  # Replace with your Google Sheets name

# File paths
email_content_file = "email_content.html"  # Path where email HTML content will be saved

# Step 1: Read and process the Google Sheets data
product_data = []
rows = worksheet.get_all_records()  # Get all rows of data

# Scrape Amazon product details
# Updated product data handling
updated_data = []

# HTML content to display the email report
html_content = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        h2 { color: #4CAF50; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 16px; }
        table th, table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        table th { background-color: #f4f4f4; }
        .price-change { color: #ff5722; font-weight: bold; }
        .rating-change { color: #2196F3; font-weight: bold; }
    </style>
</head>
<body>
    <h2>Product Price and Rating Update</h2>
    <p>Here are the latest updates for the products you are tracking:</p>
    <table>
        <thead>
            <tr>
                <th>Product Name</th>
                <th>Last Price</th>
                <th>Last Rating</th>
                <th>Updated Price</th>
                <th>Updated Rating</th>
                <th>Price Changed</th>
                <th>Rating Changed</th>
                <th>Last Updated</th>
                <th>Link</th>
            </tr>
        </thead>
        <tbody>
"""

# Loop through the rows from Google Sheets
for product in rows:
    product_name = product.get("Product Name")
    product_link = product.get("Product Link")
    last_price = product.get("Last Price", "N/A")  # Get last price
    last_rating = product.get("Last Rating", "N/A")  # Get last rating
    price_changed = "No"  # Default value
    rating_changed = "No"  # Default value
    last_updated = product.get("Last Updated", "N/A")

    # Fetch product details from Amazon
    response = requests.get(product_link, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        updated_price = soup.select_one(".a-price .a-price-whole").text.strip()  # Extract price
        updated_rating = soup.select_one(".a-icon-alt").text.split(" ")[0]  # Extract rating
    except AttributeError:
        updated_price = "N/A"
        updated_rating = "N/A"

    # Compare old vs new prices and ratings
    if last_price != updated_price:
        price_changed = "Yes"
    if last_rating != updated_rating:
        rating_changed = "Yes"

    # Update the HTML content for the email with product data
    html_content += f"""
        <tr>
            <td>{product_name}</td>
            <td>{last_price}</td>
            <td>{last_rating}</td>
            <td>{updated_price}</td>
            <td>{updated_rating}</td>
            <td class="price-change">{price_changed}</td>
            <td class="rating-change">{rating_changed}</td>
            <td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>  <!-- Add timestamp -->
            <td><a href="{product_link}" target="_blank">View Product</a></td>
        </tr>
    """

    # Add the updated data to the list for Google Sheets update
    updated_data.append({
        "Product Name": product_name,
        "Product Link": product_link,
        "Last Price": last_price,  # Keep the last price fixed
        "Last Rating": last_rating,  # Keep the last rating fixed
        "Updated Price": updated_price,
        "Updated Rating": updated_rating,
        "Price Changed": price_changed,
        "Rating Changed": rating_changed,
        "Last Updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

html_content += """
        </tbody>
    </table>
    <p>This report is generated automatically at the scheduled time.</p>
</body>
</html>
"""

# Save the HTML content to a file
with open(email_content_file, "w") as email_file:
    email_file.write(html_content)

# Step 2: Update the Google Sheet with new product data
for i, product in enumerate(updated_data, start=2):  # Start from row 2 to avoid header
    worksheet.update_cell(i, 4, product["Updated Price"])
    worksheet.update_cell(i, 5, product["Updated Rating"])
    worksheet.update_cell(i, 6, product["Price Changed"])
    worksheet.update_cell(i, 7, product["Rating Changed"])
    worksheet.update_cell(i, 8, product["Last Updated"])

# Step 3: Send the email with HTML content
receiver_email = "kashishvarmaa@gmail.com"  # Enter receiver's email here
subject = "Daily Product Price and Rating Updates"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject

with open(email_content_file, "r") as email_file:
    msg.attach(MIMEText(email_file.read(), "html"))

# Send the email
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Email sent successfully!")