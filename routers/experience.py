from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from backend.schemas.schemas import ExperienceCreate, ExperienceResponse
from backend.database import experience_collection, serialize_doc, serialize_list
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/experience", tags=["Experience"])

@router.get("", response_model=List[ExperienceResponse])
async def get_experience():
    cursor = experience_collection.find({})
    items = await cursor.to_list(length=1000)
    return serialize_list(items)

@router.post("", response_model=ExperienceResponse, status_code=status.HTTP_201_CREATED)
async def create_experience(data: ExperienceCreate, current_admin: dict = Depends(get_current_admin)):
    result = await experience_collection.insert_one(data.model_dump())
    new_item = await experience_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_item)

@router.put("/{exp_id}", response_model=ExperienceResponse)
async def update_experience(exp_id: str, data: ExperienceCreate, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(exp_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Experience ID format")
    
    result = await experience_collection.update_one({"_id": oid}, {"$set": data.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Experience item not found")
        
    updated = await experience_collection.find_one({"_id": oid})
    return serialize_doc(updated)

@router.delete("/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_experience(exp_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(exp_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Experience ID format")
        
    result = await experience_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Experience item not found")
    return None
