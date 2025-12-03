from fastapi import APIRouter
# DIRECT IMPORT: We import the 'router' variable directly from the file
from app.api.analyze import router as security_router

api_router = APIRouter()

# We attach the router we just imported
api_router.include_router(security_router, prefix="/security", tags=["Security"])