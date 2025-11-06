# AI-Powered Lead Scoring & Prioritization (SDR Demo)

A demo project aligned with LeadSquared's SDR workflows: intake leads, score by conversion likelihood, prioritize, visualize, and trigger basic outreach.

## Features
- Upload lead lists (CSV)
- Train a simple ML model (Logistic Regression) on sample or your labeled data
- Score & prioritize leads (Very High ... Very Low)
- Visualize priority distribution
- (Optional) Send intro emails to top leads via SMTP

## Tech Stack
- Streamlit (UI)
- scikit-learn (ML)
- pandas / numpy (data)
- matplotlib (charts)
- joblib (model persistence)
- python-dotenv (email config)

## Local Setup

```bash
# 1) Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) (Optional) Train on sample data
python models/train.py

# 4) Run the app
streamlit run frontend/streamlit_app.py
```

Open the link shown in your terminal (usually http://localhost:8501).

## CSV Format

Required modeling columns:
- `industry`, `lead_source`, `region` (categorical)
- `employees`, `pages_visited`, `emails_opened`, `last_contact_days` (numeric)

Optional columns (kept and shown in UI): `name`, `email`, `company`, etc.

If you want to train on your own data, include a binary target column `converted` (0/1).

## Email Automation (Optional)
1. Copy `.env.example` to `.env` and fill your SMTP settings.  
2. In Gmail, use an **App Password** (not your normal password).  
3. In the UI, go to **Automation** and click *Send*. If env is missing, it falls back to simulation.

## Docker (One-Command Run)

```dockerfile
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "frontend/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build & run:

```bash
docker build -t leadscorer .
docker run -p 8501:8501 leadscorer
```

## Deploy Options

### 1) Streamlit Community Cloud (easiest)
- Push this folder to a GitHub repo.
- Go to share.streamlit.io, choose the repo, set the main file to `frontend/streamlit_app.py`.
- Add secrets (for SMTP) in Streamlit Settings if needed.

### 2) Render (Docker or Python)
- **Docker**: Connect your repo, Render auto-builds the Dockerfile.
- **Python App**: Set `Start Command`: `streamlit run frontend/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

### 3) Any VM (AWS/GCP/Azure)
- Install Docker and run as above, or run Python directly via `tmux`/`systemd`.

## Project Narrative (Use in your Resume)
- Built a ML-backed lead scoring prototype that prioritizes prospects for SDR workflows.
- Mimics CRM behaviors: intake, scoring, prioritization, export, and basic automated outreach.
- Demonstrates understanding of sales KPIs (qualified pipeline) and data hygiene (consistent columns, export).

## Roadmap Ideas
- Add login/auth and user roles
- Connect to LinkedIn/ZoomInfo APIs for enrichment
- Export leads to Salesforce/HubSpot via API
- A/B test email templates and track open/reply rates
