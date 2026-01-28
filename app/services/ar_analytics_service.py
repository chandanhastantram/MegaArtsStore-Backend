"""
AR Analytics Service
Business logic for AR try-on tracking and size recommendations
"""

from typing import List, Optional, Dict
from bson import ObjectId
from datetime import datetime, timedelta

from app.database import get_database


def get_ar_events_collection():
    """Get AR events collection"""
    return get_database()["ar_events"]


def get_wrist_measurements_collection():
    """Get wrist measurements collection"""
    return get_database()["wrist_measurements"]


# ============ Try-On Analytics ============

async def log_try_on_event(
    product_id: str,
    user_id: str = None,
    session_id: str = None,
    device_type: str = "unknown",
    duration_seconds: int = 0,
    screenshot_taken: bool = False
) -> Dict:
    """
    Log an AR try-on event.
    
    Args:
        product_id: Product being tried on
        user_id: Logged-in user ID (optional)
        session_id: Session ID for anonymous users
        device_type: Device type (mobile, tablet, desktop)
        duration_seconds: How long user tried on the item
        screenshot_taken: Whether user took a screenshot
    
    Returns:
        Created event document
    """
    from app.models.ar_analytics import ARTryOnEvent
    
    collection = get_ar_events_collection()
    
    event_doc = ARTryOnEvent.create_document(
        product_id=product_id,
        user_id=user_id,
        session_id=session_id,
        device_type=device_type,
        duration_seconds=duration_seconds,
        screenshot_taken=screenshot_taken
    )
    
    result = await collection.insert_one(event_doc)
    event_doc["_id"] = str(result.inserted_id)
    
    return event_doc


async def update_try_on_conversion(
    event_id: str,
    added_to_cart: bool = False,
    purchased: bool = False
) -> bool:
    """Update try-on event with conversion data"""
    collection = get_ar_events_collection()
    
    update_doc = {}
    if added_to_cart:
        update_doc["added_to_cart"] = True
    if purchased:
        update_doc["purchased"] = True
    
    if update_doc:
        result = await collection.update_one(
            {"event_id": event_id},
            {"$set": update_doc}
        )
        return result.modified_count > 0
    
    return False


async def get_product_ar_stats(product_id: str) -> Dict:
    """
    Get AR analytics for a specific product.
    
    Returns:
        Dictionary with try-on stats
    """
    collection = get_ar_events_collection()
    
    pipeline = [
        {"$match": {"product_id": product_id}},
        {"$group": {
            "_id": None,
            "total_try_ons": {"$sum": 1},
            "unique_users": {"$addToSet": {"$ifNull": ["$user_id", "$session_id"]}},
            "avg_duration": {"$avg": "$duration_seconds"},
            "screenshots": {"$sum": {"$cond": ["$screenshot_taken", 1, 0]}},
            "added_to_cart": {"$sum": {"$cond": ["$added_to_cart", 1, 0]}},
            "purchased": {"$sum": {"$cond": ["$purchased", 1, 0]}}
        }}
    ]
    
    result = await collection.aggregate(pipeline).to_list(1)
    
    if not result:
        return {
            "total_try_ons": 0,
            "unique_users": 0,
            "avg_duration_seconds": 0,
            "screenshot_rate": 0,
            "cart_conversion_rate": 0,
            "purchase_conversion_rate": 0
        }
    
    data = result[0]
    total = data["total_try_ons"]
    
    return {
        "total_try_ons": total,
        "unique_users": len(data["unique_users"]),
        "avg_duration_seconds": round(data["avg_duration"] or 0, 1),
        "screenshot_rate": round((data["screenshots"] / total) * 100, 1) if total > 0 else 0,
        "cart_conversion_rate": round((data["added_to_cart"] / total) * 100, 1) if total > 0 else 0,
        "purchase_conversion_rate": round((data["purchased"] / total) * 100, 1) if total > 0 else 0
    }


async def get_top_tried_products(limit: int = 10, days: int = 30) -> List[Dict]:
    """Get most tried-on products in the last N days"""
    collection = get_ar_events_collection()
    
    since = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": "$product_id",
            "try_on_count": {"$sum": 1},
            "cart_conversions": {"$sum": {"$cond": ["$added_to_cart", 1, 0]}}
        }},
        {"$sort": {"try_on_count": -1}},
        {"$limit": limit}
    ]
    
    results = await collection.aggregate(pipeline).to_list(limit)
    
    return [
        {
            "product_id": r["_id"],
            "try_on_count": r["try_on_count"],
            "cart_conversions": r["cart_conversions"]
        }
        for r in results
    ]


