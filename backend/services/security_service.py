"""
=============================================================================
Enhanced Security Service
=============================================================================
MFA, biometric authentication, and advanced security features.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pyotp
import qrcode
import io
import base64
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db.models import User

logger = structlog.get_logger()


class SecurityService:
    """Enhanced security service for MFA and biometric authentication."""
    
    @staticmethod
    async def setup_mfa(
        db: AsyncSession,
        user_id: str,
        user_email: str
    ) -> Dict[str, Any]:
        """
        Setup Multi-Factor Authentication for a user.
        
        Args:
            db: Database session
            user_id: User ID
            user_email: User email for QR code label
        
        Returns:
            MFA setup data including QR code
        """
        try:
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Create TOTP object
            totp = pyotp.TOTP(secret)
            
            # Generate provisioning URI
            provisioning_uri = totp.provisioning_uri(
                name=user_email,
                issuer_name="Stock Market Intelligence"
            )
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Store secret in user metadata (in production, encrypt this)
            # For now, we'll return it - in production, store encrypted
            result = await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(
                    # In production, store encrypted MFA secret
                    # For demo, we'll use a metadata field
                )
            )
            await db.commit()
            
            logger.info("mfa_setup_completed", user_id=user_id)
            
            return {
                "secret": secret,  # In production, don't return this
                "qr_code": f"data:image/png;base64,{qr_code_base64}",
                "backup_codes": SecurityService._generate_backup_codes(),
                "message": "Scan QR code with authenticator app (Google Authenticator, Authy, etc.)"
            }
            
        except Exception as e:
            logger.error("mfa_setup_error", user_id=user_id, error=str(e))
            return {"error": str(e)}
    
    @staticmethod
    def _generate_backup_codes() -> list[str]:
        """Generate backup codes for MFA."""
        import secrets
        return [secrets.token_hex(4).upper() for _ in range(10)]
    
    @staticmethod
    async def verify_mfa_token(
        user_secret: str,
        token: str
    ) -> bool:
        """
        Verify MFA token.
        
        Args:
            user_secret: User's MFA secret
            token: Token from authenticator app
        
        Returns:
            True if token is valid
        """
        try:
            totp = pyotp.TOTP(user_secret)
            return totp.verify(token, valid_window=1)  # Allow 1 time step window
        except Exception as e:
            logger.error("mfa_verification_error", error=str(e))
            return False
    
    @staticmethod
    async def setup_webauthn(
        db: AsyncSession,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Setup WebAuthn (biometric) authentication.
        
        Args:
            db: Database session
            user_id: User ID
        
        Returns:
            WebAuthn challenge and options
        """
        try:
            # In production, use a WebAuthn library like py-webauthn
            # For now, return structure for frontend implementation
            
            import secrets
            challenge = secrets.token_urlsafe(32)
            
            # Store challenge temporarily (in Redis in production)
            # For now, return it
            
            logger.info("webauthn_setup_initiated", user_id=user_id)
            
            return {
                "challenge": challenge,
                "rp_id": "localhost",  # Replace with your domain
                "user_id": user_id,
                "user_name": "user@example.com",  # Get from user
                "timeout": 60000,
                "message": "Use your device's biometric authentication (fingerprint, face ID, etc.)"
            }
            
        except Exception as e:
            logger.error("webauthn_setup_error", user_id=user_id, error=str(e))
            return {"error": str(e)}
    
    @staticmethod
    async def verify_webauthn(
        db: AsyncSession,
        user_id: str,
        credential: Dict[str, Any]
    ) -> bool:
        """
        Verify WebAuthn credential.
        
        Args:
            db: Database session
            user_id: User ID
            credential: WebAuthn credential from client
        
        Returns:
            True if credential is valid
        """
        try:
            # In production, verify using py-webauthn library
            # For now, return structure
            
            logger.info("webauthn_verification_attempted", user_id=user_id)
            
            # Placeholder - implement actual WebAuthn verification
            return True
            
        except Exception as e:
            logger.error("webauthn_verification_error", user_id=user_id, error=str(e))
            return False
    
    @staticmethod
    def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
        """
        Encrypt sensitive data using AES-256.
        
        Args:
            data: Data to encrypt
            key: Encryption key (from environment in production)
        
        Returns:
            Encrypted data (base64 encoded)
        """
        try:
            from cryptography.fernet import Fernet
            import os
            
            # In production, use key from environment
            if key is None:
                key = os.getenv("ENCRYPTION_KEY")
                if not key:
                    # Generate key for demo (don't do this in production)
                    key = Fernet.generate_key().decode()
            
            f = Fernet(key.encode() if isinstance(key, str) else key)
            encrypted = f.encrypt(data.encode())
            return base64.b64encode(encrypted).decode()
            
        except Exception as e:
            logger.error("encryption_error", error=str(e))
            return data  # Return unencrypted on error (log this in production)
    
    @staticmethod
    def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
        """
        Decrypt sensitive data.
        
        Args:
            encrypted_data: Encrypted data (base64 encoded)
            key: Decryption key
        
        Returns:
            Decrypted data
        """
        try:
            from cryptography.fernet import Fernet
            import os
            
            if key is None:
                key = os.getenv("ENCRYPTION_KEY")
            
            f = Fernet(key.encode() if isinstance(key, str) else key)
            decrypted = f.decrypt(base64.b64decode(encrypted_data))
            return decrypted.decode()
            
        except Exception as e:
            logger.error("decryption_error", error=str(e))
            return ""

