# YouTube Automation Toolkit 🚀

A modular, production-ready Python automation system for the YouTube Data API.

## 🌟 Features

*   **YouTube API Integration**: Fetch channel and video metadata with pagination support.
*   **Analytics Engine**: Calculate average views, engagement rate, and upload frequency.
*   **Workflow Automation**: Run multi-step automations (reports, notifications, monitoring) via YAML/JSON configs.
*   **Visual Reports**: Generate professional HTML reports with performance charts.
*   **Multi-Channel Notifications**: Send alerts via Slack and Telegram webhooks.
*   **Background Scheduler**: Schedule periodic workflows using APScheduler.
*   **FastAPI REST Interface**: Clean API endpoints for manual triggers and status monitoring.

## 🛠️ Tech Stack

*   **Backend**: Python, FastAPI
*   **Validation**: Pydantic v2
*   **API Client**: google-api-python-client
*   **Data Analysis**: Pandas, Matplotlib
*   **Automation**: APScheduler, PyYAML
*   **Logging**: Loguru

## 🚀 Getting Started

### 1. Prerequisites
*   Python 3.10+
*   YouTube Data API Key ([Google Cloud Console](https://console.cloud.google.com/))

### 2. Installation
```bash
# Clone the repository
# git clone ...
# cd youtube-automation-toolkit

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
Rename `.env.example` to `.env` and fill in your API keys:
```env
YOUTUBE_API_KEY=your_key_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

### 4. Running the Application
```bash
python -m app.main
```
The API will be available at `http://localhost:8000`. Explore documentation at `/docs`.

## 🤖 Workflow Example

Define your automation in `app/workflows/weekly_report.yaml`:
```yaml
name: Weekly Channel Report
steps:
  - name: Get Channel Info
    action: fetch_channel
    params: { channel_id: "UC_x5..." }
  - name: Analyze Performance
    action: analyze_stats
  - name: Generate Visual Report
    action: generate_report
```

## 🧪 Testing
```bash
pytest
```

## 📂 Project Structure
```text
youtube-automation/
├── app/
│   ├── main.py            # FastAPI entry point
│   ├── services/          # Business logic (YouTube, Analytics, Reports)
│   ├── workflows/         # Workflow engine and example configs
│   ├── models/            # Pydantic schemas
│   └── templates/         # HTML report templates
├── reports/               # Generated results
└── tests/                 # Unit tests
```
