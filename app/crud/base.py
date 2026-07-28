"""
基础 CRUD 封装 - 通用数据库操作（含软删除）
"""
from datetime import datetime, timezone
from typing import TypeVar, Generic, Type, Sequence

from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """通用 CRUD 基类 - 默认过滤已删除记录，delete 为软删除"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> ModelType | None:
        return db.query(self.model).filter(
            self.model.id == id,
            self.model.is_deleted == False,  # noqa: E712
        ).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[ModelType]:
        return db.query(self.model).filter(
            self.model.is_deleted == False,  # noqa: E712
        ).offset(skip).limit(limit).all()

    def get_count(self, db: Session) -> int:
        return db.query(func.count(self.model.id)).filter(
            self.model.is_deleted == False,  # noqa: E712
        ).scalar() or 0

    def create(self, db: Session, obj_in: BaseModel | dict) -> ModelType:
        if isinstance(obj_in, BaseModel):
            data = obj_in.model_dump(exclude_unset=True)
        else:
            data = obj_in
        db_obj = self.model(**data)
        db.add(db_obj)
        db.flush()
        return db_obj

    def update(
        self,
        db: Session,
        db_obj: ModelType,
        obj_in: BaseModel | dict,
    ) -> ModelType:
        if isinstance(obj_in, BaseModel):
            update_data = obj_in.model_dump(exclude_unset=True)
        else:
            update_data = obj_in

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        db.flush()
        return db_obj

    def delete(self, db: Session, id: int) -> bool:
        """软删除 - 标记 is_deleted=True 并记录删除时间"""
        obj = db.query(self.model).filter(
            self.model.id == id,
            self.model.is_deleted == False,  # noqa: E712
        ).first()
        if obj:
            obj.is_deleted = True
            obj.deleted_at = datetime.now(timezone.utc)
            db.flush()
            return True
        return False
