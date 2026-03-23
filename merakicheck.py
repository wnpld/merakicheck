#!/path/to/.venv/bin/python

# The above path will need to be updated.  The recommended current practice
# is to run scripts like this requiring additiona libraries to be run in a virtual
# environment which will have its own Python interpreter.  The path above reflects
# this general idea. (see https://docs.python.org/3/library/venv.html)

# This script requires a Meraki API key to be established in the Meraki administrative interface
# This can be found (as of March 2026) under:
# Organization > [Configuration] API & Webhooks > API keys and access
# There is documentation for the Meraki API at this location as well

# The API key is not entered directly into this script, but is added at the top
# of the crontab file which executes this script in an environment variable
# called MERAKI_KEY

# Meraki assigns each organization an Organization ID which can be found in the footer 
# of most every page in the administration portal
# Each network and SSID is also assigned its own ID, and you will need those IDs to 
# complete this script.
# You can use the meraki_api_test.py Python script to get a JSON report of your network
# which includes these IDs in it.  They are identified by the id and number fields, respectively

import meraki
import os
import sys
import re
import hashlib
import time
import mysql.connector
from datetime import datetime, date, timedelta
from numbers import Number

# API User Agent
# Put here a custom user agent string to identify this application
user_agent = "StatsCollection MyLibrary" 

# Log files directory
local_log_path = "/home/user/logs/"

#UTC Day Start
#Put here the time string indicating when midnight happens in your locale in UTC
day_start = "T05:00:00Z"

# Location IDs should be defined here.
# For my purposes we had two ids and our internal database ids for our SSIDs
# were divided so that numbers less than 6 were one location and the rest were
# the other location.  You will need to adjust the code where these variables
# are called if you have more or fewer locations
network_id_one = "L_1234567890"
network_id_two = "L_2345678901"
network_ssid_split = 6

# Database Connection Information
# Update this with your data
sql_server = "localhost"
sql_user = "dbuser"
sql_password = "monkey123"
sql_db = "my_stats"

# Database tables are assumed to be MerakiDailyConnections & MerakiUniqueClients

# Errorstate is used for exit code
errorstate = 0
# Takes minimum 2, up to 3 arguments: ssid (number from Meraki), wirelessid (internal db number), and date to run
# Examples: If the Meraki assigned SSID number is 1 and the ID in the local database is 2
# the command line with arguments is 
# /path/merakicheck.py 1 2
# If a specific date is being run, an example is:
# /path/merakicheck.py 1 2 2026-03-03
args = len(sys.argv)

# Multiday is used for doing a number of days in sequence
multiday = 0
# one_day is frequently used to add or remove a day from a datetime
one_day = timedelta(days=1)

#Check arg count
if args == 4:
  try:
    ssidno = int(sys.argv[1])
  except ValueError:
    print("Unable to parse ssid value as a number")
    sys.exit(1)
  try:
    wirelessid = int(sys.argv[2])
  except ValueError:
    print("Unable to parse wirelessid value as a number")
    sys.exit(1)
  cldate = sys.argv[3]
  pattern_raw_string = r"^\d\d\d\d-\d\d-\d\d$"
  if re.search(pattern_raw_string, cldate):
    startdate = date.fromisoformat(cldate)
    enddate = startdate + one_day
  else:
    print("Date passed to script incorrectly formatted.  Use yyyy-mm-dd.")
    sys.exit(1)
