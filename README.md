## Tech Stack

* **Backend:** Python, FastAPI, LiveKit Voice Agent SDK, UV
* **Frontend:** React, Next.js / Vite, TypeScript, Tailwind CSS
* **Database:** PostgreSQL
* **Containerization & Dev:** Docker

# Docker Setup & Usage Guide

## Quick Start

### 1. Configure Environment
Copy the example environment file:
```bash
cp .env.example backend/.env.local
```
## 2. Start All Services
```bash
docker compose up --build -d
```
### Check db after conversation
```bash
docker exec -it app_db psql -U app_user -d app_db
```
