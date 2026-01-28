"""
Security Routes
Password reset, email verification, and 2FA endpoints
"""

from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.services.security_service import SecurityService
from app.utils.auth import get_current_user

router = APIRouter()


# ============ Password Reset ============

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str


@router.post("/password-reset/request")
async def request_password_reset(request_data: PasswordResetRequest):
    """
    Request a password reset.
    
    - Public endpoint
    - Sends reset email if user exists
    """
    # Always return success to prevent email enumeration
    await SecurityService.generate_password_reset_token(request_data.email)
    
    return {
        "message": "If an account with that email exists, a password reset link has been sent."
    }


@router.post("/password-reset/verify")
async def verify_reset_token(token: str):
    """
    Verify a password reset token.
    
    - Public endpoint
    - Returns user info if token is valid
    """
    user = await SecurityService.verify_reset_token(token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {
        "valid": True,
        "email": user.get("email")
    }


@router.post("/password-reset/confirm")
async def confirm_password_reset(reset_data: PasswordResetConfirm):
    """
    Reset password using token.
    
    - Public endpoint
    - Requires valid token and new password
    """
    success = await SecurityService.reset_password(
        token=reset_data.token,
        new_password=reset_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password reset successfully"}


# ============ Email Verification ============

@router.post("/email/verify")
async def verify_email(token: str):
    """
    Verify email address using token.
    
    - Public endpoint
    """
    success = await SecurityService.verify_email(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email verified successfully"}


@router.post("/email/resend-verification")
async def resend_verification_email(
    current_user: dict = Depends(get_current_user)
):
    """
    Resend email verification.
    
    - Authenticated users only
    """
    if current_user.get("email_verified"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    await SecurityService.generate_email_verification_token(
        user_id=str(current_user["_id"]),
        email=current_user["email"]
    )
    
    return {"message": "Verification email sent"}


# ============ Two-Factor Authentication ============

class TwoFactorSetup(BaseModel):
    """Schema for 2FA setup verification"""
    verification_code: str


class TwoFactorVerify(BaseModel):
    """Schema for 2FA code verification"""
    code: str


class TwoFactorDisable(BaseModel):
    """Schema for disabling 2FA"""
    password: str


@router.post("/2fa/setup")
async def setup_2fa(
    current_user: dict = Depends(get_current_user)
):
    """
    Setup 2FA for current user.
    
    - Authenticated users only
    - Returns QR code for authenticator app
    """
    if current_user.get("two_factor_enabled"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2FA is already enabled"
        )
    
    setup_data = await SecurityService.setup_2fa(str(current_user["_id"]))
    
    return {
        "message": "Scan the QR code with your authenticator app",
        "secret": setup_data["secret"],
        "qr_code_url": setup_data["qr_code_url"]
    }


@router.post("/2fa/enable")
async def enable_2fa(
    setup_data: TwoFactorSetup,
    current_user: dict = Depends(get_current_user)
):
    """
    Enable 2FA after verifying setup code.
    
    - Authenticated users only
    - Requires verification code from authenticator app
    """
    success = await SecurityService.enable_2fa(
        user_id=str(current_user["_id"]),
        verification_code=setup_data.verification_code
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    return {"message": "2FA enabled successfully"}


@router.post("/2fa/verify")
async def verify_2fa(
    verify_data: TwoFactorVerify,
    current_user: dict = Depends(get_current_user)
):
    """
    Verify a 2FA code.
    
    - Authenticated users only
    """
    valid = await SecurityService.verify_2fa_code(
        user_id=str(current_user["_id"]),
        code=verify_data.code
    )
    
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid 2FA code"
        )
    
    return {"message": "2FA code verified", "valid": True}


@router.post("/2fa/disable")
async def disable_2fa(
    disable_data: TwoFactorDisable,
    current_user: dict = Depends(get_current_user)
):
    """
    Disable 2FA.
    
    - Authenticated users only
    - Requires password confirmation
    """
    success = await SecurityService.disable_2fa(
        user_id=str(current_user["_id"]),
        password=disable_data.password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password or 2FA not enabled"
        )
    
    return {"message": "2FA disabled successfully"}


# ============ Session Management ============

@router.get("/sessions")
async def get_active_sessions(
    current_user: dict = Depends(get_current_user)
):
    """
    Get all active sessions for current user.
    
    - Authenticated users only
    """
    sessions = await SecurityService.get_active_sessions(str(current_user["_id"]))
    
    return {
        "count": len(sessions),
        "sessions": sessions
    }


@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke a specific session.
    
    - Authenticated users only
    """
    await SecurityService.revoke_session(session_id)
    
    return {"message": "Session revoked successfully"}


@router.delete("/sessions")
async def revoke_all_sessions(
    current_user: dict = Depends(get_current_user)
):
    """
    Revoke all sessions except current one.
    
    - Authenticated users only
    """
    await SecurityService.revoke_all_sessions(str(current_user["_id"]))
    
    return {"message": "All sessions revoked successfully"}
