"""
Search rip.ie for notices based on contents of the watchlist file and display results in a window.
This script may be run manually or on a daily timed basis, via Windows Task Scheduler.
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

EDGE_DRIVER_PATH = "C:/DriversEtc/Drivers/edgedriver_win64/msedgedriver.exe"
WATCHLIST_PATH = "watchlist.csv"
DAYS_LOOKBACK = 1
logging.basicConfig(level=logging.INFO)

# Build RIP.ie search URL
def build_url(county, town, firstname, surname, start_date):
    base = "https://rip.ie/death-notice/s"
    path_parts = []
    if county:
        path_parts.append(county)
    if town:
        path_parts.append(town)
    path = "/".join(path_parts)
    # Build query string in the exact order required
    query_params = [
        "page=1"
    ]
    if firstname:
        query_params.append(f"firstname={firstname}")
    if surname:
        query_params.append(f"surname={surname}")
    query_params.extend([
        f"start={start_date}+00%3A00%3A00",
        "end=today",
        "sortField=a.createdAtCastToDate",
        "sortDir=DESC",
        "view=list"
    ])
    query = "&".join(query_params)
    return f"{base}/{path}?{query}"

# Fetch page HTML using EdgeDriver
def fetch_html_with_selenium(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    service = Service(executable_path=EDGE_DRIVER_PATH)
    driver = None
    try:
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

def show_alert_window(subject, notices_html):
    root = tk.Tk()
    root.title("R.I.P.")
    root.geometry("800x400")
    label = tk.Label(root, text=subject, font=("Arial", 16, "bold"))
    label.pack(pady=(10, 0))
    html_widget = HTMLScrolledText(root, html=notices_html, font=("Arial", 11))
    html_widget.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
    root.mainloop()

def search_notices_for_row(row, start_day):
    county = row["county"].strip().lower()
    town = row["town"].strip().lower()
    firstname = row["firstname"].strip()
    surname = row["surname"].strip()
    if not surname:
        return ["No results"]   # Skip search if surname is empty

    url = build_url(county, town, firstname, surname, start_day)
    logging.info('\n' + url)
    html = fetch_html_with_selenium(url)
    soup = BeautifulSoup(html, "html.parser")
    found_items = []
    pattern = rf"/death-notice/.*{re.escape(surname.lower())}.*-\d+$"
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].lower()
        if re.search(pattern, href):
            notice_url = f"https://rip.ie{a_tag['href']}"
            if notice_url not in found_items:
                found_items.append(notice_url)
    return found_items or ["No results"]

# Main execution
def main():
    notices = []
    start_day = (datetime.today() - timedelta(days=DAYS_LOOKBACK)).strftime("%Y-%m-%d")
    try:
        with open(WATCHLIST_PATH, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                notices.extend(search_notices_for_row(row, start_day))

        # Build HTML string
        html_lines = []
        for notice in notices:
            if notice != "No results":
                html_lines.append(f'<p><a href="{notice}">{notice}</a><br></p>')
        notices_html = "\n".join(html_lines)

        if html_lines:
            show_alert_window("R.I.P.", notices_html)

    except FileNotFoundError:
        logging.error(f"File not found: {WATCHLIST_PATH}")
        return

if __name__ == "__main__":
    main()