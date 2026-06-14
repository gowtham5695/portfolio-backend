from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from backend.schemas.schemas import EducationCreate, EducationResponse
from backend.database import education_collection, serialize_doc, serialize_list
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/education", tags=["Education"])

@router.get("", response_model=List[EducationResponse])
async def get_education():
    cursor = education_collection.find({})
    items = await cursor.to_list(length=1000)
    return serialize_list(items)

@router.post("", response_model=EducationResponse, status_code=status.HTTP_201_CREATED)
async def create_education(data: EducationCreate, current_admin: dict = Depends(get_current_admin)):
    result = await education_collection.insert_one(data.model_dump())
    new_item = await education_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_item)

@router.put("/{education_id}", response_model=EducationResponse)
async def update_education(education_id: str, data: EducationCreate, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(education_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Education ID format")
    
    result = await education_collection.update_one({"_id": oid}, {"$set": data.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Education item not found")
        
    updated = await education_collection.find_one({"_id": oid})
    return serialize_doc(updated)

@router.delete("/{education_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_education(education_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(education_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Education ID format")
        
    result = await education_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Education item not found")
    return None
