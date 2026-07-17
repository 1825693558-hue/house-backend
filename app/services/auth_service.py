"""
认证业务逻辑
"""
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password, create_access_token
from app.crud.user import user_crud
from app.models.user import User
from app.schemas.user import UserCreate


class AuthService:
    @staticmethod
    def authenticate(db: Session, username: str, password: str) -> User | None:
        """验证用户名密码，成功返回用户对象"""
        user = user_crud.get_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def create_token(user: User) -> str:
        """为用户生成 JWT Token"""
        return create_access_token(data={"sub": str(user.id), "role": user.role})

    @staticmethod
    def create_user(db: Session, user_in: UserCreate) -> User:
        """创建新用户"""
        existing = user_crud.get_by_username(db, username=user_in.username)
        if existing:
            raise ValueError("用户名已存在")
        pwd_hash = hash_password(user_in.password)
        return user_crud.create(db, obj_in=user_in, password_hash=pwd_hash)


auth_service = AuthService()