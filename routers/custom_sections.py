from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from backend.schemas.schemas import CustomSectionCreate, CustomSectionResponse
from backend.database import custom_sections_collection, serialize_doc, serialize_list
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/custom-sections", tags=["Custom Sections"])

@router.get("", response_model=List[CustomSectionResponse])
async def get_custom_sections():
    cursor = custom_sections_collection.find({}).sort("order", 1)
    sections = await cursor.to_list(length=100)
    return serialize_list(sections)

@router.post("", response_model=CustomSectionResponse, status_code=status.HTTP_201_CREATED)
async def create_custom_section(data: CustomSectionCreate, current_admin: dict = Depends(get_current_admin)):
    result = await custom_sections_collection.insert_one(data.model_dump())
    new_section = await custom_sections_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_section)

@router.put("/{section_id}", response_model=CustomSectionResponse)
async def update_custom_section(section_id: str, data: CustomSectionCreate, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(section_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Custom Section ID format")
    
    result = await custom_sections_collection.update_one({"_id": oid}, {"$set": data.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Custom Section not found")
        
    updated = await custom_sections_collection.find_one({"_id": oid})
    return serialize_doc(updated)

@router.delete("/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_custom_section(section_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(section_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Custom Section ID format")
        
    result = await custom_sections_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Custom Section not found")
    return None
