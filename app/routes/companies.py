from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.services.company_service import update_liked_status

router = APIRouter()


class LikeRequest(BaseModel):
    company_names: List[str]
    

@router.post("/api/companies/like")
def like_companies(request: LikeRequest):
    result = update_liked_status(request.company_names)
    return result