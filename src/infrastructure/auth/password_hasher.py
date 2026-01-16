import hashlib
import secrets


class PasswordHasher:
    @staticmethod
    def hash(password: str) -> str:
        salt = secrets.token_hex(16)
        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000,
        )
        return f"{salt}${hashed.hex()}"

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        try:
            salt, stored_hash = hashed_password.split("$")
            new_hash = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode(),
                salt.encode(),
                100000,
            )
            return secrets.compare_digest(new_hash.hex(), stored_hash)
        except ValueError:
            return False
