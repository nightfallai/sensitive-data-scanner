import os
from nightfall import Confidence, DetectionRule, Detector, RedactionConfig, MaskConfig, AlertConfig, WebhookAlert, Nightfall
from os import walk

nightfall = Nightfall() # reads API key from NIGHTFALL_API_KEY environment variable by default
webhook_url = f"{os.getenv('NIGHTFALL_SERVER_URL')}/ingest"

# update this path to point to your folder/directory/backup to scan
rootpath = os.getenv('SCAN_DIRECTORY_PATH')

# if a detection rule UUID is provided, use it
# else use a default inline detection rule for credit card numbers, SSNs, and API keys
detection_rule_uuid = os.getenv('NIGHTFALL_DETECTION_RULE_UUID')
detection_rules = None
detection_rule_uuids = None

if detection_rule_uuid is None:
	print("No detection rule UUID specified - using default inline detection rule")
	detection_rules = [ DetectionRule([ # specify an inline detection rule
		Detector(
			min_confidence=Confidence.LIKELY,
			nightfall_detector="CREDIT_CARD_NUMBER",
			display_name="Credit Card Number"
	   	),
	   	Detector(
			min_confidence=Confidence.LIKELY,
			nightfall_detector="US_SOCIAL_SECURITY_NUMBER",
			display_name="US Social Security Number"
	   	),
	   	Detector(
			min_confidence=Confidence.LIKELY,
			nightfall_detector="API_KEY",
			display_name="API Key"
	   	)])
	]
else:
	print("Found detection rule UUID")
	detection_rule_uuids = [ detection_rule_uuid ]

# crawl the backup directory to scan all files
count = 0
for (dirpath, dirnames, filenames) in walk(rootpath):
	for filename in filenames:
		filepath = f"{dirpath}/{filename}"
		count += 1

		try:
			print(f"Scanning {filepath}")
			# scan with Nightfall
			scan_id, message = nightfall.scan_file(filepath, 
				alert_config=AlertConfig(url=WebhookAlert(webhook_url)),
				detection_rule_uuids=detection_rule_uuids,
				detection_rules=detection_rules, 
				request_metadata=filepath)
			print(scan_id, message)
		except Exception as err:
			print(err)
print(f"Completed. Scanned {count} file(s)")