from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from backend.schemas.schemas import ProjectCreate, ProjectResponse
from backend.database import projects_collection, serialize_doc, serialize_list
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("", response_model=List[ProjectResponse])
async def get_projects():
    cursor = projects_collection.find({})
    projects = await cursor.to_list(length=1000)
    return serialize_list(projects)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(data: ProjectCreate, current_admin: dict = Depends(get_current_admin)):
    result = await projects_collection.insert_one(data.model_dump())
    new_project = await projects_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_project)

@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, data: ProjectCreate, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(project_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Project ID format")
    
    result = await projects_collection.update_one({"_id": oid}, {"$set": data.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
        
    updated = await projects_collection.find_one({"_id": oid})
    return serialize_doc(updated)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(project_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(project_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Project ID format")
        
    result = await projects_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Project not found")
    return None
