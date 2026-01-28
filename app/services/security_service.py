"""
Security Service
Advanced security features: password reset, email verification, 2FA
"""

import secrets
import pyotp
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from bson import ObjectId

from app.database import db
from app.services.email_service import send_email
from app.utils.auth import hash_password


class SecurityService:
    """Service for advanced security operations"""

    @staticmethod
    async def generate_password_reset_token(email: str) -> Optional[str]:
        """
        Generate a password reset token for a user.
        
        Returns token if user exists, None otherwise
        """
        user = await db.users.find_one({"email": email})
        if not user:
            return None
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # Token valid for 1 hour
        
        # Store token in database
        await db.password_reset_tokens.insert_one({
            "user_id": str(user["_id"]),
            "email": email,
            "token": token,
            "expires_at": expires_at,
            "used": False,
            "created_at": datetime.utcnow()
        })
        
        # Send reset email
        reset_link = f"https://yourdomain.com/reset-password?token={token}"
        subject = "Password Reset Request"
        body = f"""
        <h2>Password Reset Request</h2>
        <p>Hi {user.get('full_name', 'there')},</p>
        <p>We received a request to reset your password. Click the link below to reset it:</p>
        <p><a href="{reset_link}">Reset Password</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
        """
        
        await send_email(email, subject, body)
        
        return token

    @staticmethod
    async def verify_reset_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a password reset token.
        
        Returns user info if valid, None otherwise
        """
        token_doc = await db.password_reset_tokens.find_one({
            "token": token,
            "used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not token_doc:
            return None
        
        user = await db.users.find_one({"_id": ObjectId(token_doc["user_id"])})
        return user

    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool:
        """
        Reset password using a valid token.
        
        Returns True if successful, False otherwise
        """
        # Verify token
        token_doc = await db.password_reset_tokens.find_one({
            "token": token,
            "used": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not token_doc:
            return False
        
        # Update password
        hashed_password = hash_password(new_password)
        await db.users.update_one(
            {"_id": ObjectId(token_doc["user_id"])},
            {"$set": {"password": hashed_password, "updated_at": datetime.utcnow()}}
        )
        
        # Mark token as used
        await db.password_reset_tokens.update_one(
            {"_id": token_doc["_id"]},
            {"$set": {"used": True}}
        )
        
        return True

    @staticmethod
    async def generate_email_verification_token(user_id: str, email: str) -> str:
        """
        Generate an email verification token.
        """
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=7)  # Token valid for 7 days
        
        # Store token
        await db.email_verification_tokens.insert_one({
            "user_id": user_id,
            "email": email,
            "token": token,
            "expires_at": expires_at,
            "verified": False,
            "created_at": datetime.utcnow()
        })
        
        # Send verification email
        verification_link = f"https://yourdomain.com/verify-email?token={token}"
        subject = "Verify Your Email Address"
        body = f"""
        <h2>Welcome to MegaArtsStore!</h2>
        <p>Please verify your email address by clicking the link below:</p>
        <p><a href="{verification_link}">Verify Email</a></p>
        <p>This link will expire in 7 days.</p>
        """
        
        await send_email(email, subject, body)
        
        return token

    @staticmethod
    async def verify_email(token: str) -> bool:
        """
        Verify email using token.
        
        Returns True if successful, False otherwise
        """
        token_doc = await db.email_verification_tokens.find_one({
            "token": token,
            "verified": False,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not token_doc:
            return False
        
        # Mark user as verified
        await db.users.update_one(
            {"_id": ObjectId(token_doc["user_id"])},
            {"$set": {"email_verified": True, "updated_at": datetime.utcnow()}}
        )
        
        # Mark token as verified
        await db.email_verification_tokens.update_one(
            {"_id": token_doc["_id"]},
            {"$set": {"verified": True}}
        )
        
        return True

    @staticmethod
    async def setup_2fa(user_id: str) -> Dict[str, Any]:
        """
        Setup 2FA for a user.
        
        Returns secret and QR code data
        """
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found")
        
        # Generate secret
        secret = pyotp.random_base32()
        
        # Create provisioning URI for QR code
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user.get("email"),
            issuer_name="MegaArtsStore"
        )
        
        # Store secret (not yet enabled)
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "two_factor_secret": secret,
                    "two_factor_enabled": False,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "secret": secret,
            "provisioning_uri": provisioning_uri,
            "qr_code_url": f"https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl={provisioning_uri}"
        }

    @staticmethod
    async def enable_2fa(user_id: str, verification_code: str) -> bool:
        """
        Enable 2FA after verifying the setup code.
        
        Returns True if successful, False otherwise
        """
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user or not user.get("two_factor_secret"):
            return False
        
        # Verify code
        totp = pyotp.TOTP(user["two_factor_secret"])
        if not totp.verify(verification_code):
            return False
        
        # Enable 2FA
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"two_factor_enabled": True, "updated_at": datetime.utcnow()}}
        )
        
        return True

    @staticmethod
    async def verify_2fa_code(user_id: str, code: str) -> bool:
        """
        Verify a 2FA code.
        
        Returns True if valid, False otherwise
        """
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user or not user.get("two_factor_enabled"):
            return False
        
        totp = pyotp.TOTP(user["two_factor_secret"])
        return totp.verify(code)

    @staticmethod
    async def disable_2fa(user_id: str, password: str) -> bool:
        """
        Disable 2FA for a user.
        
        Requires password verification
        """
        from app.utils.auth import verify_password
        
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return False
        
        # Verify password
        if not verify_password(password, user.get("password")):
            return False
        
        # Disable 2FA
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {
                "$set": {
                    "two_factor_enabled": False,
                    "updated_at": datetime.utcnow()
                },
                "$unset": {"two_factor_secret": ""}
            }
        )
        
        return True

    @staticmethod
    async def create_session(user_id: str, device_info: str = None) -> str:
        """
        Create a user session.
        
        Returns session ID
        """
        session_id = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(days=30)  # Session valid for 30 days
        
        await db.sessions.insert_one({
            "session_id": session_id,
            "user_id": user_id,
            "device_info": device_info,
            "expires_at": expires_at,
            "active": True,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow()
        })
        
        return session_id

    @staticmethod
    async def verify_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Verify a session and return user info.
        """
        session = await db.sessions.find_one({
            "session_id": session_id,
            "active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        })
        
        if not session:
            return None
        
        # Update last activity
        await db.sessions.update_one(
            {"_id": session["_id"]},
            {"$set": {"last_activity": datetime.utcnow()}}
        )
        
        # Get user
        user = await db.users.find_one({"_id": ObjectId(session["user_id"])})
        return user

    @staticmethod
    async def revoke_session(session_id: str):
        """Revoke a session"""
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"active": False}}
        )

    @staticmethod
    async def revoke_all_sessions(user_id: str):
        """Revoke all sessions for a user"""
        await db.sessions.update_many(
            {"user_id": user_id},
            {"$set": {"active": False}}
        )

    @staticmethod
    async def get_active_sessions(user_id: str):
        """Get all active sessions for a user"""
        sessions = await db.sessions.find({
            "user_id": user_id,
            "active": True,
            "expires_at": {"$gt": datetime.utcnow()}
        }).to_list(length=100)
        
        return sessions
