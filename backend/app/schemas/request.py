from pydantic import BaseModel
from typing import List, Optional

class LoginEvent(BaseModel):
    user_id: str
    features: List[float] 
    sequence_data: List[List[float]]
    # ✨ NEW FIELD: Optional email for the demo
    target_email: Optional[str] = None 

class AnalysisResponse(BaseModel):
    user_id: str
    verdict: str
    risk_score: float
    breakdown: dict