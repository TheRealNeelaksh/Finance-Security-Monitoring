from fastapi import APIRouter, HTTPException
from app.schemas.request import LoginEvent, AnalysisResponse
from app.services import ai_engine

router = APIRouter()

@router.post("/analyze-login", response_model=AnalysisResponse)
async def analyze_login(data: LoginEvent):
    try:
        # 1. Get raw scores from AI Engine
        scores = ai_engine.predict(data.user_id, data.features, data.sequence_data)
        
        # 2. The Ensemble Logic (Manual Weights)
        # We trust Network (Graph) and LSTM (Sequence) the most
        final_risk = (
            (scores['iso'] * 0.1) +
            (scores['ae'] * 0.2) +
            (scores['lstm'] * 0.3) +
            (scores['network'] * 0.4)
        )
        
        # 3. Determine Verdict
        verdict = "ALLOW"
        if final_risk > 0.85:
            verdict = "BLOCK"
        elif final_risk > 0.65:
            verdict = "MFA_CHALLENGE"
            
        return AnalysisResponse(
            user_id=data.user_id,
            verdict=verdict,
            risk_score=round(final_risk, 4),
            breakdown=scores
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))