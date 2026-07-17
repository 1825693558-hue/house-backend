"""
账号管理接口（ADMIN 专属）
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.core.security import hash_password
from app.crud.user import user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.response import ok
from app.schemas.user import UserCreate, UserUpdate, UserOut

router = APIRouter()


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """获取当前登录用户信息"""
    return ok(data=UserOut.model_validate(current_user).model_dump())


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    """创建账号（ADMIN）"""
    try:
        user = user_crud.create(db, obj_in=user_in, password_hash=hash_password(user_in.password))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    db.commit()
    db.refresh(user)

    return ok(data=UserOut.model_validate(user).model_dump(), msg="创建成功")


@router.get("", dependencies=[Depends(require_admin)])
async def list_users(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """账号列表（ADMIN）"""
    skip = (page - 1) * size
    users = user_crud.get_multi(db, skip=skip, limit=size)
    total = user_crud.get_count(db)

    return ok(data={
        "total": total,
        "page": page,
        "size": size,
        "items": [UserOut.model_validate(u).model_dump() for u in users],
    })


@router.put("/{user_id}", dependencies=[Depends(require_admin)])
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: Session = Depends(get_db),
):
    """修改账号信息/角色（ADMIN）"""
    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    # 如果修改密码，生成新的哈希
    pwd_hash = None
    if user_in.password:
        pwd_hash = hash_password(user_in.password)

    user = user_crud.update(db, db_obj=user, obj_in=user_in, password_hash=pwd_hash)
    db.commit()
    db.refresh(user)

    return ok(data=UserOut.model_validate(user).model_dump(), msg="修改成功")


@router.delete("/{user_id}", dependencies=[Depends(require_admin)])
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除账号（ADMIN）- 不能删除自己"""
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账号",
        )

    user = user_crud.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    user_crud.delete(db, id=user_id)
    db.commit()

    return ok(msg="删除成功")
