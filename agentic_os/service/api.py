from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import os
import json
from pathlib import Path
from agentic_os.utils.logger import logger

from fastapi.staticfiles import StaticFiles

app = FastAPI()
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Allow CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the dashboard
@app.get("/")
async def get_dashboard():
    dashboard_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    return FileResponse(dashboard_path)

# Serve the logs for vision replay
logs_path = str(PROJECT_ROOT / "logs")
if not os.path.exists(logs_path):
    os.makedirs(logs_path)
app.mount("/logs", StaticFiles(directory=logs_path), name="logs")

from pydantic import BaseModel
import asyncio

class TaskRequest(BaseModel):
    goal: str

# Broadcast channel for real-time state updates
clients = set()
app_state = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except:
        clients.remove(websocket)

async def _do_broadcast(state: dict):
    """Internal async broadcast."""
    if not clients:
        return
    message = json.dumps(state)
    for client in list(clients):
        try:
            await client.send_text(message)
        except:
            clients.remove(client)

def broadcast_state(state: dict):
    """Thread-safe way to send AgentState to connected clients."""
    loop = app_state.get('loop')
    if loop and loop.is_running():
        loop.call_soon_threadsafe(asyncio.create_task, _do_broadcast(state))

@app.post("/api/run_task")
async def run_task(req: TaskRequest):
    graph = app_state.get('graph')
    memory = app_state.get('memory')
    if not graph or not memory:
        return {"error": "System not fully initialized."}
        
    # Run the task in a background thread to avoid blocking the API
    import threading
    
    def execute_task(goal):
        logger.info(f"API Backend: Executing goal from Dashboard - {goal}")
        task_id = memory.record_task(goal)
        initial_state = {
            "goal": goal,
            "plan": [],
            "current_step_index": 0,
            "tool_outputs": [],
            "history": [],
            "status": "started",
            "final_result": None,
            "reflection": None,
            "wisdom": [],
            "research_notes": None,
            "missing_tool": None,
            "rejection_count": 0,
            "summary": None
        }
        
        broadcast_state(initial_state)
        result_state = graph.invoke(initial_state)
        broadcast_state(result_state)
        
        memory.update_task_status(task_id, result_state['status'])
        logger.info(f"API Backend: Task complete for - {goal}")
        
    threading.Thread(target=execute_task, args=(req.goal,), daemon=True).start()
    return {"status": "Task started", "goal": req.goal}

import socket

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def start_api_server(graph=None, memory=None):
    """Starts the FastAPI server in a background thread with discovery."""
    app_state['graph'] = graph
    app_state['memory'] = memory
    
    port = 8000
    while is_port_in_use(port):
        logger.info(f"Port {port} in use, trying {port + 1}...")
        port += 1
        
    logger.info(f"Neural Dashboard active at: http://localhost:{port}")
    
    # Store the loop for thread-safe broadcasting
    app_state['loop'] = asyncio.new_event_loop()
    asyncio.set_event_loop(app_state['loop'])
    
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error", loop="asyncio")
    server = uvicorn.Server(config)
    app_state['loop'].run_until_complete(server.serve())
