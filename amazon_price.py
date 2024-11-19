import subprocess
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import csv
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
json_keyfile = 'rpaautomatio-01d742083a67.json'  # Path to your JSON key file
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
updated_data = []
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

for product in rows:
    product_name = product.get("Product Name")
    product_link = product.get("Product Link")
    last_price = product.get("Last Price", "N/A")  # Use .get() to avoid KeyError
    last_rating = product.get("Last Rating", "N/A")  # Use .get() to avoid KeyError
    updated_price = product.get("Updated Price", "N/A")  # Default value if not found
    updated_rating = product.get("Updated Rating", "N/A")  # Default value if not found
    price_changed = product.get("Price Changed", "No")  # Default value if not found
    rating_changed = product.get("Rating Changed", "No")  # Default value if not found
    last_updated = product.get("Last Updated", "N/A")  # Default value if not found

    # Fetch product details from Amazon
    response = requests.get(product_link, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(response.text, "html.parser")

    try:
        price = soup.select_one(".a-price .a-offscreen").text.strip("")
        rating = soup.select_one(".a-icon-alt").text.split(" ")[0]
    except AttributeError:
        price = "N/A"
        rating = "N/A"

    # Determine if price or rating has changed
    price_changed = "Yes" if last_price != price else "No"
    rating_changed = "Yes" if last_rating != rating else "No"

    # Update the HTML content for the email with the product data
    html_content += f"""
        <tr>
            <td>{product_name}</td>
            <td>{last_price}</td>
            <td>{last_rating}</td>
            <td>{price}</td>
            <td>{rating}</td>
            <td class="price-change">{price_changed}</td>
            <td class="rating-change">{rating_changed}</td>
            <td>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</td>  <!-- Place timestamp here -->
            <td><a href="{product_link}" target="_blank">View Product</a></td>
        </tr>
    """

    # Add the new data to the updated data list
    updated_data.append({
        "Product Name": product_name,
        "Product Link": product_link,
        "Last Price": price,
        "Last Rating": rating,
        "Updated Price": price,
        "Updated Rating": rating,
        "Price Changed": price_changed,
        "Rating Changed": rating_changed,
        "Last Updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Add timestamp here
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
for i, product in enumerate(updated_data, start=2):  # Start at row 2 to avoid header
    worksheet.update_cell(i, 3, product["Updated Price"])  # Update "Updated Price" column
    worksheet.update_cell(i, 4, product["Updated Rating"])  # Update "Updated Rating" column
    worksheet.update_cell(i, 5, product["Price Changed"])  # Update "Price Changed" column
    worksheet.update_cell(i, 6, product["Rating Changed"])  # Update "Rating Changed" column
    worksheet.update_cell(i, 7, product["Last Updated"])  # Update "Last Updated" column

# Step 3: Send the email with HTML content
sender_email = "kashishvc.btech22@rvu.edu.in"  # Your email address
receiver_email = "Kashishvarmaa@gmail.com"  # Receiver's email address
subject = "Daily Product Price and Rating Updates"

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject

with open(email_content_file, "r") as email_file:
    msg.attach(MIMEText(email_file.read(), "html"))

# Send email
with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())

print("Email sent successfully!")