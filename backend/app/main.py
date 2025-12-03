import os
# ⚠️ THIS MUST BE THE VERY FIRST LINE OF CODE
# It forces TensorFlow to use the "Old Keras" that matches your teammate's code
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.services import ai_engine
from typing import List

app = FastAPI(title="AI Financial Security System")

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- WEBSOCKET MANAGER (Objective 3: Real-Time Alerts) ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        # Push message to all connected dashboards
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# This is the "Channel" the frontend listens to
@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Store manager so other files (like analyze.py) can use it
app.state.manager = manager

# --- STARTUP ---
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting AI Engine...")
    ai_engine.load_models()

app.include_router(api_router)

@app.get("/")
def home():
    return {"status": "System Active", "version": "2.0.0"}