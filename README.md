# Salesforce DLP Scanner

#### Scan a backup of Salesforce to discover sensitive data (like PII & credit card numbers) that lives at-rest in your Salesforce instance with Nightfall's data loss prevention APIs.

This service uses Nightfall's [data loss prevention (DLP) APIs](https://nightfall.ai/developer-platform) to scan a backup of your Salesforce instance for sensitive data. Salesforce houses high volumes of customer information, support tickets, quotes and files, synced emails, tasks & notes, and much more. This service will (1) send Salesforce backup data to Nightfall to be scanned, (2) run a local webhook server that retrieves sensitive results back from Nightfall, and (3) write the sensitive findings to a CSV file. This output provides a comprehensive report/audit of the sensitive data at-rest in your Salesforce tenant.

If you'd like a more detailed tutorial or walk-through of how this service works, we recommend reviewing our [file scanner tutorial](https://github.com/nightfallai/file-scanner-tutorial), as the components are largely the same.

## Prerequisites

* Admin access to Salesforce to be able to create a backup
* Nightfall account - [sign up](https://app.nightfall.ai/sign-up) for free if you don't have an account

## Usage

1. Create a Salesforce backup ([instructions](https://help.salesforce.com/s/articleView?id=sf.admin_exportdata.htm&type=5)), download it, and extract it locally.

1. Install dependencies.

```bash
pip install -r requirements.txt
```

2. Create a local ngrok tunnel to point to your webhook server.

```bash
./ngrok http 8000
```

3. Set your environment variables: your Nightfall API key, your Nightfall signing secret, your Nightfall [detection rule UUID](https://docs.nightfall.ai/docs/creating-detection-rules), your webhook server URL from ngrok, and the path to your extracted Salesforce backup that you want to crawl.

Your Nightfall detection rule UUID is optional. If not specified, the default rule will detect likely credit card numbers, US social security numbers, and API keys.

```bash
export NIGHTFALL_API_KEY=<your_key_here>
export NIGHTFALL_SIGNING_SECRET=<your_secret_here>
export NIGHTFALL_DETECTION_RULE_UUID=<your_uuid_here>
export NIGHTFALL_SERVER_URL=https://<your_subdomain_here>.ngrok.io
export SALESFORCE_BACKUP_PATH='/Users/myuser/salesforce-exports/'
```

4. Start your webhook server. This runs `app.py`.

```bash
gunicorn app:app
```

5. Run your scan.

```python
python scanner.py
```

6. Monitor your webhook server output. Once all file scan events have been received and the scan is complete, view your results in `results.csv`. Each row in the output CSV will correspond to a sensitive finding. Each row will have the following fields, which you can customize in your webhook server in `app.py`: 

* Upload ID provided by Nightfall
* An incrementing index
* Timestamp
* Filepath
* Characters before the sensitive finding (for context)
* Sensitive finding itself
* Characters after the sensitive finding (for context)
* Confidence level of the detection
* Byte range location (character indicies) of the sensitive finding in its parent file
* Corresponding detection rules that flagged the sensitive finding
