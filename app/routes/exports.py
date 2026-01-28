"""
Export Routes
Data export endpoints for orders, products, and analytics
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime
import io

from app.services.export_service import ExportService
from app.middleware.rbac import get_admin_user, get_admin_or_subadmin

router = APIRouter()


@router.get("/orders/csv")
async def export_orders(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Export orders to CSV.
    
    - Admin and SubAdmin only
    - Optionally filter by date range and status
    """
    csv_data = await ExportService.export_orders_csv(
        start_date=start_date,
        end_date=end_date,
        status=status_filter
    )
    
    filename = f"orders_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/products/csv")
async def export_products(
    current_user: dict = Depends(get_admin_or_subadmin)
):
    """
    Export product catalog to CSV.
    
    - Admin and SubAdmin only
    """
    csv_data = await ExportService.export_products_csv()
    
    filename = f"products_catalog_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/analytics/csv")
async def export_analytics(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: dict = Depends(get_admin_user)
):
    """
    Export analytics report to CSV.
    
    - Admin only
    - Optionally filter by date range
    """
    csv_data = await ExportService.export_analytics_csv(
        start_date=start_date,
        end_date=end_date
    )
    
    filename = f"analytics_report_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/customers/csv")
async def export_customers(
    current_user: dict = Depends(get_admin_user)
):
    """
    Export customers list to CSV.
    
    - Admin only
    """
    csv_data = await ExportService.export_customers_csv()
    
    filename = f"customers_{datetime.now().strftime('%Y%m%d')}.csv"
    
    return StreamingResponse(
        io.StringIO(csv_data),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
