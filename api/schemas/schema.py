from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AttachmentBase(BaseModel):
    filename: str
    driver: int
    type: str
    user_id: Optional[int] = None
    post_id: Optional[int] = None
    story_id: Optional[int] = None
    message_id: Optional[int] = None
    collab_id: Optional[int] = None
    coconut_id: Optional[str] = None
    has_thumbnail: Optional[bool] = None
    has_blurred_preview: Optional[bool] = None
    payment_request_id: Optional[int] = None
    is_personal_details_detected: bool = False

class AttachmentCreate(AttachmentBase):
    pass

class AttachmentUpdate(BaseModel):
    filename: Optional[str] = None
    driver: Optional[int] = None
    type: Optional[str] = None
    user_id: Optional[int] = None
    post_id: Optional[int] = None
    story_id: Optional[int] = None
    message_id: Optional[int] = None
    collab_id: Optional[int] = None
    coconut_id: Optional[str] = None
    has_thumbnail: Optional[bool] = None
    has_blurred_preview: Optional[bool] = None
    payment_request_id: Optional[int] = None
    is_personal_details_detected: Optional[bool] = None

class Attachment(AttachmentBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
