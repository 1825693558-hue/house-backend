"""
小区接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, require_admin
from app.crud.community import community_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.community import CommunityCreate, CommunityUpdate, CommunityOut, CommunitySimple
from app.schemas.response import ok

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
async def create_community(
    comm_in: CommunityCreate,
    db: Session = Depends(get_db),
):
    """新增小区（ADMIN）"""
    existing = community_crud.get_by_name(db, name=comm_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"小区 '{comm_in.name}' 已存在",
        )

    community = community_crud.create(db, obj_in=comm_in)
    db.commit()
    db.refresh(community)

    return ok(data=CommunityOut.model_validate(community).model_dump(), msg="创建成功")


@router.get("")
async def list_communities(
    keyword: str | None = Query(default=None, description="搜索关键词"),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=100, ge=1, le=100),
    simple: bool = Query(default=False, description="是否返回简洁模式(下拉选择用)"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
):
    """获取小区列表"""
    skip = (page - 1) * size
    communities = community_crud.get_list(db, keyword=keyword, skip=skip, limit=size)
    total = community_crud.get_count(db, keyword=keyword)

    if simple:
        items = [CommunitySimple.model_validate(c).model_dump() for c in communities]
    else:
        items = [CommunityOut.model_validate(c).model_dump() for c in communities]

    return ok(data={
        "total": total,
        "page": page,
        "size": size,
        "items": items,
    })


@router.put("/{community_id}", dependencies=[Depends(require_admin)])
async def update_community(
    community_id: int,
    comm_in: CommunityUpdate,
    db: Session = Depends(get_db),
):
    """修改小区（ADMIN）"""
    community = community_crud.get(db, id=community_id)
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="小区不存在")

    # 如果修改名称，检查重名
    if comm_in.name and comm_in.name != community.name:
        existing = community_crud.get_by_name(db, name=comm_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"小区 '{comm_in.name}' 已存在",
            )

    community = community_crud.update(db, db_obj=community, obj_in=comm_in)
    db.commit()
    db.refresh(community)

    return ok(data=CommunityOut.model_validate(community).model_dump(), msg="修改成功")


@router.delete("/{community_id}", dependencies=[Depends(require_admin)])
async def delete_community(
    community_id: int,
    db: Session = Depends(get_db),
):
    """删除小区（ADMIN）- 如果小区下有房源则禁止删除"""
    community = community_crud.get(db, id=community_id)
    if not community:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="小区不存在")

    if community_crud.has_houses(db, community_id=community_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该小区下存在房源，无法删除",
        )

    community_crud.delete(db, id=community_id)
    db.commit()

    return ok(msg="删除成功")
