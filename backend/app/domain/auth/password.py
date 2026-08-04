"""Password hashing and verification domain service."""

import hashlib
import hmac
import os


class PasswordHasher:
    """Password hashing and verification helper using PBKDF2-HMAC-SHA256."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash plain text password with PBKDF2-HMAC-SHA256."""

        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100000)
        return salt.hex() + ":" + key.hex()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify plain text password against hashed salt:key representation."""

        try:
            salt_hex, key_hex = hashed_password.split(":")
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(key_hex)
            computed_key = hashlib.pbkdf2_hmac(
                "sha256", plain_password.encode("utf-8"), salt, 100000
            )
            return hmac.compare_digest(expected_key, computed_key)
        except Exception:
            return False


__all__ = ["PasswordHasher"]
