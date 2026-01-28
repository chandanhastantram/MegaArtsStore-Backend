"""
Inventory Service
Stock tracking, low stock alerts, and automatic updates
"""

from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId

from app.database import db
from app.services.email_service import send_email


class InventoryService:
    """Service for inventory management"""

    LOW_STOCK_THRESHOLD = 10  # Alert when stock falls below this

    @staticmethod
    async def update_stock(product_id: str, quantity_change: int, reason: str = "manual"):
        """
        Update product stock.
        
        Args:
            product_id: Product ID
            quantity_change: Positive to add, negative to reduce
            reason: Reason for stock change (order, restock, manual, etc.)
        """
        product = await db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            raise ValueError("Product not found")
        
        current_stock = product.get("stock", 0)
        new_stock = current_stock + quantity_change
        
        if new_stock < 0:
            raise ValueError("Insufficient stock")
        
        # Update stock
        await db.products.update_one(
            {"_id": ObjectId(product_id)},
            {
                "$set": {
                    "stock": new_stock,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Log inventory change
        await db.inventory_logs.insert_one({
            "product_id": product_id,
            "product_name": product.get("name"),
            "previous_stock": current_stock,
            "quantity_change": quantity_change,
            "new_stock": new_stock,
            "reason": reason,
            "timestamp": datetime.utcnow()
        })
        
        # Check for low stock
        if new_stock <= InventoryService.LOW_STOCK_THRESHOLD and new_stock > 0:
            await InventoryService.send_low_stock_alert(product_id, product.get("name"), new_stock)
        
        # Check for out of stock
        if new_stock == 0:
            await InventoryService.send_out_of_stock_alert(product_id, product.get("name"))
        
        return new_stock

    @staticmethod
    async def reduce_stock_for_order(order_items: List[Dict[str, Any]]):
        """
        Reduce stock for multiple products in an order.
        
        Args:
            order_items: List of items with product_id and quantity
        """
        for item in order_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            try:
                await InventoryService.update_stock(
                    product_id=product_id,
                    quantity_change=-quantity,
                    reason="order"
                )
            except ValueError as e:
                # Rollback previous stock reductions if any item fails
                raise ValueError(f"Failed to reduce stock for product {product_id}: {str(e)}")

    @staticmethod
    async def restore_stock_for_order(order_items: List[Dict[str, Any]]):
        """
        Restore stock when order is cancelled.
        
        Args:
            order_items: List of items with product_id and quantity
        """
        for item in order_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 1)
            
            await InventoryService.update_stock(
                product_id=product_id,
                quantity_change=quantity,
                reason="order_cancelled"
            )

    @staticmethod
    async def get_low_stock_products(threshold: int = None):
        """Get all products with low stock"""
        if threshold is None:
            threshold = InventoryService.LOW_STOCK_THRESHOLD
        
        products = await db.products.find({
            "stock": {"$lte": threshold, "$gt": 0}
        }).to_list(length=100)
        
        return products

    @staticmethod
    async def get_out_of_stock_products():
        """Get all out of stock products"""
        products = await db.products.find({
            "stock": 0
        }).to_list(length=100)
        
        return products

    @staticmethod
    async def get_inventory_report():
        """Generate inventory report"""
        total_products = await db.products.count_documents({})
        in_stock = await db.products.count_documents({"stock": {"$gt": 0}})
        out_of_stock = await db.products.count_documents({"stock": 0})
        low_stock = await db.products.count_documents({
            "stock": {"$lte": InventoryService.LOW_STOCK_THRESHOLD, "$gt": 0}
        })
        
        # Get total inventory value
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_value": {
                        "$sum": {"$multiply": ["$price", "$stock"]}
                    },
                    "total_items": {"$sum": "$stock"}
                }
            }
        ]
        
        value_result = await db.products.aggregate(pipeline).to_list(length=1)
        total_value = value_result[0]["total_value"] if value_result else 0
        total_items = value_result[0]["total_items"] if value_result else 0
        
        return {
            "total_products": total_products,
            "in_stock": in_stock,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
            "total_inventory_value": round(total_value, 2),
            "total_items_in_stock": total_items,
            "timestamp": datetime.utcnow().isoformat()
        }

    @staticmethod
    async def get_inventory_logs(product_id: str = None, limit: int = 50):
        """Get inventory change logs"""
        query = {}
        if product_id:
            query["product_id"] = product_id
        
        logs = await db.inventory_logs.find(query).sort("timestamp", -1).limit(limit).to_list(length=limit)
        return logs

    @staticmethod
    async def send_low_stock_alert(product_id: str, product_name: str, stock: int):
        """Send low stock alert to admin"""
        # Get admin emails
        admins = await db.users.find({"role": "admin"}).to_list(length=10)
        admin_emails = [admin.get("email") for admin in admins if admin.get("email")]
        
        if not admin_emails:
            return
        
        subject = f"Low Stock Alert: {product_name}"
        body = f"""
        <h2>Low Stock Alert</h2>
        <p>The following product is running low on stock:</p>
        <ul>
            <li><strong>Product:</strong> {product_name}</li>
            <li><strong>Current Stock:</strong> {stock} units</li>
            <li><strong>Threshold:</strong> {InventoryService.LOW_STOCK_THRESHOLD} units</li>
        </ul>
        <p>Please restock this product soon.</p>
        """
        
        for email in admin_emails:
            try:
                await send_email(email, subject, body)
            except Exception as e:
                print(f"Failed to send low stock alert to {email}: {e}")

    @staticmethod
    async def send_out_of_stock_alert(product_id: str, product_name: str):
        """Send out of stock alert to admin"""
        # Get admin emails
        admins = await db.users.find({"role": "admin"}).to_list(length=10)
        admin_emails = [admin.get("email") for admin in admins if admin.get("email")]
        
        if not admin_emails:
            return
        
        subject = f"Out of Stock: {product_name}"
        body = f"""
        <h2>Out of Stock Alert</h2>
        <p>The following product is now out of stock:</p>
        <ul>
            <li><strong>Product:</strong> {product_name}</li>
            <li><strong>Current Stock:</strong> 0 units</li>
        </ul>
        <p><strong>Action Required:</strong> Please restock this product immediately.</p>
        """
        
        for email in admin_emails:
            try:
                await send_email(email, subject, body)
            except Exception as e:
                print(f"Failed to send out of stock alert to {email}: {e}")
