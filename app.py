import os
from flask import Flask, request, render_template
from nightfall import Confidence, DetectionRule, Detector, RedactionConfig, MaskConfig, Nightfall
from datetime import datetime, timedelta
import urllib.request, urllib.parse, json
import csv

app = Flask(__name__)

nightfall = Nightfall(
	key=os.getenv('NIGHTFALL_API_KEY'),
	signing_secret=os.getenv('NIGHTFALL_SIGNING_SECRET')
)

# create CSV where sensitive findings will be written
headers = ["upload_id", "#", "datetime", "filepath", "before_context", "finding", "after_context", "detector", "confidence", "loc", "detection_rules"]
with open(f"results.csv", 'a') as csvfile:
	writer = csv.writer(csvfile)
	writer.writerow(headers)

# respond to POST requests at /ingest
# Nightfall will send requests to this webhook endpoint with file scan results
@app.route("/ingest", methods=['POST'])
def ingest():
	data = request.get_json(silent=True)
	# validate webhook URL with challenge response
	challenge = data.get("challenge") 
	if challenge:
		return challenge
	# challenge was passed, now validate the webhook payload
	else: 
		# get details of the inbound webhook request for validation
		request_signature = request.headers.get('X-Nightfall-Signature')
		request_timestamp = request.headers.get('X-Nightfall-Timestamp')
		request_data = request.get_data(as_text=True)

		if nightfall.validate_webhook(request_signature, request_timestamp, request_data):
			# check if any sensitive findings were found in the file, return if not
			if not data["findingsPresent"]: 
				print("No sensitive data present!")
				return "", 200

			# there are sensitive findings in the file
			output_results(data)
			return "", 200
		else:
			return "Invalid webhook", 500

def output_results(data):
	findings_url = data['findingsURL']
	# open findings URL provided by Nightfall to access findings
	with urllib.request.urlopen(findings_url) as url:
		findings = json.loads(url.read().decode())
		findings = findings['findings']

	filepath = ""
	if 'requestMetadata' in data:
		filepath = data['requestMetadata']

	print(f"Sensitive data found in {filepath} | Outputting {len(findings)} finding(s) to CSV | UploadID {data['uploadID']}")
	table = []
	# loop through findings JSON, get relevant finding metadata, write each finding as a row into output CSV
	for i, finding in enumerate(findings):
		before_context = ""
		if 'beforeContext' in finding:
			before_context = repr(finding['beforeContext'])
		after_context = ""
		if 'afterContext' in finding:
			after_context = repr(finding['afterContext'])

		row = [
			data['uploadID'],
			i+1,
			datetime.now(),
			filepath,
			before_context, 
			repr(finding['finding']),
			after_context,
			finding['detector']['name'],
			finding['confidence'],
			finding['location']['byteRange'],
			finding['matchedDetectionRules']
		]
		table.append(row)
		with open(f"results.csv", 'a') as csvfile:
			writer = csv.writer(csvfile)
			writer.writerow(row)
	return
