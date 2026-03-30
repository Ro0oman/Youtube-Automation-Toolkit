# 🚀 YouTube Intelligence Suite v3.0

A professional, production-ready framework for YouTube channel analytics, strategic insights, and automated reporting. Built with **FastAPI**, **SQLAlchemy**, and **Clean Architecture** to demonstrate high-level engineering standards.

![Dashboard Preview](https://via.placeholder.com/1000x500/f8fafc/ff0000?text=YouTube+Intelligence+v3+SaaS+Dashboard)

## ✨ Features

- **🧠 Domain-Driven Scoring**: Automatically calculates a 0-10 "Channel Health Score" based on engagement, consistency, and benchmark performance.
- **📈 Historical Evolution**: Tracks performance over time using SQLite. Detects growth trends (e.g., "Engagement is up 12% vs last month").
- **💡 Strategic Insights**: Identifies "Topic Gaps" by comparing your channel with trending competitors and suggests high-impact video ideas.
- **📄 SaaS-Grade Reports**: Generates premium HTML dashboards with color-coded status pills and actionable advice cards.
- **🌐 RESTful API**: Fully documented FastAPI backend with endpoints for analysis, history, and report management.
- **🐳 Production-Ready**: Includes a multi-stage Dockerfile and full unit testing suite.

## 🏗️ Architecture

The project follows a **Layered Architecture** to ensure maintainability and testability:

- `app/api`: FastAPI routers and endpoints.
- `app/domain`: Core business logic, scoring rules, and data entities.
- `app/infra`: Database repository (SQLAlchemy), YouTube client, and Report engine.
- `app/core`: Centralized configuration and logging.

## 🚀 Getting Started

### ⚡ Option 1: One-Click Demo (Recommended for Recruiters)
Run the system immediately without an API Key to see a "Perfect Showcase" report:
```bash
python demo.py
```

### 🐍 Option 2: Local Setup
1. **Clone & Install**:
```bash
pip install -r requirements.txt
```
2. **Configure Environment**:
Create a `.env` file from the example:
```bash
cp .env.example .env
# Add your YOUTUBE_API_KEY
```
3. **Run the API**:
```bash
python -m app.main
```
4. **Interactive Docs**:
Navigate to `http://localhost:8000/docs` to test the endpoints.

## 🐳 Docker Support
Run the entire suite inside a container:
```bash
docker build -t yt-intelligence .
docker run -p 8000:8000 --env-file .env yt-intelligence
```

## 🧪 Testing
Run the domain logic tests:
```bash
pytest app/tests/test_domain.py
```

---
Powered by **YouTube Intelligence Suite v3.0** | Designed for Growth.
