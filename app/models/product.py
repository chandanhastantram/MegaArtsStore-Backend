"""
Product Model for MongoDB
Supports AR-enabled jewellery products with 3D models
"""

from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from bson import ObjectId


# Material types for jewellery
MaterialType = Literal["gold", "silver", "kundan", "diamond", "platinum"]


class ARConfigModel(BaseModel):
    """AR Configuration for wrist alignment"""
    scale: float = 1.0
    rotation: List[float] = [0, 0, 0]  # X, Y, Z rotation in degrees
    offset: List[float] = [0, 0, 0]    # X, Y, Z offset
    wrist_diameter: float = 0.0         # Detected wrist diameter for fit


class ProductDocument:
    """
    Product document structure for MongoDB.
    
    Attributes:
        _id: MongoDB ObjectId
        name: Product name
        description: Product description
        price: Base price in INR
        category: Category ID reference
        material: Material type (gold, silver, kundan, etc.)
        sizes: Available size variants
        images: List of image URLs
        model_3d: URL to 3D model file (GLB)
        model_original: URL to original 3D model (for recovery)
        ar_enabled: Whether AR try-on is available
        ar_config: AR alignment configuration
        visibility: Whether product is visible to users
        featured: Whether product is featured on homepage
        stock: Available stock quantity
        created_by: User ID who created the product
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """
    
    @staticmethod
    def create_document(
        name: str,
        description: str,
        price: float,
        category: str,
        material: MaterialType,
        created_by: str,
        sizes: List[str] = None,
        images: List[str] = None,
        stock: int = 0
    ) -> dict:
        """Create a new product document"""
        now = datetime.utcnow()
        return {
            "name": name,
            "description": description,
            "price": price,
            "category": category,
            "material": material,
            "sizes": sizes or ["S", "M", "L"],
            "images": images or [],
            "model_3d": None,
            "model_original": None,
            "ar_enabled": False,
            "ar_config": {
                "scale": 1.0,
                "rotation": [0, 0, 0],
                "offset": [0, 0, 0],
                "wrist_diameter": 0.0
            },
            "visibility": True,
            "featured": False,
            "stock": stock,
            "reviews": [],
            "avg_rating": 0.0,
            "created_by": created_by,
            "created_at": now,
            "updated_at": now
        }


class ReviewModel(BaseModel):
    """Product review embedded document"""
    user_id: str
    user_name: str
    rating: int = Field(ge=1, le=5)
    comment: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ProductInDB(BaseModel):
    """Product model as stored in database"""
    id: Optional[str] = Field(default=None, alias="_id")
    name: str
    description: str
    price: float
    category: str
    material: MaterialType
    sizes: List[str] = ["S", "M", "L"]
    images: List[str] = []
    model_3d: Optional[str] = None
    model_original: Optional[str] = None
    ar_enabled: bool = False
    ar_config: ARConfigModel = ARConfigModel()
    visibility: bool = True
    featured: bool = False
    stock: int = 0
    reviews: List[ReviewModel] = []
    avg_rating: float = 0.0
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
