from sqlalchemy import Column, Integer, BigInteger, Text, Boolean, TIMESTAMP, String
from api.database import Base
from sqlalchemy.dialects.mysql import VARCHAR, TINYINT, BIGINT

class UserMessage(Base):
    __tablename__ = "user_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(BigInteger, nullable=True)       # foreign key optional
    receiver_id = Column(BigInteger, nullable=True)     # foreign key optional
    replyTo = Column(Integer, nullable=True)            # None if not a reply
    message = Column(Text, nullable=True)
    is_personal_message_detected = Column(Boolean, default=False)
    isSeen = Column(Boolean, default=False)
    isAttached = Column(Boolean, default=False)
    price = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)

# ─────────────────────────────────────────────
# ATTACHMENTS TABLE (for image/video)
# ─────────────────────────────────────────────
class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String(36), primary_key=True)
    filename = Column(Text, nullable=False)
    is_personal_message_detected = Column(TINYINT(1), nullable=False, default=0)
    user_id = Column(BigInteger, nullable=True, index=True)
    post_id = Column(BigInteger, nullable=True, index=True)
    story_id = Column(BigInteger, nullable=True, index=True)
    message_id = Column(BigInteger, nullable=True, index=True)
    collab_id = Column(BigInteger, nullable=True, index=True)
    has_thumbnail = Column(TINYINT(1), nullable=True)
    has_blurred_preview = Column(TINYINT(1), nullable=True)
    created_at = Column(TIMESTAMP, nullable=True)
    updated_at = Column(TIMESTAMP, nullable=True)