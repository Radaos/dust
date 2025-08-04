# dust
A Python script to search rip.ie for notices based on contents of the watchlist file and display results in a window.
Windows Task Scheduler may be used to run this script at a specific time each day.

Installation:\
Ensure an up-to-date version of Python is installed: https://www.python.org/ \
Run the following in a command window if not already installed:\
&emsp;  pip install selenium\
&emsp;  pip install bs4\
&emsp;  pip install tkhtmlview\
Download Edge WebDriver:\
&emsp;  https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/ \
Move msedgedriver.exe to C:\DriversEtc\Drivers\edgedriver_win64
\
Setup:\
Add search criteria to watchlist.csv as required.\
Run launcher.bat manually, or \
Create a new timed task in Windows Task Scheduler to run daily.
