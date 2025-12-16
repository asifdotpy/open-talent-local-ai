from enum import Enum
from typing import Optional, Dict, Any

from pydantic import BaseModel, EmailStr, Field, constr


class NotificationPriority(str, Enum):
    """Priority levels for notifications"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class EmailNotificationRequest(BaseModel):
    to: EmailStr
    subject: constr(strip_whitespace=True, min_length=1)
    html: Optional[str] = ""
    text: Optional[str] = None
    priority: Optional[NotificationPriority] = Field(default=NotificationPriority.NORMAL)


class SMSNotificationRequest(BaseModel):
    # E.164 phone format: optional +, up to 15 digits
    to: constr(strip_whitespace=True, pattern=r'^\+?[1-9]\d{1,14}$')
    text: constr(strip_whitespace=True, min_length=1)
    priority: Optional[NotificationPriority] = Field(default=NotificationPriority.NORMAL)


class PushNotificationRequest(BaseModel):
    to: constr(strip_whitespace=True, min_length=1)
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
    data: Optional[Dict[str, Any]] = None
    priority: Optional[NotificationPriority] = Field(default=NotificationPriority.NORMAL)