elif args == 3:
  # If a date is not specified, do a query to find out what the most recent
  # records for the wireless network in question are
  try:
    ssidno = int(sys.argv[1])
  except ValueError:
    print("Unable to parse ssid value as a number")
    sys.exit(1)
  try:
    wirelessid = int(sys.argv[2])
  except ValueError:
    print("Unable to parse wirelessid value as a number")
    sys.exit(1)
  try:
    # Establish connection
    mydb = mysql.connector.connect(
      host=sql_server,
      user=sql_user,
      password=sql_password,
      database=sql_db
    )
    mycursor = mydb.cursor()
    datequery = "SELECT DISTINCT MerakiConnectionDate FROM MerakiDailyConnections WHERE WirelessID = %s ORDER BY MerakiConnectionDate DESC LIMIT 1"
    sqldata = (wirelessid,)
    mycursor.execute(datequery, sqldata)
    dateresult = mycursor.fetchone()
    # Apparently the MySQL cursor returns the date as a Python datetime.date
    # so it requires no conversion
    lastdate = dateresult[0]
    todaydt = datetime.now()
    today = todaydt.date()
    yesterday = today - one_day
    if lastdate < yesterday:
      multiday = 1
      startdate = lastdate
      enddate = today
    elif lastdate == yesterday:
      startdate = yesterday
      enddate = today
    else:
      print("Data is current.")
      errorstate=1
  except:
    print(f"Error: {err}")
    errorstate = 1
  finally:
    #Close connection
    if 'myb' in locals() and mydb.is_connected():
      mycursor.close()
      mydb.close()
    if errorstate == 1:
      sys.exit(errorstate)
else:
  print("Incorrect number of arguments.  Usage: merakicheck.py <ssid-id> <wirelessid> [<date to check as yyyy-mm-dd>]")
  sys.exit(1)

# It's more secure to store the SSID in an environment variable.  This needs to be set before execution
API_KEY = os.environ.get("MERAKI_KEY")
dashboard = meraki.DashboardAPI(API_KEY, caller=user_agent, log_path=local_log_path)

# Network id is a Meraki specific value for each location
if wirelessid < network_ssid_split:
  # Winnetka
  network_id = network_id_one
else:
  # Northfield
  network_id = network_id_two

start = startdate.strftime("%Y-%m-%d")
timeone = start + day_start

if multiday == 1:
  nextdate = startdate + one_day
  formatted_next = nextdate.strftime("%Y-%m-%d")
  timetwo = formatted_next + day_start
else:
  formatted_today = enddate.strftime("%Y-%m-%d")
  timetwo = formatted_today + day_start

# This loops untill all days are done
# If this is not a multiday query, there's a break at the bottom to exit
while True:
  response = dashboard.wireless.getNetworkWirelessClientsConnectionStats(
    network_id, t0=timeone, t1=timetwo, ssid=ssidno
  )

  try:
    # Establish connection
    mydb = mysql.connector.connect(
      host=sql_server,
      user=sql_user,
      password=sql_password,
      database=sql_db
    )

    mycursor = mydb.cursor()

    for record in response:
      macid = record['mac']
      sessions = record['connectionStats']['success']
      macid_hash = hashlib.sha1(macid.encode('utf-8'))
      macid_hex = macid_hash.hexdigest()
  
      id_check = "SELECT MerakiClientID FROM MerakiUniqueClients WHERE UIDHash = UNHEX(%s)"
      sql_data = (macid_hex,)
  
      mycursor.execute(id_check, sql_data)
  
      id_result = mycursor.fetchone()
  
      if not id_result:
        id_add = "INSERT INTO MerakiUniqueClients (UIDHash) VALUES (UNHEX(%s))"
        mycursor.execute(id_add, sql_data)
        mydb.commit()
    
        clientid = mycursor.lastrowid
      else:
        clientid = id_result[0]
    
      session_add = "INSERT IGNORE INTO MerakiDailyConnections (MerakiConnectionDate, MerakiClientID, MerakiSessionCount, WirelessID) VALUES (%s, %s, %s, %s)"
  
      sql_data = (start, clientid, sessions, wirelessid)
  
      mycursor.execute(session_add, sql_data)
      mydb.commit()
    
  except mysql.connector.Error as err:
    print(f"Error: {err}")
    errorstate=1
  finally:
    #Close connection
    if 'myb' in locals() and mydb.is_connected():
      mycursor.close()
      mydb.close()
      if (errorstate == 1):
        sys.exit(errorstate)
  if multiday == 0:
    break
  else:
    # Sleep to slow down the API rate
    time.sleep(0.25)
    startdate = startdate + one_day
    nextdate = startdate + one_day
    if nextdate == enddate:
      multiday = 0
    start = startdate.strftime("%Y-%m-%d")
    timeone = start + day_start
    nextdate = startdate + one_day
    formatted_next = nextdate.strftime("%Y-%m-%d")
    timetwo = formatted_next + day_start
  
sys.exit(errorstate)
