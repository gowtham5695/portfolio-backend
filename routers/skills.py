from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from backend.schemas.schemas import SkillCreate, SkillResponse
from backend.database import skills_collection, serialize_doc, serialize_list
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/skills", tags=["Skills"])

@router.get("", response_model=List[SkillResponse])
async def get_skills():
    cursor = skills_collection.find({})
    skills = await cursor.to_list(length=1000)
    return serialize_list(skills)

@router.post("", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(data: SkillCreate, current_admin: dict = Depends(get_current_admin)):
    result = await skills_collection.insert_one(data.model_dump())
    new_skill = await skills_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_skill)

@router.put("/{skill_id}", response_model=SkillResponse)
async def update_skill(skill_id: str, data: SkillCreate, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(skill_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Skill ID format")
    
    result = await skills_collection.update_one({"_id": oid}, {"$set": data.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Skill not found")
        
    updated = await skills_collection.find_one({"_id": oid})
    return serialize_doc(updated)

@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(skill_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(skill_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Skill ID format")
        
    result = await skills_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Skill not found")
    return None
