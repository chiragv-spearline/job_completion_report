utc_timezone_id = 45
company_id = 8
cli = 123456789
route = 408
dtmf = '4'
sudo_password = 'chirag'
ivr_spearline_prompt_id = 19
ivr_spearline_prompt = 'Spearline Prompt'
email_contact = 'tania.hodnett@spearline.com'
campaign_timegroup_interval = {'id': 'hourly_interval_id-2', 'schedule': 'Every 2 Hours'}

# IDs value of test type 
conferences_test_type_id = 1
connection_test_type_id = 3
audio_latency_test_type_id = 43
single_line_test_type_id = 40
in_country_test_type_id = 4
agent_connection_test_type_id = 55
sip_trunk_test_type_id = 63

# Numbers for generating campaign job schedule report
pstn_conf_qual_numbers = {
    'number1': { 'id': 1041247, 'number': 2234332432, 'country': 'India', 'desc_name': 'Agent', 'phonegroup_id': 1011428, 'route_id': 158, 'route_id': 158, 'desc_id': 89, 'server_id': 78, 'pesq_server_id': 2, 'type': 'Toll Free' },
    'number2': { 'id': 1041248, 'number': 2234332412, 'country': 'Ireland', 'desc_name': 'Busy', 'phonegroup_id': 1011429, 'route_id': 174, 'desc_id': 3, 'server_id': 141, 'pesq_server_id': 1, 'type': 'Mobile Toll' },
    'number3': { 'id': 1041249, 'number': 2234332414, 'country': 'Argentina', 'desc_name': 'Connected', 'phonegroup_id': 1011430, 'route_id': 1, 'desc_id': 14, 'server_id': 2, 'pesq_server_id': 2, 'type': 'Toll' },
    'number4': { 'id': 1041250, 'number': 2234332487, 'country': 'United States', 'desc_name': 'Successful', 'phonegroup_id': 1011431, 'route_id': 408, 'desc_id': 88, 'server_id': 46, 'pesq_server_id': 2, 'type': 'Toll' },
    'number5': { 'id': 1041251, 'number': 2234332467, 'country': 'Ireland', 'desc_name': 'No Answer', 'phonegroup_id': 1011432, 'route_id': 174, 'desc_id': 7, 'server_id': 141, 'pesq_server_id': 1, 'type': 'Toll Free' }
}

pstn_qual_numbers = {
    'number1': { 'id': 1044513, 'number': 5425453452, 'country': 'Argentina', 'desc_name': 'Agent', 'route_id': 1, 'desc_id': 89, 'server_id': 78, 'type': 'Toll Free' },
    'number2': { 'id': 1044515, 'number': 5425453453, 'country': 'Spain', 'desc_name': 'Busy', 'route_id': 90, 'desc_id': 3, 'server_id': 141, 'type': 'Toll' },
    'number3': { 'id': 1044517, 'number': 5425453454, 'country': 'Ireland', 'desc_name': 'Connected', 'route_id': 174, 'desc_id': 14, 'server_id': 2, 'type': 'Toll' },
    'number4': { 'id': 1044520, 'number': 5425453455, 'country': 'India', 'desc_name': 'Successful', 'route_id': 158, 'desc_id': 88, 'server_id': 46, 'type': 'Toll' },
    'number5': { 'id': 1044522, 'number': 5425453456, 'country': 'United States', 'desc_name': 'No Answer', 'route_id': 408, 'desc_id': 7, 'server_id': 141, 'type': 'Toll' }
}

sip_quality_uri = {
    'uri1': { 'id': 1057965, 'uri': 134354563435, 'country': 'Ireland', 'desc_name': 'Agent', 'route_id': 174, 'desc_id': 89, 'server_id': 78, 'type': 'SIP' },
    'uri2': { 'id': 1057966, 'uri': 134354563436, 'country': 'India', 'desc_name': 'Busy', 'route_id': 158, 'desc_id': 3, 'server_id': 141, 'type': 'SIP' },
    'uri3': { 'id': 1057967, 'uri': 134354563437, 'country': 'Australia', 'desc_name': 'Connected', 'route_id': 5, 'desc_id': 14, 'server_id': 2, 'type': 'SIP' },
    'uri4': { 'id': 1057968, 'uri': 134354563438, 'country': 'Spain', 'desc_name': 'Successful', 'route_id': 90, 'desc_id': 88, 'server_id': 46, 'type': 'SIP' },
    'uri5': { 'id': 1057969, 'uri': 134354563439, 'country': 'Canada', 'desc_name': 'No Answer', 'route_id': 41, 'desc_id': 7, 'server_id': 141, 'type': 'SIP' }
}

# Campaign Report Headers
conferences_testtype_report_headers = ['ID', 'Number', 'Campaign', 'Country', 'Number Type', 'Customer', 'Department', 'Location', 'Carrier', 'CLI', 'IVR Traversal', 'Call Start Time', 'Call End Time', 'State', 'Score', 'Recording', 'Number', 'Country', 'Start Time', 'Connect Time', 'DDI End Time']
connection_testtype_report_headers = ['ID', 'Number', 'Campaign', 'Country', 'Number Type', 'Customer', 'Department', 'Location', 'Carrier', 'CLI', 'IVR Traversal', 'State', 'Score', 'Recording']
audio_latency_testtype_report_headers = ['ID', 'Number', 'Campaign', 'Country', 'Number Type', 'Customer', 'Department', 'Location', 'Carrier', 'CLI', 'IVR Traversal', 'State', 'Score', 'Recording']
single_line_testtype_report_headers = ['ID', 'Number', 'Campaign', 'Country', 'Number Type', 'Customer', 'Department', 'Location', 'Carrier', 'CLI', 'IVR Traversal', 'Call Start Time', 'Call End Time', 'State', 'Score', 'Recording']
in_country_testtype_report_headers = ['ID', 'Number', 'Campaign', 'Country', 'Number Type', 'Customer', 'Department', 'Location', 'Carrier', 'CLI', 'IVR Traversal', 'Call Start Time', 'Call End Time', 'State', 'Score', 'Recording']
agent_connection_testtype_report_headers = ['ID', 'Number', 'Campaign', 'Country', 'Number Type', 'Customer', 'Department', 'Location', 'Carrier', 'CLI', 'IVR Traversal', 'Received DTMF', 'Agent Confirmation Time', 'State', 'Score', 'Recording']
sip_trunk_testtype_report_headers = ['ID', 'Number', 'Campaign', 'Country', 'Number Type', 'Customer', 'Department', 'Location', 'Carrier', 'CLI', 'IVR Traversal', 'Call Start Time', 'Call End Time', 'State', 'Score', 'Recording']


