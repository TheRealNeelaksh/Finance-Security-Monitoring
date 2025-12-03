import os
# ⚠️ THIS MUST BE THE VERY FIRST LINE OF CODE
# It forces TensorFlow to use the "Old Keras" that matches your teammate's code
os.environ["TF_USE_LEGACY_KERAS"] = "1"


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import api_router
from app.services import ai_engine

app = FastAPI(title="AI Financial Early Warning System")

# CORS (Allow Frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Models on Startup
@app.on_event("startup")
async def startup_event():
    ai_engine.load_models()

app.include_router(api_router)

@app.get("/")
def home():
    return {"status": "System Active", "version": "1.0.0"}