from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
import json

app = FastAPI()

# Allow CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def get_dashboard():
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    return FileResponse(dashboard_path)

# Broadcast channel for real-time state updates
clients = set()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except:
        clients.remove(websocket)

async def broadcast_state(state: dict):
    """Sends current AgentState to all connected dashboard clients."""
    if not clients:
        return
        
    message = json.dumps(state)
    for client in clients:
        try:
            await client.send_text(message)
        except:
            pass

def start_api_server():
    """Starts the FastAPI server in a background thread."""
    uvicorn.run(app, host="0.0.0.0", port=8000)
