"""
Bulk Operations Routes
CSV/Excel import and export for products and inventory
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.responses import StreamingResponse
from typing import List
import csv
import io
from datetime import datetime
from bson import ObjectId

from app.database import get_products_collection, get_categories_collection
from app.middleware.rbac import get_admin_user
from app.models.product import ProductDocument

router = APIRouter()


@router.post("/products/import")
async def import_products_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_admin_user)
):
    """
    Bulk import products from CSV.
    
    - Admin only
    - CSV format: name,description,price,category,material,sizes,stock
    - Sizes should be pipe-separated (e.g., "2-4|2-6|2-8")
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    products_collection = get_products_collection()
    
    # Read CSV
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    imported = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (header is 1)
        try:
            # Parse sizes
            sizes = row.get('sizes', '').split('|') if row.get('sizes') else []
            
            # Create product document
            product_doc = ProductDocument.create_document(
                name=row['name'],
                description=row.get('description', ''),
                price=float(row['price']),
                category=row['category'],
                material=row.get('material', ''),
                created_by=current_user["_id"],
                sizes=sizes,
                images=[],
                stock=int(row.get('stock', 0))
            )
            
            # Insert
            await products_collection.insert_one(product_doc)
            imported += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "imported": imported,
        "errors": errors,
        "total_rows": imported + len(errors)
    }


@router.get("/products/export")
async def export_products_csv(
    current_user: dict = Depends(get_admin_user)
):
    """
    Export all products to CSV.
    
    - Admin only
    """
    products_collection = get_products_collection()
    
    # Get all products
    products = await products_collection.find().to_list(10000)
    
    # Create CSV
    output = io.StringIO()
    fieldnames = ['id', 'name', 'description', 'price', 'category', 'material', 'sizes', 'stock', 'visibility', 'ar_enabled']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for p in products:
        writer.writerow({
            'id': str(p['_id']),
            'name': p['name'],
            'description': p.get('description', ''),
            'price': p['price'],
            'category': p['category'],
            'material': p.get('material', ''),
            'sizes': '|'.join(p.get('sizes', [])),
            'stock': p.get('stock', 0),
            'visibility': p.get('visibility', True),
            'ar_enabled': p.get('ar_enabled', False)
        })
    
    # Return as downloadable file
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=products_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
    )


@router.post("/inventory/bulk-update")
async def bulk_update_inventory(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_admin_user)
):
    """
    Bulk update inventory from CSV.
    
    - Admin only
    - CSV format: product_id,stock
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    products_collection = get_products_collection()
    
    # Read CSV
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    updated = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            product_id = row['product_id']
            new_stock = int(row['stock'])
            
            # Update stock
            result = await products_collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": {"stock": new_stock, "updated_at": datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                updated += 1
            else:
                errors.append(f"Row {row_num}: Product {product_id} not found")
                
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "updated": updated,
        "errors": errors,
        "total_rows": updated + len(errors)
    }


@router.get("/inventory/export")
async def export_inventory_csv(
    current_user: dict = Depends(get_admin_user)
):
    """
    Export inventory levels to CSV.
    
    - Admin only
    """
    products_collection = get_products_collection()
    
    # Get all products
    products = await products_collection.find(
        {},
        {"_id": 1, "name": 1, "category": 1, "stock": 1}
    ).to_list(10000)
    
    # Create CSV
    output = io.StringIO()
    fieldnames = ['product_id', 'name', 'category', 'stock']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for p in products:
        writer.writerow({
            'product_id': str(p['_id']),
            'name': p['name'],
            'category': p['category'],
            'stock': p.get('stock', 0)
        })
    
    # Return as downloadable file
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=inventory_{datetime.utcnow().strftime('%Y%m%d')}.csv"}
    )


@router.post("/categories/import")
async def import_categories_csv(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_admin_user)
):
    """
    Bulk import categories from CSV.
    
    - Admin only
    - CSV format: name,description
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV"
        )
    
    categories_collection = get_categories_collection()
    
    # Read CSV
    contents = await file.read()
    csv_data = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_data))
    
    imported = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):
        try:
            # Check if category already exists
            existing = await categories_collection.find_one({"name": row['name']})
            if existing:
                errors.append(f"Row {row_num}: Category '{row['name']}' already exists")
                continue
            
            # Create category
            await categories_collection.insert_one({
                "name": row['name'],
                "description": row.get('description', ''),
                "created_at": datetime.utcnow()
            })
            imported += 1
            
        except Exception as e:
            errors.append(f"Row {row_num}: {str(e)}")
    
    return {
        "imported": imported,
        "errors": errors,
        "total_rows": imported + len(errors)
    }
