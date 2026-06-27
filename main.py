from fastapi import FastAPI, Form, BackgroundTasks
from pydantic import BaseModel
import httpx
import requests
from typing import Annotated

N8N_WEBHOOK_URL = "http://localhost:5678/webhook/newragtest"  # Replace with your actual n8n webhook URL

app = FastAPI(title="RAG Chatbot", description="A generic RAG chatbot connector for n8n", version="1.0.0")

class Prompt(BaseModel):
    prompt: str

@app.post("/chat")
def chat_with_rag(payload: Prompt):
    """Send a message to the N8N RAG workflow and return the response"""
    response = requests.post(N8N_WEBHOOK_URL, json={"prompt": payload.prompt})
    response.raise_for_status()

    return response.json()


#SLACK Prompt to be sent to N8N and response to be sent back to slack
def send_slack_response(response_url: str, prompt: str):
    """Background me query process hogi to avoid slack timeout"""
    
    try:
        # Create Prompt object following your existing Pydantic model
        payload = Prompt(prompt=prompt)
        
        # Send to N8N using the same logic
        response = requests.post(N8N_WEBHOOK_URL, json={"prompt": payload.prompt})
        response.raise_for_status()
        
        # Extract response text
        rag_response = response.json()

        # If N8N returns a list, get the first item
        if isinstance(rag_response, list):
            rag_response = rag_response[0] if rag_response else {}

        response_text = (
            rag_response.get("output") or 
            rag_response.get("text") or 
            rag_response.get("answer") or 
            str(rag_response)
        )

        formatted_response = f" {response_text}"

        # Send response back to Slack using response_url
        requests.post(response_url, json={
            "response_type": "in_channel",  # visible to everyone, use "ephemeral" for private
            "text": formatted_response
        })
        
    except Exception as e:
        # Send error message back to Slack
        requests.post(response_url, json={
            "response_type": "ephemeral",
            "text": f"AHHHH errror in the processing: {str(e)}"
        })


@app.post("/slack")
async def slack_command( background_tasks: BackgroundTasks, text: Annotated[str, Form()], response_url: Annotated[str, Form()]):
    """ 
    Ingest query from slash command, extract text from the form data, and response url 
    """

    background_tasks.add_task(send_slack_response, response_url, text) #Process the n8n in  background

    
    return {
        "response_type": "in_channel",
        "text": f"Hi! How's it going? If you have asked me a question, I am processing it and will get back to you shortly"
    }


@app.get("/health")
async def health_check():
    """Check if the BOTH THE API and N8N connection are working fine or not"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:5678/healthz")
            return {"status": "healthy", "n8n_status": response.status_code == 200}
    except:
        return {"status": "healthy", "n8n_status": False}
