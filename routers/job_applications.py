from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from backend.schemas.schemas import JobApplicationCreate, JobApplicationResponse
from backend.database import job_applications_collection, serialize_doc, serialize_list
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/job-applications", tags=["Job Applications"])

@router.get("", response_model=List[JobApplicationResponse])
async def get_job_applications(current_admin: dict = Depends(get_current_admin)):
    # Sort by date_applied descending
    cursor = job_applications_collection.find({}).sort("date_applied", -1)
    apps = await cursor.to_list(length=500)
    return serialize_list(apps)

@router.post("", response_model=JobApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_job_application(data: JobApplicationCreate, current_admin: dict = Depends(get_current_admin)):
    result = await job_applications_collection.insert_one(data.model_dump())
    new_app = await job_applications_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_app)

@router.put("/{app_id}", response_model=JobApplicationResponse)
async def update_job_application(app_id: str, data: JobApplicationCreate, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(app_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
    
    result = await job_applications_collection.update_one({"_id": oid}, {"$set": data.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Job application card not found")
        
    updated = await job_applications_collection.find_one({"_id": oid})
    return serialize_doc(updated)

@router.delete("/{app_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job_application(app_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(app_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid application ID format")
        
    result = await job_applications_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job application card not found")
    return None
