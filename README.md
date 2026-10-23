# LegalBot — Multi-Agent Legal Assistant

LegalBot is an AI-powered legal assistance project designed to help users ask legal questions and receive structured responses using a multi-agent architecture and a FastAPI backend. The project combines an API-driven application with a lightweight web interface and Docker-based containerization.

> **Disclaimer:** LegalBot is an educational project, not a substitute for professional legal advice. AI-generated responses may be inaccurate and should be independently verified.

## Key Features

- **Multi-Agent Architecture:** Organizes legal question processing through a team of AI agents.
- **FastAPI Backend:** Provides API endpoints for interacting with the application.
- **Web Interface:** Includes a frontend built with HTML, CSS, and JavaScript.
- **REST API:** Supports question submission through the `/ask` endpoint.
- **Health Monitoring:** Provides a `/health` endpoint for application health checks.
- **Interactive API Documentation:** Uses FastAPI's automatically generated API documentation.
- **Docker Containerization:** Packages the application and its dependencies into a reproducible container environment.
- **Environment-Based Configuration:** Supports configuration through environment variables.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| AI Agent Framework | Agno |
| API Server | Uvicorn |
| Frontend | HTML, CSS, JavaScript |
| Containerization | Docker |
| API Documentation | Swagger UI / OpenAPI |
| Testing | pytest |

## Project Structure

```text
LegalBot/
├── app/
│   ├── agents/
│   │   ├── legal_team.py
│   │   └── tools.py
│   ├── data/
│   │   └── sample_documents.py
│   ├── static/
│   │   ├── index.html
│   │   ├── style.css
│   │   └── app.js
│   ├── config.py
│   ├── main.py
│   └── schemas.py
├── tests/
│   ├── test_health.py
│   ├── test_validation.py
│   └── test_agents.py
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.11 or a compatible Python environment
- pip
- Git
- Docker Desktop (for containerized execution)
- Any API credentials required by your configured AI provider

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/LegalBot.git
cd LegalBot
```

Replace `YOUR-USERNAME` with your GitHub username.

### 2. Create a Virtual Environment

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a local `.env` file from the provided template:

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
cp .env.example .env
```

Add the required configuration values and AI provider credentials according to `app/config.py`.

**Security:** Never commit `.env` or expose API keys in source code, screenshots, logs, or public repositories.

### 5. Run the Application Locally

```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open the following URLs in your browser:

- Web application: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Health endpoint: http://localhost:8000/health

The web interface depends on how the routes are configured in `app/main.py`.

## Run with Docker

Docker packages the application and its dependencies so it can run in a consistent environment.

### 1. Build the Image

Run this command from the project root, where the `Dockerfile` is located:

```bash
docker build -t legalbot:latest .
```

### 2. Start the Container

If your `.env` file has been configured:

```bash
docker run -d --name legalbot-app -p 8000:8000 --env-file .env legalbot:latest
```

### 3. Verify the Container

```bash
docker ps
```

View application logs:

```bash
docker logs legalbot-app
```

Open the application at http://localhost:8000.

### 4. Stop the Container

```bash
docker stop legal