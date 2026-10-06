## Tech Stack

* **Backend:** Python, FastAPI, LiveKit Voice Agent SDK
* **Frontend:** React, Next.js / Vite, TypeScript, Tailwind CSS
* **Database:** PostgreSQL
* * **Voice Models:** 
  * **STT (Speech-to-Text):** Deepgram (`nova-3-general`) — *Free API keys available for testing*
  * **LLM (Reasoning):** OpenAI (`gpt-4o-mini`)
  * **TTS (Text-to-Speech):** Cartesia (`sonic-3.6`) — *Free API keys available for testing*
* **Infrastructure:** Docker

# Docker Setup & Usage Guide

## Quick Start

### 1. Configure Environment
Copy the example environment file and paste required API-keys:
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
## How the Voice Agent Works


1. **HTTP Signaling & Room Creation:**
   * When you click "Connect", the frontend sends an HTTP POST request to the backend (`/api/token`)
   * The backend generates a secure JWT token and websocket link(`wss://`) and creates a LiveKit Room
   * **Topic Assignment:** The conversation topic (e.g., "Car Rental Service") is passed during this HTTP request and embedded inside the token's metadata
   * *Why is the topic set on the frontend?* Because it allows you to dynamically change the agent's behavior (e.g., via a dropdown on the website) without restarting the backend server. The backend simply reads the topic from the room metadata when the agent connects

2. **WebRTC for Audio & Events:**
   ** The frontend uses the provided `wss://` link to open a **WebSocket** connection to the LiveKit server. This step is called "signaling".
   * Over this WebSocket, the client and server quickly negotiate connection details (SDP and ICE candidates).
   * Once negotiated, a **WebRTC** connection is established.
   * WebSocket is only used briefly under the hood by LiveKit for the initial WebRTC signaling (exchanging SDP and ICE candidates).

3. **Data Pipeline (Inside the Agent):**
   * The agent receives your voice via WebRTC.
   * It is immediately transcribed by **Deepgram**
   * The text is sent to **OpenAI** to generate a contextual response based on the HTTP-provided topic
   * The text response is sent to **Cartesia** to generate human-like speech
   * The generated audio is streamed back to you via WebRTC.
