# Sensitive At-Rest Data Scanner

#### Scan directories, exports, and backups for sensitive data (like PII and API keys) with Nightfall's data loss prevention (DLP) APIs. Discover what lives at-rest in your data silos.

This service uses Nightfall's [data loss prevention (DLP) APIs](https://nightfall.ai/developer-platform) to scan a folder/directory, backup, or export. 

For example, you can scan a backup of your Salesforce instance to detect sensitive data in Salesforce. Salesforce houses high volumes of customer information, support tickets, quotes and files, synced emails, tasks & notes, and much more. This service will (1) send Salesforce backup data to Nightfall to be scanned, (2) run a local webhook server that retrieves sensitive results back from Nightfall, and (3) write the sensitive findings to a CSV file. This output provides a comprehensive report/audit of the sensitive data at-rest in your Salesforce tenant. The same premise extends to any service that allows you to generate a backup or export.

If you'd like a more detailed tutorial or walk-through of how this service works, we recommend reviewing our [file scanner tutorial](https://github.com/nightfallai/file-scanner-tutorial), as the components are largely the same.

## Prerequisites

* Nightfall account - [sign up](https://app.nightfall.ai/sign-up) for free if you don't have an account
* If you are scanning a cloud backup or export, you'll need admin access to the data silos you wish to scan, in order to create a backup or export

## Usage

1. Create a cloud backup/export of the systems you wish to scan. Download the backup and extract it locally. We've compiled instructions for a handful of popular cloud apps below.

- [Salesforce](https://help.salesforce.com/s/articleView?id=sf.admin_exportdata.htm&type=5)
- [Jira](https://confluence.atlassian.com/adminjiraserver/backing-up-data-938847673.html)
- [Confluence](https://confluence.atlassian.com/doc/manually-backing-up-the-site-152405.html)
- [Asana](https://asana.com/guide/help/faq/security#gl-full-org-export)
- [HubSpot](https://knowledge.hubspot.com/account/export-your-content-and-data)
- [ServiceNow](https://docs.servicenow.com/bundle/rome-platform-administration/page/administer/export-sets/concept/c_ExportSets.html)
- [ClickUp](https://docs.clickup.com/en/articles/1907587-data-portability-export-your-workspace-s-data)
- [Notion](https://www.notion.so/help/back-up-your-data)
- [Coda](https://help.coda.io/en/articles/1222787-how-can-i-export-data-from-coda)
- [Monday.com](https://support.monday.com/hc/en-us/articles/360002543719-How-to-export-your-entire-account-s-data)
- [Linear](https://linear.app/docs/google-sheets)

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create a local ngrok tunnel to point to your webhook server.

```bash
./ngrok http 8000
```

4. Set your environment variables: your Nightfall API key, your Nightfall signing secret, your Nightfall [detection rule UUID](https://docs.nightfall.ai/docs/creating-detection-rules), your webhook server URL from ngrok, and the path to your extracted directory/export/backup that you want to crawl.

Your Nightfall detection rule UUID is optional. If not specified, the default rule will detect likely credit card numbers, US social security numbers, and API keys.

```bash
export NIGHTFALL_API_KEY=<your_key_here>
export NIGHTFALL_SIGNING_SECRET=<your_secret_here>
export NIGHTFALL_DETECTION_RULE_UUID=<your_uuid_here>
export NIGHTFALL_SERVER_URL=https://<your_subdomain_here>.ngrok.io
export SALESFORCE_BACKUP_PATH='/Users/myuser/salesforce-exports/'
```

5. Start your webhook server. This runs `app.py`.

```bash
gunicorn app:app
```

6. Run your scan.

```python
python scanner.py
```

7. Monitor your webhook server output. Once all file scan events have been received and the scan is complete, view your results in `results.csv`. Each row in the output CSV will correspond to a sensitive finding. Each row will have the following fields, which you can customize in your webhook server in `app.py`: 

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
