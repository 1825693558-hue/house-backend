"""
房源接口
"""
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.crud.house import house_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.house import HouseCreate, HouseUpdate, HouseStatusUpdate
from app.schemas.response import ok
from app.services.house_service import house_service

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_house(
    house_in: HouseCreate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """创建房源（含联系人+家电）"""
    try:
        house = house_service.create_house(db, house_in=house_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return ok(data={"id": house.id}, msg="创建成功")


@router.get("")
async def list_houses(
    page: int = Query(default=1, ge=1, description="页码"),
    size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    keyword: str | None = Query(default=None, description="关键词搜索"),
    community_id: int | None = Query(default=None, description="按小区筛选"),
    status: str | None = Query(default=None, description="按状态筛选(逗号分隔)"),
    decoration: str | None = Query(default=None, description="按装修状况筛选"),
    key_type: str | None = Query(default=None, description="按钥匙类型筛选"),
    min_area: float | None = Query(default=None, description="最小面积"),
    max_area: float | None = Query(default=None, description="最大面积"),
    min_floor: int | None = Query(default=None, description="最小楼层"),
    max_floor: int | None = Query(default=None, description="最大楼层"),
    start_date: date | None = Query(default=None, description="创建时间起始"),
    end_date: date | None = Query(default=None, description="创建时间截止"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """查询房源列表（分页+多条件筛选）"""
    items, total = house_crud.query_houses(
        db,
        page=page,
        size=size,
        keyword=keyword,
        community_id=community_id,
        status=status,
        decoration=decoration,
        key_type=key_type,
        min_area=min_area,
        max_area=max_area,
        min_floor=min_floor,
        max_floor=max_floor,
        start_date=start_date,
        end_date=end_date,
    )

    return ok(data={
        "total": total,
        "page": page,
        "size": size,
        "items": items,
    })


@router.get("/{house_id}")
async def get_house(
    house_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """获取房源详情"""
    detail = house_service.get_house_detail(db, house_id)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="房源不存在")

    return ok(data=detail)


@router.put("/{house_id}")
async def update_house(
    house_id: int,
    house_in: HouseUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """更新房源（含联系人+家电）"""
    house = house_crud.get(db, id=house_id)
    if not house:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="房源不存在")

    try:
        house = house_service.update_house(db, house=house, house_in=house_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return ok(data={"id": house.id}, msg="更新成功")


@router.patch("/{house_id}")
async def patch_house(
    house_id: int,
    status_in: HouseStatusUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """部分更新房源状态（含合法性校验）"""
    house = house_crud.get(db, id=house_id)
    if not house:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="房源不存在")

    try:
        house = house_service.update_status(db, house=house, new_status=status_in.status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return ok(data={"id": house.id, "status": house.status}, msg="状态更新成功")


@router.delete("/{house_id}")
async def delete_house(
    house_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """删除房源（级联删除联系人和家电关联）"""
    house = house_crud.get(db, id=house_id)
    if not house:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="房源不存在")

    house_service.delete_house(db, house=house)

    return ok(msg="删除成功")
