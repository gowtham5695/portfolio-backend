from fastapi import APIRouter, Depends, HTTPException
from backend.schemas.schemas import ProfileUpdate, ProfileResponse
from backend.database import profile_collection, serialize_doc
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/profile", tags=["Profile"])

@router.get("", response_model=ProfileResponse)
async def get_profile():
    profile = await profile_collection.find_one({})
    if not profile:
        raise HTTPException(status_code=404, detail="Profile details not found in database")
    return serialize_doc(profile)

@router.put("", response_model=ProfileResponse)
async def update_profile(data: ProfileUpdate, current_admin: dict = Depends(get_current_admin)):
    profile = await profile_collection.find_one({})
    if not profile:
        # Create one if missing
        res = await profile_collection.insert_one(data.model_dump())
        new_profile = await profile_collection.find_one({"_id": res.inserted_id})
        return serialize_doc(new_profile)
    
    await profile_collection.update_one(
        {"_id": profile["_id"]},
        {"$set": data.model_dump()}
    )
    updated_profile = await profile_collection.find_one({"_id": profile["_id"]})
    return serialize_doc(updated_profile)
