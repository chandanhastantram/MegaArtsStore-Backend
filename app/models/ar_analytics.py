"""
AR Analytics Model for MongoDB
Tracks AR try-on events and user behavior
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
import uuid


class ARTryOnEvent:
    """
    AR Try-On event document structure.
    
    Tracks when users try on products using AR feature.
    """
    
    @staticmethod
    def create_document(
        product_id: str,
        user_id: str = None,
        session_id: str = None,
        device_type: str = "unknown",
        duration_seconds: int = 0,
        screenshot_taken: bool = False,
        added_to_cart: bool = False,
        purchased: bool = False
    ) -> dict:
        """Create a new AR try-on event document"""
        return {
            "event_id": str(uuid.uuid4()),
            "product_id": product_id,
            "user_id": user_id,
            "session_id": session_id or str(uuid.uuid4()),
            "device_type": device_type,  # mobile, tablet, desktop
            "duration_seconds": duration_seconds,
            "screenshot_taken": screenshot_taken,
            "added_to_cart": added_to_cart,
            "purchased": purchased,
            "created_at": datetime.utcnow()
        }


class WristMeasurement:
    """
    Wrist measurement document for size recommendation.
    
    Stores user's wrist measurements from AR scan.
    """
    
    @staticmethod
    def create_document(
        user_id: str,
        wrist_circumference: float,  # in cm
        wrist_width: float,          # in cm
        measurement_method: str = "ar_scan",
        confidence_score: float = 0.0
    ) -> dict:
        """Create a new wrist measurement document"""
        return {
            "measurement_id": str(uuid.uuid4()),
            "user_id": user_id,
            "wrist_circumference": wrist_circumference,
            "wrist_width": wrist_width,
            "measurement_method": measurement_method,
            "confidence_score": confidence_score,
            "created_at": datetime.utcnow()
        }


# ============ Pydantic Models ============

class ARTryOnEventDB(BaseModel):
    """AR Try-On event as stored in database"""
    id: Optional[str] = Field(default=None, alias="_id")
    event_id: str
    product_id: str
    user_id: Optional[str] = None
    session_id: str
    device_type: str = "unknown"
    duration_seconds: int = 0
    screenshot_taken: bool = False
    added_to_cart: bool = False
    purchased: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class WristMeasurementDB(BaseModel):
    """Wrist measurement as stored in database"""
    id: Optional[str] = Field(default=None, alias="_id")
    measurement_id: str
    user_id: str
    wrist_circumference: float
    wrist_width: float
    measurement_method: str = "ar_scan"
    confidence_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
