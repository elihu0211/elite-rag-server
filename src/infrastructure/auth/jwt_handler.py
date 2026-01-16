"""
JWT 處理器

ABP 對比：
- ABP: IJwtSecurityTokenHandler / ITokenService
- ABP 使用 Microsoft.IdentityModel.Tokens
- Python: 自製輕量 JWT 實作或使用 python-jose
"""
import json
import base64
import hmac
import hashlib
from datetime import datetime, timedelta, timezone
from typing import TypedDict

from src.config import settings


class TokenPayload(TypedDict, total=False):
    """
    JWT Token 載荷型別定義

    ABP 對比：
    - ABP: public class JwtPayload
    - TypedDict 提供編譯時型別檢查，比 dict[str, Any] 更安全
    """

    sub: str  # Subject (user ID)
    email: str
    iat: int  # Issued at
    exp: int  # Expiration


class JWTHandler:
    @staticmethod
    def _base64url_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    @staticmethod
    def _base64url_decode(data: str) -> bytes:
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        return base64.urlsafe_b64decode(data)

    @classmethod
    def create_token(cls, payload: dict[str, Any]) -> str:
        header = {"alg": "HS256", "typ": "JWT"}

        now = datetime.now(timezone.utc)
        payload = {
            **payload,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
        }

        header_b64 = cls._base64url_encode(json.dumps(header).encode())
        payload_b64 = cls._base64url_encode(json.dumps(payload).encode())

        message = f"{header_b64}.{payload_b64}"
        signature = hmac.new(
            settings.jwt_secret_key.encode(),
            message.encode(),
            hashlib.sha256,
        ).digest()
        signature_b64 = cls._base64url_encode(signature)

        return f"{message}.{signature_b64}"

    @classmethod
    def decode_token(cls, token: str) -> TokenPayload | None:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None

            header_b64, payload_b64, signature_b64 = parts

            message = f"{header_b64}.{payload_b64}"
            expected_sig = hmac.new(
                settings.jwt_secret_key.encode(),
                message.encode(),
                hashlib.sha256,
            ).digest()

            actual_sig = cls._base64url_decode(signature_b64)
            if not hmac.compare_digest(expected_sig, actual_sig):
                return None

            payload = json.loads(cls._base64url_decode(payload_b64))

            if payload.get("exp", 0) < datetime.now(timezone.utc).timestamp():
                return None

            return payload
        except Exception:
            return None
