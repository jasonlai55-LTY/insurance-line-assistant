from app.core.database import Base  # noqa
# Import all models here for Alembic metadata discovery
from app.db.models import (  # noqa
    Agent,
    OTPRecord,
    Category,
    ProductAsset,
    Tag,
    AgentTag,
    Notification,
    NotificationLog,
    AdminUser
)
