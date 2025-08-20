#!/usr/bin/env python
"""
Search rip.ie for notices based on contents of the watchlist file and display results in a window.
This script may be run manually or on a daily timed basis, via Windows Task Scheduler.
Author: Robert Drohan
Copyright: Copyright 2025, Robert Drohan
license = GPLv3
version = 1.0
status = Release
"""
import csv
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup
import re
import tkinter as tk
from tkhtmlview import HTMLScrolledText
import logging
import os

edge_driver_path = "C:/DriversEtc/Drivers/edgedriver_win64/msedgedriver.exe"
script_directory = os.path.dirname(__file__)
watchlist_path = os.path.join(script_directory, "watchlist.csv")
days_lookback = 1
logging.basicConfig(level=logging.INFO)

# Build RIP.ie search URL
def build_url(county, town, firstname, surname, start_date):
    base_url = "https://rip.ie/death-notice/s"
    # Initialize list to hold path components (e.g., county/town)
    path_parts = []
    if county:
        path_parts.append(county)
    if town:
        path_parts.append(town)
    path = "/".join(path_parts)
    # Initialize query parameters with default page number
    query_params = [
        "page=1"
    ]
    if firstname:
        query_params.append(f"firstname={firstname}")
    if surname:
        query_params.append(f"surname={surname}")

    # Add remaining fixed query parameters:
    # - start date (formatted with time and URL encoding)
    # - end date set to 'today'
    # - sort field and direction
    # - view type set to 'list'
    query_params.extend([
        f"start={start_date}+00%3A00%3A00",  # URL-encoded timestamp
        "end=today",
        "sortField=a.createdAtCastToDate",
        "sortDir=DESC",
        "view=list"
    ])

    # Construct and return the full URL
    query = "&".join(query_params)
    return f"{base_url}/{path}?{query}"


# Fetch page HTML using EdgeDriver, necessary for sites that render content via JavaScript
def fetch_html_with_selenium(url):
    options = Options()
    options.add_argument("--headless")      # Run browser in headless mode (no GUI)
    options.add_argument("--disable-gpu")   # Disable GPU acceleration (recommended for headless mode)
    service = Service(executable_path=edge_driver_path)
    driver = None  # Initialize driver variable

    try:
        # Launch edgedriver, get page source HTML
        driver = webdriver.Edge(service=service, options=options)
        driver.get(url)
        html = driver.page_source
        return html

    except WebDriverException as e:
        logging.error(f"Selenium WebDriver error while fetching {url}: {e}")
        return ""

    except Exception as e:
        logging.error(f"Unexpected error while fetching {url}: {e}")
        return ""

    finally:
        if driver:
            driver.quit()


# Display a pop-up window with a subject heading and HTML-formatted notices
def show_alert_window(subject, notices_html):
    # Create the main application window
    root = tk.Tk()
    root.title("R.I.P.")
    root.geometry("800x400")
    # Create a label widget to display the subject text in bold
    label = tk.Label(root, text=subject, font=("Arial", 16, "bold"))
    # Add some vertical padding and pack the label into the window
    label.pack(pady=(10, 0))
    # Create a scrollable HTML widget to display the notices
    html_widget = HTMLScrolledText(root, html=notices_html, font=("Arial", 11))
    # Pack the HTML widget to fill available space with padding
    html_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    # Start the Tkinter event loop to display the window and handle user interaction
    root.mainloop()


# Search RIP.ie death notices based on a row of input data and a start date
def search_notices_for_row(row, start_day):
    if all(not str(value).strip() for value in row.values()):
        return ["No results"]
    # Extract and normalize search parameters from the input row
    county = row["county"].strip().lower()
    town = row["town"].strip().lower()
    firstname = row["firstname"].strip()
    surname = row["surname"].strip()

    if not county and not town and not firstname and not surname:
        return ["No results"]   # No criteria provided, nothing to search for
    url = build_url(county, town, firstname, surname, start_day)
    # Log the constructed URL for debugging or tracking purposes
    logging.info('\n' + url)
    html = fetch_html_with_selenium(url)
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    found_notices = []
    # Create a regex pattern to match the provided surname
    pattern = rf"/death-notice/.*{re.escape(surname.lower())}.*-\d+$"

    # Search all anchor tags with href attributes in the parsed HTML
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].lower()
        # If the href matches the expected regex pattern, construct the full notice URL
        if re.search(pattern, href):
            notice_url = f"https://rip.ie{a_tag['href']}"
            if notice_url not in found_notices:
                found_notices.append(notice_url)

    # Return the list of found notice URLs, or a default message if none were found
    return found_notices or ["No results"]



def main():
    notices = []

    # Calculate the start date for the search based on the lookback period
    # Format it as YYYY-MM-DD for use in the search URL
    start_day = (datetime.today() - timedelta(days=days_lookback)).strftime("%Y-%m-%d")

    try:
        # Open the CSV file containing the watchlist of individuals to search for
        with open(watchlist_path, newline="") as f:
            reader = csv.DictReader(f)  # Read rows as dictionaries
            # For each person in the watchlist, search for matching death notices
            for row in reader:
                notices.extend(search_notices_for_row(row, start_day))

        # Build an HTML string to display the found notices
        html_lines = []
        for notice in notices:
            if notice != "No results":
                # Format each notice URL as a clickable HTML link
                html_lines.append(f'<p><a href="{notice}">{notice}</a><br></p>')

        # Join all HTML lines into a single string
        notices_html = "\n".join(html_lines)

        # If any notices were found, display them in a pop-up alert window
        if html_lines:
            show_alert_window("R.I.P.", notices_html)

    except FileNotFoundError:
        logging.error(f"File not found: {watchlist_path}")
        return


if __name__ == "__main__":

    main()