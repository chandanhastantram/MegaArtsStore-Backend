"""
Notifications Service
Push/Email notifications for back-in-stock, flash sales, order updates
"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.database import get_database, get_products_collection, get_users_collection
from app.services import email_service


# ============ Back-in-Stock Notifications ============

async def subscribe_back_in_stock(user_id: str, product_id: str, email: str):
    """
    Subscribe to back-in-stock notifications for a product.
    
    Args:
        user_id: User ID
        product_id: Product ID
        email: User email
    """
    db = get_database()
    subscriptions = db["back_in_stock_subscriptions"]
    
    # Check if already subscribed
    existing = await subscriptions.find_one({
        "user_id": user_id,
        "product_id": product_id
    })
    
    if existing:
        return {"status": "already_subscribed"}
    
    # Create subscription
    await subscriptions.insert_one({
        "user_id": user_id,
        "product_id": product_id,
        "email": email,
        "created_at": datetime.utcnow(),
        "notified": False
    })
    
    return {"status": "subscribed"}


async def notify_back_in_stock(product_id: str, product_name: str):
    """
    Notify all subscribers when a product is back in stock.
    
    Args:
        product_id: Product ID
        product_name: Product name
    """
    db = get_database()
    subscriptions = db["back_in_stock_subscriptions"]
    
    # Get all subscribers who haven't been notified
    subscribers = await subscriptions.find({
        "product_id": product_id,
        "notified": False
    }).to_list(1000)
    
    # Send emails
    for sub in subscribers:
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #B8860B, #DAA520); padding: 20px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; }}
                .button {{ display: inline-block; background: #B8860B; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Back in Stock!</h1>
                </div>
                
                <p>Great news! <strong>{product_name}</strong> is back in stock.</p>
                
                <p style="text-align: center;">
                    <a href="http://localhost:3000/product/{product_id}" class="button">Shop Now</a>
                </p>
                
                <p>Hurry, limited stock available!</p>
                
                <p>Best regards,<br>MegaArtsStore Team</p>
            </div>
        </body>
        </html>
        """
        
        await email_service.send_email(
            to_email=sub["email"],
            subject=f"🎉 {product_name} is Back in Stock!",
            html_content=html
        )
    
    # Mark as notified
    await subscriptions.update_many(
        {"product_id": product_id, "notified": False},
        {"$set": {"notified": True, "notified_at": datetime.utcnow()}}
    )
    
    return {"notified_count": len(subscribers)}


# ============ Flash Sale Notifications ============

async def notify_flash_sale(
    product_ids: List[str],
    discount_percentage: int,
    end_time: datetime
):
    """
    Notify users about flash sale.
    
    Args:
        product_ids: List of product IDs on sale
        discount_percentage: Discount percentage
        end_time: Sale end time
    """
    products_collection = get_products_collection()
    users_collection = get_users_collection()
    
    # Get product details
    products = await products_collection.find({
        "_id": {"$in": [ObjectId(pid) for pid in product_ids]}
    }).to_list(100)
    
    # Get all active users
    users = await users_collection.find({"is_active": True}).to_list(10000)
    
    # Build email
    products_html = ""
    for p in products:
        original_price = p["price"]
        sale_price = original_price * (1 - discount_percentage / 100)
        products_html += f"""
        <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 8px;">
            <h3>{p['name']}</h3>
            <p style="text-decoration: line-through; color: #999;">₹{original_price:.2f}</p>
            <p style="font-size: 24px; color: #B8860B; font-weight: bold;">₹{sale_price:.2f}</p>
            <p>{discount_percentage}% OFF</p>
        </div>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #FF6B6B, #FF8E53); padding: 30px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; font-size: 32px; }}
            .timer {{ background: #fff3cd; padding: 15px; text-align: center; border-radius: 8px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚡ FLASH SALE ⚡</h1>
                <p style="color: white; font-size: 20px;">{discount_percentage}% OFF</p>
            </div>
            
            <div class="timer">
                <p style="margin: 0; font-weight: bold;">Ends: {end_time.strftime('%B %d, %Y at %I:%M %p')}</p>
            </div>
            
            {products_html}
            
            <p style="text-align: center;">
                <a href="http://localhost:3000/sale" style="display: inline-block; background: #FF6B6B; color: white; padding: 15px 40px; text-decoration: none; border-radius: 5px; font-size: 18px;">Shop Now</a>
            </p>
        </div>
    </body>
    </html>
    """
    
    # Send to all users (in batches to avoid overwhelming SMTP)
    batch_size = 100
    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]
        for user in batch:
            await email_service.send_email(
                to_email=user["email"],
                subject=f"⚡ Flash Sale: {discount_percentage}% OFF!",
                html_content=html
            )
    
    return {"notified_count": len(users)}


# ============ Order Status Notifications ============

async def notify_order_status_change(
    order_id: str,
    user_email: str,
    user_name: str,
    old_status: str,
    new_status: str
):
    """
    Notify user of order status change.
    
    This is already handled in orders.py via email_service,
    but this function provides a centralized notification hub.
    """
    # Delegate to existing email service
    if new_status == "shipped":
        await email_service.send_shipping_update(
            order_id=order_id,
            user_email=user_email,
            user_name=user_name
        )
    elif new_status == "delivered":
        await email_service.send_delivery_confirmation(
            order_id=order_id,
            user_email=user_email,
            user_name=user_name
        )


# ============ Wishlist Price Drop Notifications ============

async def check_and_notify_price_drops():
    """
    Check for price drops on wishlisted items and notify users.
    
    This should be run as a scheduled task (e.g., daily cron job).
    """
    db = get_database()
    wishlists = db["wishlists"]
    products_collection = get_products_collection()
    users_collection = get_users_collection()
    
    # Get all wishlists
    all_wishlists = await wishlists.find().to_list(10000)
    
    notifications_sent = 0
    
    for wishlist in all_wishlists:
        user_id = wishlist["user_id"]
        product_ids = wishlist.get("product_ids", [])
        
        if not product_ids:
            continue
        
        # Get user
        user = await users_collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            continue
        
        # Check each product for price drops
        # (This would require storing historical prices, which we'll skip for now)
        # For demo purposes, we'll just notify about products on sale
        
        products = await products_collection.find({
            "_id": {"$in": [ObjectId(pid) for pid in product_ids]},
            "on_sale": True  # Assuming we add this field
        }).to_list(100)
        
        if products:
            # Send notification
            products_html = ""
            for p in products:
                products_html += f"""
                <li>{p['name']} - Now ₹{p['price']:.2f}</li>
                """
            
            html = f"""
            <p>Hi {user['name']},</p>
            <p>Great news! Some items in your wishlist are now on sale:</p>
            <ul>{products_html}</ul>
            <p><a href="http://localhost:3000/wishlist">View Wishlist</a></p>
            """
            
            await email_service.send_email(
                to_email=user["email"],
                subject="💰 Price Drop Alert on Your Wishlist!",
                html_content=html
            )
            
            notifications_sent += 1
    
    return {"notifications_sent": notifications_sent}
