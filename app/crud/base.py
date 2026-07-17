"""
基础 CRUD 封装 - 通用数据库操作
"""
from typing import TypeVar, Generic, Type, Any, Sequence

from pydantic import BaseModel
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    """通用 CRUD 基类"""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> ModelType | None:
        return db.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 20,
    ) -> Sequence[ModelType]:
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_count(self, db: Session) -> int:
        return db.query(func.count(self.model.id)).scalar() or 0

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
        obj = db.query(self.model).filter(self.model.id == id).first()
        if obj:
            db.delete(obj)
            db.flush()
            return True
        return False