import hashlib
import os

from app.models.user import User
from app.core.database import SessionLocal


def hash_password(password: str) -> str:
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def verify_password(password: str, stored: str) -> bool:
    salt_hex, key_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    stored_key = bytes.fromhex(key_hex)
    new_key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return new_key == stored_key


def get_user_by_token(token: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.api_token == token).first()
    finally:
        db.close()


def get_user_by_phone(phone: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.phone == phone).first()
    finally:
        db.close()


def get_user_by_email(email: str):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.email == email).first()
    finally:
        db.close()
