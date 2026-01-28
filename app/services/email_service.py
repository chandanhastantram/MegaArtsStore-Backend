"""
Email Service
Handles email notifications for orders and account events
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from datetime import datetime
import asyncio

from app.config import get_settings


async def send_email(
    to_email: str,
    subject: str,
    html_content: str,
    plain_content: str = None
) -> bool:
    """
    Send an email using SMTP.
    
    Args:
        to_email: Recipient email
        subject: Email subject
        html_content: HTML body
        plain_content: Plain text fallback
    
    Returns:
        True if sent successfully
    """
    settings = get_settings()
    
    if not settings.smtp_host:
        print("SMTP not configured, skipping email")
        return False
    
    msg = MIMEMultipart("alternative")
    msg["From"] = settings.smtp_from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    
    if plain_content:
        msg.attach(MIMEText(plain_content, "plain"))
    msg.attach(MIMEText(html_content, "html"))
    
    try:
        # Run SMTP in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, _send_smtp, msg, settings)
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def _send_smtp(msg: MIMEMultipart, settings):
    """Synchronous SMTP send"""
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)


# ============ Order Emails ============

async def send_order_confirmation(order: dict, user_email: str, user_name: str) -> bool:
    """Send order confirmation email"""
    
    items_html = ""
    for item in order["items"]:
        items_html += f"""
        <tr>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['product_name']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['size']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">{item['quantity']}</td>
            <td style="padding: 10px; border-bottom: 1px solid #eee;">₹{item['subtotal']:.2f}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #B8860B, #DAA520); padding: 20px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; }}
            .order-details {{ background: #f9f9f9; padding: 20px; margin: 20px 0; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #333; color: white; padding: 10px; text-align: left; }}
            .total {{ font-size: 18px; font-weight: bold; color: #B8860B; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🛍️ Order Confirmed!</h1>
            </div>
            
            <p>Hi {user_name},</p>
            <p>Thank you for your order! We're excited to craft your beautiful jewellery.</p>
            
            <div class="order-details">
                <h3>Order #{order['order_id']}</h3>
                <p>Placed on: {order['created_at'].strftime('%B %d, %Y')}</p>
                
                <table>
                    <tr>
                        <th>Product</th>
                        <th>Size</th>
                        <th>Qty</th>
                        <th>Price</th>
                    </tr>
                    {items_html}
                </table>
                
                <hr style="margin: 20px 0;">
                
                <p>Subtotal: ₹{order['subtotal']:.2f}</p>
                <p>Shipping: ₹{order['shipping_cost']:.2f}</p>
                <p>Tax (GST): ₹{order['tax']:.2f}</p>
                <p class="total">Total: ₹{order['total']:.2f}</p>
            </div>
            
            <h3>Shipping Address</h3>
            <p>
                {order['shipping_address']['name']}<br>
                {order['shipping_address']['address_line1']}<br>
                {order['shipping_address'].get('address_line2', '')}<br>
                {order['shipping_address']['city']}, {order['shipping_address']['state']} {order['shipping_address']['pincode']}
            </p>
            
            <p>We'll send you another email when your order ships.</p>
            
            <p>With love,<br>MegaArtsStore Team</p>
        </div>
    </body>
    </html>
    """
    
    return await send_email(
        to_email=user_email,
        subject=f"Order Confirmed - #{order['order_id']}",
        html_content=html,
        plain_content=f"Order #{order['order_id']} confirmed. Total: ₹{order['total']:.2f}"
    )


async def send_shipping_update(
    order_id: str,
    user_email: str,
    user_name: str,
    tracking_number: str = None,
    carrier: str = None
) -> bool:
    """Send shipping update email"""
    
    tracking_info = ""
    if tracking_number:
        tracking_info = f"""
        <p><strong>Tracking Number:</strong> {tracking_number}</p>
        <p><strong>Carrier:</strong> {carrier or 'Standard Shipping'}</p>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #2E8B57, #3CB371); padding: 20px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; }}
            .tracking {{ background: #f0fff0; padding: 20px; margin: 20px 0; border-radius: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📦 Your Order is on the Way!</h1>
            </div>
            
            <p>Hi {user_name},</p>
            <p>Great news! Your order #{order_id} has been shipped and is on its way to you.</p>
            
            <div class="tracking">
                <h3>Tracking Information</h3>
                {tracking_info if tracking_info else '<p>Tracking information will be available soon.</p>'}
            </div>
            
            <p>Estimated delivery: 3-5 business days</p>
            
            <p>Happy shopping!<br>MegaArtsStore Team</p>
        </div>
    </body>
    </html>
    """
    
    return await send_email(
        to_email=user_email,
        subject=f"Your Order #{order_id} has Shipped!",
        html_content=html
    )


async def send_delivery_confirmation(
    order_id: str,
    user_email: str,
    user_name: str
) -> bool:
    """Send delivery confirmation email"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #B8860B, #DAA520); padding: 20px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 Order Delivered!</h1>
            </div>
            
            <p>Hi {user_name},</p>
            <p>Your order #{order_id} has been delivered!</p>
            
            <p>We hope you love your new jewellery. If you have any questions or concerns, please don't hesitate to reach out.</p>
            
            <p>We'd love to hear from you! Please consider leaving a review on the products you purchased.</p>
            
            <p>Thank you for shopping with us!<br>MegaArtsStore Team</p>
        </div>
    </body>
    </html>
    """
    
    return await send_email(
        to_email=user_email,
        subject=f"Your Order #{order_id} has been Delivered!",
        html_content=html
    )


# ============ Account Emails ============

async def send_welcome_email(user_email: str, user_name: str) -> bool:
    """Send welcome email to new users"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #B8860B, #DAA520); padding: 30px; text-align: center; }}
            .header h1 {{ color: white; margin: 0; }}
            .feature {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✨ Welcome to MegaArtsStore!</h1>
            </div>
            
            <p>Hi {user_name},</p>
            <p>Welcome to MegaArtsStore - your destination for beautiful, handcrafted jewellery!</p>
            
            <div class="feature">
                <h4>🔮 AR Try-On</h4>
                <p>Try bangles on your wrist using our AR feature before you buy!</p>
            </div>
            
            <div class="feature">
                <h4>💎 Handcrafted Quality</h4>
                <p>Each piece is carefully crafted by skilled artisans.</p>
            </div>
            
            <div class="feature">
                <h4>📦 Free Shipping</h4>
                <p>Free shipping on orders above ₹5,000!</p>
            </div>
            
            <p>Start exploring our collection today!</p>
            
            <p>With love,<br>MegaArtsStore Team</p>
        </div>
    </body>
    </html>
    """
    
    return await send_email(
        to_email=user_email,
        subject="Welcome to MegaArtsStore! ✨",
        html_content=html
    )


async def send_password_reset_email(
    user_email: str,
    user_name: str,
    reset_token: str,
    reset_url: str
) -> bool:
    """Send password reset email"""
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .button {{ display: inline-block; background: #B8860B; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h2>Password Reset Request</h2>
            
            <p>Hi {user_name},</p>
            <p>We received a request to reset your password. Click the button below to set a new password:</p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}?token={reset_token}" class="button">Reset Password</a>
            </p>
            
            <p>This link will expire in 1 hour.</p>
            
            <p>If you didn't request this, please ignore this email.</p>
            
            <p>Best regards,<br>MegaArtsStore Team</p>
        </div>
    </body>
    </html>
    """
    
    return await send_email(
        to_email=user_email,
        subject="Reset Your Password - MegaArtsStore",
        html_content=html
    )
