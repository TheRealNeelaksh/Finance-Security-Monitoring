#This defines the JSON format your frontend must send.
from pydantic import BaseModel
from typing import List, Optional

class LoginEvent(BaseModel):
    user_id: str
    # Features for the Behavioral Models (Time, Lat, Long, DeviceID_Int, etc.)
    features: List[float] 
    
    # History for the Sequence Model (Last 10 actions)
    # Each action is a list of features (e.g., [ActionCode, Timestamp])
    sequence_data: List[List[float]]

class AnalysisResponse(BaseModel):
    user_id: str
    verdict: str
    risk_score: float
    breakdown: dict