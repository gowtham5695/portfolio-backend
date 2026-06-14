from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from backend.schemas.schemas import CertificationCreate, CertificationResponse
from backend.database import certifications_collection, serialize_doc, serialize_list
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/certifications", tags=["Certifications"])

@router.get("", response_model=List[CertificationResponse])
async def get_certifications():
    cursor = certifications_collection.find({})
    certs = await cursor.to_list(length=1000)
    return serialize_list(certs)

@router.post("", response_model=CertificationResponse, status_code=status.HTTP_201_CREATED)
async def create_certification(data: CertificationCreate, current_admin: dict = Depends(get_current_admin)):
    result = await certifications_collection.insert_one(data.model_dump())
    new_cert = await certifications_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_cert)

@router.put("/{cert_id}", response_model=CertificationResponse)
async def update_certification(cert_id: str, data: CertificationCreate, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(cert_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Certification ID format")
    
    result = await certifications_collection.update_one({"_id": oid}, {"$set": data.model_dump()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Certification not found")
        
    updated = await certifications_collection.find_one({"_id": oid})
    return serialize_doc(updated)

@router.delete("/{cert_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_certification(cert_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(cert_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Certification ID format")
        
    result = await certifications_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Certification not found")
    return None
