"""
安全工具 - 密码哈希、JWT 生成与验证、AES 加密/解密
"""
import base64
import hashlib
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

from app.core.config import settings


# ============ 密码哈希 (bcrypt) ============

def hash_password(password: str) -> str:
    """使用 bcrypt 对密码进行哈希 (cost factor = 12)"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码是否匹配"""
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# ============ JWT Token ============

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """生成 JWT Access Token"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(days=settings.JWT_EXPIRE_DAYS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """解码并验证 JWT Token，失败返回 None"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ============ AES-256-CBC 加密/解密 (密码锁密码) ============

def _get_aes_key() -> bytes:
    """将 AES_SECRET_KEY 统一处理为 32 字节密钥"""
    key = settings.AES_SECRET_KEY
    if len(key.encode("utf-8")) == 32:
        return key.encode("utf-8")
    # SHA-256 哈希确保 32 字节
    return hashlib.sha256(key.encode("utf-8")).digest()


def aes_encrypt(plaintext: str) -> str:
    """AES-256-CBC 加密，返回 base64 编码的密文"""
    key = _get_aes_key()
    iv = hashlib.md5(key).digest()[:16]  # 固定 IV，基于密钥派生
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # PKCS7 填充
    block_size = 16
    padding = block_size - (len(plaintext.encode("utf-8")) % block_size)
    padded = plaintext.encode("utf-8") + bytes([padding] * padding)

    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode("utf-8")


def aes_decrypt(ciphertext_b64: str) -> str:
    """AES-256-CBC 解密，输入 base64 编码的密文，返回明文"""
    key = _get_aes_key()
    iv = hashlib.md5(key).digest()[:16]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    ciphertext = base64.b64decode(ciphertext_b64)
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    # 去除 PKCS7 填充
    padding = padded[-1]
    return padded[:-padding].decode("utf-8")