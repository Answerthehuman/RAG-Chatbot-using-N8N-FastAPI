# n8n RAG Connector

This repository contains a generic FastAPI wrapper (`main.py`) and an n8n workflow export (`n8n_flow.json`) for a retrieval-augmented generation (RAG) flow.

## What this repo contains

- `main.py` — a simple FastAPI service that sends a `prompt` to an n8n webhook and returns the response.
- `n8n_flow.json` — an n8n workflow export that defines how n8n receives the prompt, performs RAG/document retrieval, and returns a response.
- `requirements.txt` — Python dependencies for the FastAPI app.

## Setup overview

1. Run n8n locally with Docker.
2. Import the provided n8n JSON flow.
3. Configure credentials and placeholder values in n8n.
4. Update `main.py` with your n8n webhook URL.
5. Start the FastAPI app and test the `/chat` endpoint.

## 1. Run n8n locally with Docker

### Option 1: `docker run`

```bash
docker run -it --rm \
  -p 5678:5678 \
  -e GENERIC_TIMEZONE="UTC" \
  -e N8N_BASIC_AUTH_ACTIVE="false" \
  n8nio/n8n:latest
```

### Option 2: `docker compose`

Create a `docker-compose.yml` file with this content if you want a reusable setup:

```yaml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n:latest
    ports:
      - "5678:5678"
    environment:
      - GENERIC_TIMEZONE=UTC
      - N8N_BASIC_AUTH_ACTIVE=false
    volumes:
      - ./n8n:/home/node/.n8n
```

Then run:

```bash
docker compose up
```

### Confirm n8n is running

Open:

```text
http://localhost:5678
```

You should see the n8n editor interface.

## 2. Import the n8n flow

1. In the n8n editor, click the menu in the top-right corner.
2. Choose `Import` > `File`.
3. Select `n8n_flow.json`.
4. Save the imported workflow.

## 3. Configure the n8n workflow

The imported workflow contains the following placeholder configuration values:

- `googlePalmApi` credentials in the embeddings and chat model nodes.
- `googleDriveOAuth2Api` credentials in Google Drive nodes.
- `postgres` credentials in the vector store and memory nodes.
- `folderToWatch.value` in Google Drive trigger nodes.

### What to update

- For Google Gemini embedding/chat nodes: add your Google PaLM/Gemini credential if you use that provider.
- For Google Drive nodes: add your own Google Drive OAuth credential and target folder ID.
- For Postgres nodes: add your Postgres credential and ensure Postgres is reachable.

> If you do not use Google Drive ingestion, you can remove or disable the Google Drive search/download trigger nodes.

### Webhook path

The workflow currently uses the webhook path:

```text
/webhook/newragtest
```

If you change this path in n8n, update `N8N_WEBHOOK_URL` in `main.py` accordingly.

## 4. Configure `main.py`

Open `main.py` and update the `N8N_WEBHOOK_URL` constant with your actual n8n webhook URL.

```python
N8N_WEBHOOK_URL = "http://localhost:5678/webhook/newragtest"
```

If n8n runs on a different host, port, or webhook path, adjust it.

## 5. Run the FastAPI app

Create a Python environment and install dependencies:

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Start the app:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 6. Test the integration

Send a prompt to the FastAPI app:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Hello from n8n"}'
```

If n8n is running and the webhook is configured correctly, the response should come back from the n8n workflow.

## How `main.py` and the n8n JSON interact

- `main.py` accepts a JSON POST at `/chat` with a `prompt` field.
- It forwards that prompt to the n8n webhook URL defined by `N8N_WEBHOOK_URL`.
- n8n receives the webhook payload and passes it through the workflow.
- The workflow uses the `body.prompt` value from the incoming request as the user query.
- The n8n workflow performs retrieval, vector store operations, memory, and agent processing.
- `Respond to Webhook` returns the final result back through n8n to the FastAPI app.
- `main.py` then returns that response as its API output.

## Notes

- This repo is intentionally generic. It expects you to add your own service credentials and Google Drive folder details.
- If you want to use a different vector database or model provider, adjust the nodes in the imported n8n workflow.
- If n8n is not on `localhost:5678`, update both `main.py` and `README` commands to match your environment.
