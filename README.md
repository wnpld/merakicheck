# Automated Meraki Data Collector
This Python script is intended to be added to a user's crontab so that it can be automatically run once per day.  It will use the Meraki API to collect connection data and save that in a MySQL/MariaDB database for later reporting.
There are three files here:
* merakicheck.py - The main script which does all of the work
* meraki_api_test.py - A script for obtaining data from the Meraki API which is necessary for customizing the main script
* meraki_tables.sql - A SQL script for creating a database and tables to be used by the main script
