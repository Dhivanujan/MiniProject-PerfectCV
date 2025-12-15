"""
Authentication module
"""
from .jwt_handler import (
    JWTConfig,
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token,
    get_current_user,
    get_current_active_user,
    authenticate_user
)

__all__ = [
    'JWTConfig',
    'verify_password',
    'get_password_hash',
    'create_access_token',
    'create_refresh_token',
    'verify_token',
    'get_current_user',
    'get_current_active_user',
    'authenticate_user'
]
