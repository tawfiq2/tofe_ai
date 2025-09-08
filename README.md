# Monitoring Prototype

This repository contains two entry points for a monitoring prototype:

* `monitoring_agent.py` – scans application log files for errors and pushes
  events to Elasticsearch. When an incident is detected the agent sends
  notifications, schedules a Teams meeting, and prepares a PDF summary.
* `web_app.py` – a minimal Flask web application that exposes a `/logs`
  endpoint for listing stored events from Elasticsearch.
* `ops_console.py` – a FastAPI operations console providing placeholder
  endpoints for incidents, runbooks and a RAG powered chatbot.

All external integrations (Elasticsearch, Twilio, SMTP, Microsoft Graph, PDF
creation) are represented as placeholders. Provide valid credentials through
environment variables when running the scripts in a real environment.

## Usage

```bash
# Run the monitoring agent
python monitoring_agent.py

# Start the web interface
python web_app.py

# Run the AI operations console
uvicorn ops_console:app --reload
```

All scripts expect an Elasticsearch instance at `ELASTIC_HOST` (defaults to
`http://localhost:9200`).

## Download OutSystems Source Code

`outsystems_source_download.py` automates retrieving application or module source
code from an OutSystems LifeTime environment. The script follows the official
API flow of requesting a package, waiting for its preparation and downloading
the resulting ZIP file.

Set the following environment variables with your LifeTime endpoint and API
access token:

```bash
export LIFETIME_BASE="https://hostname.outsystems.com"
export LIFETIME_TOKEN="<api token>"
```

Download an application's source code:

```bash
python outsystems_source_download.py --env Testing --app EmployeeBackoffice --output app.zip
```

Download a module's source code:

```bash
python outsystems_source_download.py --env Testing --module EmployeeBackoffice --output module.zip
```

The script resolves environment, application and module names to their respective
keys automatically.
