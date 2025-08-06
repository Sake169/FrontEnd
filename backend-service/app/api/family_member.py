from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional
from app.core.database import get_db
from app.models.family_member import (
    FamilyMember, 
    FamilyMemberCreate, 
    FamilyMemberUpdate, 
    FamilyMemberResponse,
    FamilyMemberListResponse,
    FamilyMemberStatsResponse
)
from app.core.security import get_current_user
from app.models.user import User
import math

router = APIRouter()

@router.post("/", response_model=FamilyMemberResponse)
def create_family_member(
    family_member: FamilyMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建家属亲戚信息
    """
    # 检查证件号码是否已存在
    existing_member = db.query(FamilyMember).filter(
        FamilyMember.id_number == family_member.id_number
    ).first()
    if existing_member:
        raise HTTPException(status_code=400, detail="该证件号码已存在")
    
    # 创建家属亲戚记录，自动设置employee_username为当前用户
    family_member_data = family_member.dict()
    family_member_data['employee_username'] = current_user.username
    db_family_member = FamilyMember(**family_member_data)
    db.add(db_family_member)
    db.commit()
    db.refresh(db_family_member)
    
    return db_family_member

@router.get("/", response_model=FamilyMemberListResponse)
def get_family_members(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    employee_username: Optional[str] = Query(None, description="证券从业人员用户名"),
    relationship: Optional[str] = Query(None, description="关系类型"),
    name: Optional[str] = Query(None, description="姓名搜索"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取家属亲戚列表
    """
    query = db.query(FamilyMember)
    
    # 应用过滤条件
    if employee_username:
        query = query.filter(FamilyMember.employee_username == employee_username)
    if relationship:
        query = query.filter(FamilyMember.relationship == relationship)
    if name:
        query = query.filter(FamilyMember.name.contains(name))
    
    # 获取总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    # 计算总页数
    pages = math.ceil(total / size)
    
    return FamilyMemberListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{family_member_id}", response_model=FamilyMemberResponse)
def get_family_member(
    family_member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取家属亲戚详情
    """
    family_member = db.query(FamilyMember).filter(
        FamilyMember.id == family_member_id
    ).first()
    
    if not family_member:
        raise HTTPException(status_code=404, detail="家属亲戚信息不存在")
    
    return family_member

@router.put("/{family_member_id}", response_model=FamilyMemberResponse)
def update_family_member(
    family_member_id: int,
    family_member_update: FamilyMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新家属亲戚信息
    """
    family_member = db.query(FamilyMember).filter(
        FamilyMember.id == family_member_id
    ).first()
    
    if not family_member:
        raise HTTPException(status_code=404, detail="家属亲戚信息不存在")
    
    # 如果更新证件号码，检查是否与其他记录冲突
    if family_member_update.id_number and family_member_update.id_number != family_member.id_number:
        existing_member = db.query(FamilyMember).filter(
            and_(
                FamilyMember.id_number == family_member_update.id_number,
                FamilyMember.id != family_member_id
            )
        ).first()
        if existing_member:
            raise HTTPException(status_code=400, detail="该证件号码已存在")
    
    # 更新字段
    update_data = family_member_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(family_member, field, value)
    
    db.commit()
    db.refresh(family_member)
    
    return family_member

@router.delete("/{family_member_id}")
def delete_family_member(
    family_member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除家属亲戚信息
    """
    family_member = db.query(FamilyMember).filter(
        FamilyMember.id == family_member_id
    ).first()
    
    if not family_member:
        raise HTTPException(status_code=404, detail="家属亲戚信息不存在")
    
    db.delete(family_member)
    db.commit()
    
    return {"message": "家属亲戚信息删除成功"}

@router.get("/employee/{employee_username}", response_model=List[FamilyMemberResponse])
def get_family_members_by_employee(
    employee_username: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定证券从业人员的所有家属亲戚
    """
    family_members = db.query(FamilyMember).filter(
        FamilyMember.employee_username == employee_username
    ).all()
    
    return family_members

@router.get("/stats/overview", response_model=FamilyMemberStatsResponse)
def get_family_member_stats(
    employee_username: Optional[str] = Query(None, description="证券从业人员用户名"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取家属亲戚统计信息
    """
    query = db.query(FamilyMember)
    
    if employee_username:
        query = query.filter(FamilyMember.employee_username == employee_username)
    
    # 总数统计
    total_members = query.count()
    
    # 按关系类型统计
    relationship_stats = db.query(
        FamilyMember.relationship,
        func.count(FamilyMember.id).label('count')
    )
    if employee_username:
        relationship_stats = relationship_stats.filter(
            FamilyMember.employee_username == employee_username
        )
    relationship_stats = relationship_stats.group_by(FamilyMember.relationship).all()
    by_relationship = {item.relationship: item.count for item in relationship_stats}
    
    # 按员工统计
    employee_stats = db.query(
        FamilyMember.employee_username,
        func.count(FamilyMember.id).label('count')
    )
    if employee_username:
        employee_stats = employee_stats.filter(
            FamilyMember.employee_username == employee_username
        )
    employee_stats = employee_stats.group_by(FamilyMember.employee_username).all()
    by_employee = {item.employee_username: item.count for item in employee_stats}
    
    return FamilyMemberStatsResponse(
        total_members=total_members,
        by_relationship=by_relationship,
        by_employee=by_employee
    )