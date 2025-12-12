import os
from dotenv import load_dotenv # <--- IMPORT THIS

# 1. LOAD SECRETS (Must be before other imports)
load_dotenv()

# Force Legacy Keras
os.environ["TF_USE_LEGACY_KERAS"] = "1"

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.services import ai_engine
from typing import List

app = FastAPI(title="AI Financial Security System")

# Debug: Print to console to prove credentials are loaded
# (Don't show this screen to judges!)
print(f"📧 Email Configured: {os.getenv('MAIL_USERNAME')}")
print(f"🤖 AI Key Configured: {'Yes' if os.getenv('GEMINI_API_KEY') else 'No'}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

app.state.manager = manager

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting AI Engine...")
    ai_engine.load_models()

app.include_router(api_router)

@app.get("/")
def home():
    return {"status": "System Active", "version": "2.0.0"}