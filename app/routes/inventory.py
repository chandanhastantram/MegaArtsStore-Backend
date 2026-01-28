"""
Inventory Routes
Stock management and inventory tracking endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel

from app.services.inventory_service import InventoryService
from app.services.export_service import ExportService
from app.database import db
from app.middleware.rbac import get_admin_user, get_admin_or_subadmin
import io

router = APIRouter()


class StockUpdate(BaseModel):
    """Schema for stock update"""
    quantity_change: int
    reason: Optional[str] = "manual"


class BulkStockUpdate(BaseModel):
    """Schema for bulk stock update"""
    product_id: str
    new_stock: int


@router.get("/report")
async def get_inventory_report(
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Get inventory report with statistics.
    
    - Admin and SubAdmin only
    - Returns stock levels, values, and alerts
    """
    report = await InventoryService.get_inventory_report()
    return report


@router.get("/low-stock")
async def get_low_stock_products(
    threshold: int = Query(10, ge=1),
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Get products with low stock.
    
    - Admin and SubAdmin only
    - Configurable threshold
    """
    products = await InventoryService.get_low_stock_products(threshold)
    return {
        "count": len(products),
        "threshold": threshold,
        "products": products
    }


@router.get("/out-of-stock")
async def get_out_of_stock_products(
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Get out of stock products.
    
    - Admin and SubAdmin only
    """
    products = await InventoryService.get_out_of_stock_products()
    return {
        "count": len(products),
        "products": products
    }


@router.put("/products/{product_id}/stock")
async def update_product_stock(
    product_id: str,
    stock_update: StockUpdate,
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Update stock for a product.
    
    - Admin and SubAdmin only
    - Logs all stock changes
    """
    if not ObjectId.is_valid(product_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid product ID"
        )
    
    try:
        new_stock = await InventoryService.update_stock(
            product_id=product_id,
            quantity_change=stock_update.quantity_change,
            reason=stock_update.reason
        )
        
        return {
            "message": "Stock updated successfully",
            "new_stock": new_stock
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/bulk-update")
async def bulk_update_stock(
    updates: List[BulkStockUpdate],
    current_user: dict = Depends(get_admin_user)
):
    """
    Bulk update stock for multiple products.
    
    - Admin only
    """
    results = []
    errors = []
    
    for update in updates:
        try:
            product = await db.products.find_one({"_id": ObjectId(update.product_id)})
            if not product:
                errors.append({
                    "product_id": update.product_id,
                    "error": "Product not found"
                })
                continue
            
            current_stock = product.get("stock", 0)
            quantity_change = update.new_stock - current_stock
            
            new_stock = await InventoryService.update_stock(
                product_id=update.product_id,
                quantity_change=quantity_change,
                reason="bulk_update"
            )
            
            results.append({
                "product_id": update.product_id,
                "previous_stock": current_stock,
                "new_stock": new_stock
            })
        except Exception as e:
            errors.append({
                "product_id": update.product_id,
                "error": str(e)
            })
    
    return {
        "successful": len(results),
        "failed": len(errors),
        "results": results,
        "errors": errors
    }


@router.get("/logs")
async def get_inventory_logs(
    product_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Get inventory change logs.
    
    - Admin and SubAdmin only
    - Optionally filter by product
    """
    logs = await InventoryService.get_inventory_logs(product_id, limit)
    return {
        "count": len(logs),
        "logs": logs
    }


@router.get("/export/csv")
async def export_inventory_csv(
    current_user: dict = Depends(get_admin_user)
):
    """
    Export inventory report as CSV.
    
    - Admin only
    - Returns downloadable CSV file
    """
    csv_data = await ExportService.export_inventory_csv()
    
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=inventory_report_{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )
