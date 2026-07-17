"""
用户 CRUD
"""
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User]):
    def get_by_username(self, db: Session, username: str) -> User | None:
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, obj_in: UserCreate, password_hash: str) -> User:
        db_obj = User(
            username=obj_in.username,
            password_hash=password_hash,
            nickname=obj_in.nickname,
            role=obj_in.role,
        )
        db.add(db_obj)
        db.flush()
        return db_obj

    def update(self, db: Session, db_obj: User, obj_in: UserUpdate, password_hash: str | None = None) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        if password_hash:
            update_data["password_hash"] = password_hash
        if "password" in update_data:
            del update_data["password"]
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.flush()
        return db_obj


user_crud = CRUDUser(User)