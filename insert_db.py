# from datetime import datetime
# from api.database import get_db
# from api.models.model import UserMessage

# db_gen = get_db()
# db = next(db_gen)

# # Sample data to insert
# data = {
#     "sender_id": 12,
#     "receiver_id": 24,
#     "replyTo": None,
#     "text": "Test message",
#     "filename": None
# }

# new_msg = UserMessage(
#     sender_id = data.get("sender_id") or 0,
#     receiver_id = data.get("receiver_id") or 0,
#     replyTo = data.get("replyTo") or 0,  # default 0 if missing
#     message = data.get("text", ""),
#     personal_message_detected = False,
#     isSeen = False,
#     isAttached = bool(data.get("filename")),
#     price = 0,
#     created_at = datetime.now(),
#     updated_at = datetime.now()
# )

# db.add(new_msg)
# db.commit()
# db.refresh(new_msg)
# print(f"✅ Inserted message ID: {new_msg.id}")

# db.close()


from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from api.database import get_db
from api.models.model import UserMessage, Attachment

def save_message_to_db(data: dict, is_personal: bool = False):
    """
    Save a message dictionary to the user_messages table.
    This version uses the working insert logic.
    """
    db_gen = get_db()
    db = next(db_gen)

    try:
        new_msg = UserMessage(
            sender_id = data.get("sender_id") or 0,
            receiver_id = data.get("receiver_id") or 0,
            replyTo = data.get("replyTo") or 0,
            message = data.get("text", ""),
            is_personal_message_detected = is_personal,
            isSeen = False,
            isAttached = bool(data.get("filename")),
            price = 0,
            created_at = datetime.now(),
            updated_at = datetime.now()
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)
        print(f"✅ Saved to DB: ID {new_msg.id}")
        return new_msg.id
    except Exception as e:
        db.rollback()
        print("❌ DB Save Error:", repr(e))
        return None
    finally:
        db.close()

# ─────────────────────────────────────────────
# INSERT ATTACHMENT (IMAGE/VIDEO)
# ─────────────────────────────────────────────
def save_attachment_to_db(data: dict, is_personal: bool):
    db_gen = get_db()
    db = next(db_gen)
    try:
        new_attachment = Attachment(
            id=str(uuid.uuid4()),
            filename=data.get("filename"),
            is_personal_message_detected=int(is_personal),
            user_id=data.get("user_id"),
            post_id=data.get("post_id"),
            story_id=data.get("story_id"),
            message_id=data.get("message_id"),
            collab_id=data.get("collab_id"),
            has_thumbnail=0,
            has_blurred_preview=0,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.add(new_attachment)
        db.commit()
        db.refresh(new_attachment)
        print(f"✅ Stored attachment ID: {new_attachment.id}")
    except Exception as e:
        print("❌ Error saving attachment:", repr(e))
        db.rollback()
    finally:
        db.close()