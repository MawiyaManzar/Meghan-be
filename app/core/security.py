"""
Security utilities for authentication.
Handles password hashing and JWT token operations.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import hashlib
import base64
import bcrypt
from jose import JWTError, jwt
from app.core.config import settings

# Note: Using bcrypt directly instead of passlib to avoid initialization issues
# and to have better control over password length handling


def _prehash_password(password: str) -> str:
    """
    Pre-hash password with SHA-256 to handle bcrypt's 72-byte limit.
    This ensures passwords of any length can be hashed securely.
    
    Args:
        password: Plain text password
    
    Returns:
        Base64-encoded SHA-256 hash (44 characters, ~44 bytes when UTF-8 encoded, well under bcrypt's 72-byte limit)
    """
    # Get SHA-256 hash as bytes (64 bytes)
    hash_bytes = hashlib.sha256(password.encode('utf-8')).digest()
    # Encode as base64 string (44 characters, safe for bcrypt)
    return base64.b64encode(hash_bytes).decode('ascii')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain password against a hashed password.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Bcrypt hash of the password (includes SHA-256 pre-hash)
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        # Pre-hash the plain password before comparing (returns base64 string)
        prehashed = _prehash_password(plain_password)
        # Use bcrypt directly to verify
        return bcrypt.checkpw(prehashed.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using SHA-256 + bcrypt.
    This handles passwords longer than bcrypt's 72-byte limit.
    
    Args:
        password: Plain text password to hash
    
    Returns:
        Bcrypt hash of the base64-encoded SHA-256 pre-hashed password (as string)
    """
    # Pre-hash with SHA-256 and encode as base64 (produces 44-char string, ~44 bytes UTF-8, under bcrypt's 72-byte limit)
    prehashed = _prehash_password(password)
    # Hash with bcrypt directly (returns bytes, convert to string for storage)
    hashed = bcrypt.hashpw(prehashed.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing the data to encode in the token (typically email)
        expires_delta: Optional timedelta for token expiration. Defaults to settings.ACCESS_TOKEN_EXPIRE_MINUTES
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT access token.
    
    Args:
        token: JWT token string to decode
    
    Returns:
        Decoded token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

