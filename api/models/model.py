from sqlalchemy import Column, Integer, BigInteger, Text, String, CHAR, TIMESTAMP, Boolean
from db import Base

class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(CHAR(36), primary_key=True)
    filename = Column(Text, nullable=False)
    driver = Column(Integer, nullable=False)
    type = Column(String(191), nullable=False, index=True)
    user_id = Column(BigInteger(unsigned=True), nullable=True, index=True)
    post_id = Column(BigInteger(unsigned=True), nullable=True, index=True)
    story_id = Column(BigInteger(unsigned=True), nullable=True, index=True)
    message_id = Column(BigInteger(unsigned=True), nullable=True, index=True)
    collab_id = Column(BigInteger(unsigned=True), nullable=True, index=True)
    coconut_id = Column(String(191), nullable=True, index=True)
    has_thumbnail = Column(Boolean, nullable=True)
    has_blurred_preview = Column(Boolean, nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)
    payment_request_id = Column(BigInteger(unsigned=True), nullable=True, index=True)
    is_personal_details_detected = Column(Boolean, nullable=False, default=False)
