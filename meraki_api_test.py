#!/home/mswenson/python/.venv/bin/python
import meraki
import os
API_KEY = os.environ.get("MERAKI_KEY")
dashboard = meraki.DashboardAPI(API_KEY, caller='APITesting Module')
organization_id = "1234567890912"

response = dashboard.wireless.getOrganizationWirelessSsidsStatusesByDevice(
	organization_id, total_pages='all'
)

print(response)
