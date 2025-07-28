# Medical Research Agent 🔬

Search PubMed's 35+ million biomedical articles with AI-powered analysis.

## Quick Start

```bash
python play.py
```

That's it! Your browser will open with a beautiful search interface.

## What It Does

The Medical Research Agent helps you:
- Search PubMed's comprehensive biomedical database
- Get AI-powered summaries of research findings
- Filter by date, open access, and more
- Export results for further analysis

## Features

✨ **Simple Web Interface** - Just type your query and click search
🚀 **Fast Results** - Powered by NCBI's E-utilities API  
🤖 **AI Analysis** - Get intelligent summaries of research trends
📊 **Smart Filtering** - Date ranges, open access, clinical trials
🔒 **Rate Limited** - Respects NCBI's usage guidelines

## Example Searches

- "Latest treatments for Type 2 Diabetes"
- "CRISPR gene therapy clinical trials 2023"
- "COVID-19 vaccine efficacy studies"
- "Alzheimer's prevention research"

## Requirements

- Python 3.8+
- Internet connection
- Modern web browser

## First Time Setup

```bash
# Install dependencies
pip install pdm
pdm install

# Run the app
python play.py
```

## API Access

The app also provides a REST API at `http://localhost:8000/docs`

---

Built with ❤️ using MCP Protocol and NCBI E-utilities
