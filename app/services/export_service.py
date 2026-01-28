"""
Export Service
Generate CSV/Excel exports for orders, products, and analytics
"""

import csv
import io
from datetime import datetime
from typing import List, Dict, Any
from bson import ObjectId

from app.database import db


class ExportService:
    """Service for data export operations"""

    @staticmethod
    async def export_orders_csv(
        start_date: datetime = None,
        end_date: datetime = None,
        status: str = None
    ) -> str:
        """
        Export orders to CSV format.
        
        Returns CSV string
        """
        # Build query
        query = {}
        if start_date or end_date:
            query["created_at"] = {}
            if start_date:
                query["created_at"]["$gte"] = start_date
            if end_date:
                query["created_at"]["$lte"] = end_date
        if status:
            query["status"] = status
        
        # Fetch orders
        orders = await db.orders.find(query).sort("created_at", -1).to_list(length=10000)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Order ID",
            "Order Number",
            "Customer Name",
            "Customer Email",
            "Status",
            "Total Amount",
            "Discount",
            "Final Amount",
            "Payment Method",
            "Payment Status",
            "Items Count",
            "Created At",
            "Updated At"
        ])
        
        # Write data
        for order in orders:
            # Get user details
            user = await db.users.find_one({"_id": ObjectId(order.get("user_id"))})
            
            writer.writerow([
                str(order["_id"]),
                order.get("order_number", ""),
                user.get("full_name", "") if user else "",
                user.get("email", "") if user else "",
                order.get("status", ""),
                order.get("total_amount", 0),
                order.get("discount_amount", 0),
                order.get("final_amount", 0),
                order.get("payment_method", ""),
                order.get("payment_status", ""),
                len(order.get("items", [])),
                order.get("created_at", "").isoformat() if order.get("created_at") else "",
                order.get("updated_at", "").isoformat() if order.get("updated_at") else ""
            ])
        
        return output.getvalue()

    @staticmethod
    async def export_products_csv() -> str:
        """
        Export products catalog to CSV format.
        
        Returns CSV string
        """
        # Fetch all products
        products = await db.products.find({}).to_list(length=10000)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Product ID",
            "Name",
            "Description",
            "Price",
            "Material",
            "Category",
            "Stock",
            "AR Enabled",
            "Featured",
            "Visible",
            "Average Rating",
            "Reviews Count",
            "Created At"
        ])
        
        # Write data
        for product in products:
            # Get category name
            category = await db.categories.find_one({"_id": ObjectId(product.get("category"))}) if product.get("category") else None
            
            writer.writerow([
                str(product["_id"]),
                product.get("name", ""),
                product.get("description", "")[:100],  # Truncate long descriptions
                product.get("price", 0),
                product.get("material", ""),
                category.get("name", "") if category else "",
                product.get("stock", 0),
                "Yes" if product.get("ar_enabled") else "No",
                "Yes" if product.get("featured") else "No",
                "Yes" if product.get("visibility") else "No",
                product.get("avg_rating", 0),
                len(product.get("reviews", [])),
                product.get("created_at", "").isoformat() if product.get("created_at") else ""
            ])
        
        return output.getvalue()

    @staticmethod
    async def export_analytics_csv(
        start_date: datetime = None,
        end_date: datetime = None
    ) -> str:
        """
        Export analytics report to CSV format.
        
        Returns CSV string
        """
        # Build date query
        date_query = {}
        if start_date or end_date:
            date_query["created_at"] = {}
            if start_date:
                date_query["created_at"]["$gte"] = start_date
            if end_date:
                date_query["created_at"]["$lte"] = end_date
        
        # Get orders analytics
        orders = await db.orders.find(date_query).to_list(length=10000)
        
        # Calculate metrics
        total_orders = len(orders)
        total_revenue = sum(order.get("final_amount", 0) for order in orders)
        total_discount = sum(order.get("discount_amount", 0) for order in orders)
        
        # Status breakdown
        status_counts = {}
        for order in orders:
            status = order.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Payment method breakdown
        payment_methods = {}
        for order in orders:
            method = order.get("payment_method", "unknown")
            payment_methods[method] = payment_methods.get(method, 0) + 1
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Summary section
        writer.writerow(["Analytics Report"])
        writer.writerow(["Generated At", datetime.utcnow().isoformat()])
        if start_date:
            writer.writerow(["Start Date", start_date.isoformat()])
        if end_date:
            writer.writerow(["End Date", end_date.isoformat()])
        writer.writerow([])
        
        # Overall metrics
        writer.writerow(["Overall Metrics"])
        writer.writerow(["Total Orders", total_orders])
        writer.writerow(["Total Revenue", f"₹{total_revenue:.2f}"])
        writer.writerow(["Total Discounts", f"₹{total_discount:.2f}"])
        writer.writerow(["Average Order Value", f"₹{(total_revenue/total_orders if total_orders > 0 else 0):.2f}"])
        writer.writerow([])
        
        # Status breakdown
        writer.writerow(["Order Status Breakdown"])
        writer.writerow(["Status", "Count"])
        for status, count in status_counts.items():
            writer.writerow([status, count])
        writer.writerow([])
        
        # Payment methods
        writer.writerow(["Payment Methods"])
        writer.writerow(["Method", "Count"])
        for method, count in payment_methods.items():
            writer.writerow([method, count])
        
        return output.getvalue()

    @staticmethod
    async def export_inventory_csv() -> str:
        """
        Export inventory report to CSV format.
        
        Returns CSV string
        """
        # Fetch all products
        products = await db.products.find({}).sort("stock", 1).to_list(length=10000)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Product ID",
            "Product Name",
            "Material",
            "Price",
            "Stock Quantity",
            "Stock Value",
            "Status",
            "Last Updated"
        ])
        
        # Write data
        for product in products:
            stock = product.get("stock", 0)
            price = product.get("price", 0)
            stock_value = stock * price
            
            # Determine status
            if stock == 0:
                status = "Out of Stock"
            elif stock <= 10:
                status = "Low Stock"
            else:
                status = "In Stock"
            
            writer.writerow([
                str(product["_id"]),
                product.get("name", ""),
                product.get("material", ""),
                f"₹{price:.2f}",
                stock,
                f"₹{stock_value:.2f}",
                status,
                product.get("updated_at", "").isoformat() if product.get("updated_at") else ""
            ])
        
        return output.getvalue()

    @staticmethod
    async def export_customers_csv() -> str:
        """
        Export customers list to CSV format.
        
        Returns CSV string
        """
        # Fetch all users (excluding admins)
        users = await db.users.find({"role": {"$ne": "admin"}}).to_list(length=10000)
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "User ID",
            "Full Name",
            "Email",
            "Phone",
            "Role",
            "Active",
            "Total Orders",
            "Registered At"
        ])
        
        # Write data
        for user in users:
            user_id = str(user["_id"])
            
            # Get order count
            order_count = await db.orders.count_documents({"user_id": user_id})
            
            writer.writerow([
                user_id,
                user.get("full_name", ""),
                user.get("email", ""),
                user.get("phone", ""),
                user.get("role", "user"),
                "Yes" if user.get("is_active") else "No",
                order_count,
                user.get("created_at", "").isoformat() if user.get("created_at") else ""
            ])
        
        return output.getvalue()
