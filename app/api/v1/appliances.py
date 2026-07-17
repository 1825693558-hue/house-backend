"""
家电类型接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.crud.appliance import appliance_crud
from app.db.session import get_db
from app.schemas.appliance import ApplianceCreate, ApplianceUpdate, ApplianceOut
from app.schemas.response import ok

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_appliance(
    app_in: ApplianceCreate,
    db: Session = Depends(get_db),
):
    """新增家电类型（ADMIN）"""
    appliance = appliance_crud.create(db, obj_in=app_in)
    db.commit()
    db.refresh(appliance)

    return ok(data=ApplianceOut.model_validate(appliance).model_dump(), msg="创建成功")


@router.get("")
async def list_appliances(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    """获取家电类型列表（ADMIN）"""
    appliances = appliance_crud.get_list(db)
    total = appliance_crud.get_count(db)

    return ok(data={
        "total": total,
        "items": [ApplianceOut.model_validate(a).model_dump() for a in appliances],
    })


@router.put("/{appliance_id}", dependencies=[Depends(require_admin)])
async def update_appliance(
    appliance_id: int,
    app_in: ApplianceUpdate,
    db: Session = Depends(get_db),
):
    """修改家电类型（ADMIN）"""
    appliance = appliance_crud.get(db, id=appliance_id)
    if not appliance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="家电类型不存在")

    appliance = appliance_crud.update(db, db_obj=appliance, obj_in=app_in)
    db.commit()
    db.refresh(appliance)

    return ok(data=ApplianceOut.model_validate(appliance).model_dump(), msg="修改成功")


@router.delete("/{appliance_id}", dependencies=[Depends(require_admin)])
async def delete_appliance(
    appliance_id: int,
    db: Session = Depends(get_db),
):
    """删除家电类型（ADMIN）- 被房源引用时禁止删除"""
    appliance = appliance_crud.get(db, id=appliance_id)
    if not appliance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="家电类型不存在")

    if appliance_crud.is_used_by_house(db, appliance_id=appliance_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该家电类型已被房源引用，无法删除",
        )

    appliance_crud.delete(db, id=appliance_id)
    db.commit()

    return ok(msg="删除成功")
