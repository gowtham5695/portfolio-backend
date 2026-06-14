from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from bson.errors import InvalidId
from typing import List
from backend.schemas.schemas import MessageCreate, MessageResponse
from backend.database import messages_collection, serialize_doc, serialize_list
from backend.routers.auth import get_current_admin

router = APIRouter(prefix="/messages", tags=["Messages"])

@router.post("", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message(data: MessageCreate):
    msg_dict = data.model_dump()
    msg_dict["created_at"] = datetime.utcnow()
    result = await messages_collection.insert_one(msg_dict)
    new_msg = await messages_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(new_msg)

@router.get("", response_model=List[MessageResponse])
async def get_messages(current_admin: dict = Depends(get_current_admin)):
    cursor = messages_collection.find({}).sort("created_at", -1)
    messages = await cursor.to_list(length=1000)
    return serialize_list(messages)

@router.delete("/{msg_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(msg_id: str, current_admin: dict = Depends(get_current_admin)):
    try:
        oid = ObjectId(msg_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid Message ID format")
        
    result = await messages_collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Message not found")
    return None
