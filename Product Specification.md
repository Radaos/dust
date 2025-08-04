# Product Specification Document

## Project Title: Dust

## Purpose: To monitor death notices on rip.ie based on a user-defined watchlist. Periodically query the site, parse relevant notices, and display matching results in a GUI window. The tool is intended for personal use.

## Functional Requirements
1. Watchlist Monitoring\
FR1.1: The application shall read a local watchlist.txt file containing keywords (e.g., surnames, locations).\
FR1.2: Each keyword shall be matched against the contents of death notices retrieved from rip.ie.

2. Web Scraping\
FR2.1: The application shall send HTTP requests to rip.ie to retrieve the latest death notices.\
FR2.2: It shall parse HTML content using BeautifulSoup to extract:\
Name of deceased\
Location\
Date of notice\
Link to full notice

3. Result Filtering\
FR3.1: Notices shall be filtered based on keyword matches from the watchlist.\
FR3.2: Duplicate notices shall be avoided using a local cache (seen.txt).

4. GUI Display\
FR4.1: Matching notices shall be displayed in a scrollable Tkinter window.\
FR4.2: Each notice shall be clickable, opening the full entry in the default browser.

5. Background Execution\
FR5.1: The script shall run silently as a .pyw file (no console window).\
FR5.2: It may be scheduled via Windows Task Scheduler or run manually.

## Design Specifications
GUI Layout\
Title Label	Displays “RIP”\
Scrollable Frame	Lists matching notices with clickable links

File Structure\
File: Purpose\
dust.pyw	Main application script\
watchlist.txt	User-defined keywords for filtering\
seen.txt	Cache of previously seen notices\
README.md	Setup and usage instructions\

Error Handling\
Network failures are caught and logged to the status label.\
Malformed HTML or missing elements are handled gracefully.

Dependencies\
requests — for HTTP communication\
bs4 (BeautifulSoup) — for HTML parsing\
tkinter — for GUI rendering\

webbrowser — to open notice links