async def get_ar_dashboard_stats(days: int = 30) -> Dict:
    """Get overall AR analytics dashboard stats"""
    collection = get_ar_events_collection()
    
    since = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": None,
            "total_try_ons": {"$sum": 1},
            "screenshots": {"$sum": {"$cond": ["$screenshot_taken", 1, 0]}},
            "cart_conversions": {"$sum": {"$cond": ["$added_to_cart", 1, 0]}},
            "purchases": {"$sum": {"$cond": ["$purchased", 1, 0]}},
            "avg_duration": {"$avg": "$duration_seconds"}
        }}
    ]
    
    result = await collection.aggregate(pipeline).to_list(1)
    
    # Device breakdown
    device_pipeline = [
        {"$match": {"created_at": {"$gte": since}}},
        {"$group": {
            "_id": "$device_type",
            "count": {"$sum": 1}
        }}
    ]
    
    device_results = await collection.aggregate(device_pipeline).to_list(10)
    device_breakdown = {r["_id"]: r["count"] for r in device_results}
    
    if not result:
        return {
            "total_try_ons": 0,
            "screenshots": 0,
            "cart_conversions": 0,
            "purchases": 0,
            "avg_duration_seconds": 0,
            "device_breakdown": device_breakdown
        }
    
    data = result[0]
    
    return {
        "total_try_ons": data["total_try_ons"],
        "screenshots": data["screenshots"],
        "cart_conversions": data["cart_conversions"],
        "purchases": data["purchases"],
        "avg_duration_seconds": round(data["avg_duration"] or 0, 1),
        "device_breakdown": device_breakdown
    }


# ============ Size Recommendation ============

async def save_wrist_measurement(
    user_id: str,
    wrist_circumference: float,
    wrist_width: float,
    measurement_method: str = "ar_scan",
    confidence_score: float = 0.0
) -> Dict:
    """
    Save a wrist measurement from AR scan.
    
    Args:
        user_id: User ID
        wrist_circumference: Wrist circumference in cm
        wrist_width: Wrist width in cm
        measurement_method: How measurement was taken
        confidence_score: AI confidence score (0-1)
    
    Returns:
        Created measurement document
    """
    from app.models.ar_analytics import WristMeasurement
    
    collection = get_wrist_measurements_collection()
    
    measurement_doc = WristMeasurement.create_document(
        user_id=user_id,
        wrist_circumference=wrist_circumference,
        wrist_width=wrist_width,
        measurement_method=measurement_method,
        confidence_score=confidence_score
    )
    
    result = await collection.insert_one(measurement_doc)
    measurement_doc["_id"] = str(result.inserted_id)
    
    return measurement_doc


async def get_user_measurements(user_id: str) -> List[Dict]:
    """Get user's wrist measurements history"""
    collection = get_wrist_measurements_collection()
    
    cursor = collection.find({"user_id": user_id}).sort("created_at", -1)
    measurements = await cursor.to_list(10)
    
    for m in measurements:
        m["_id"] = str(m["_id"])
    
    return measurements


async def recommend_bangle_size(
    user_id: str = None,
    wrist_circumference: float = None
) -> Dict:
    """
    Recommend bangle size based on wrist measurement.
    
    Args:
        user_id: User ID to get saved measurements
        wrist_circumference: Direct measurement in cm
    
    Returns:
        Size recommendation with confidence
    """
    # If no direct measurement, get from user's saved measurements
    if wrist_circumference is None and user_id:
        measurements = await get_user_measurements(user_id)
        if measurements:
            # Use most recent high-confidence measurement
            wrist_circumference = measurements[0]["wrist_circumference"]
    
    if wrist_circumference is None:
        return {
            "error": "No wrist measurement available",
            "recommended_size": None
        }
    
    # Bangle sizing chart (inner diameter in cm)
    # Standard Indian bangle sizes
    SIZE_CHART = {
        "2-2": {"min": 4.8, "max": 5.1, "diameter": 5.08},
        "2-4": {"min": 5.1, "max": 5.4, "diameter": 5.4},
        "2-6": {"min": 5.4, "max": 5.7, "diameter": 5.72},
        "2-8": {"min": 5.7, "max": 6.0, "diameter": 6.03},
        "2-10": {"min": 6.0, "max": 6.4, "diameter": 6.35},
        "2-12": {"min": 6.4, "max": 6.7, "diameter": 6.67},
        "2-14": {"min": 6.7, "max": 7.0, "diameter": 6.98}
    }
    
    # Calculate required inner diameter
    # Add 0.5cm for comfort fit
    required_diameter = (wrist_circumference / 3.14159) + 0.5
    
    recommended_size = None
    recommended_diameter = 0
    
    for size, specs in SIZE_CHART.items():
        if specs["min"] <= required_diameter <= specs["max"]:
            recommended_size = size
            recommended_diameter = specs["diameter"]
            break
        elif required_diameter < specs["min"] and recommended_size is None:
            recommended_size = size
            recommended_diameter = specs["diameter"]
    
    # If still no match, recommend largest
    if recommended_size is None:
        recommended_size = "2-14"
        recommended_diameter = 6.98
    
    return {
        "wrist_circumference": wrist_circumference,
        "required_diameter": round(required_diameter, 2),
        "recommended_size": recommended_size,
        "recommended_diameter": recommended_diameter,
        "size_chart": SIZE_CHART,
        "fit_type": "comfort",
        "note": "Sizes are in Indian bangle sizing standard"
    }
