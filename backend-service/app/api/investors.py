from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.investor import (
    Investor,
    InvestorCreate,
    InvestorUpdate,
    InvestorResponse,
    InvestorListResponse,
    InvestorStatsResponse
)
from app.core.security import get_current_user
from app.models.user import User
from sqlalchemy import and_, or_
import math

router = APIRouter(prefix="/investors", tags=["investors"])

@router.post("/", response_model=InvestorResponse)
def create_investor(
    investor: InvestorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建投资人"""
    # 检查身份证号是否已存在
    existing_investor = db.query(Investor).filter(Investor.id_number == investor.id_number).first()
    if existing_investor:
        raise HTTPException(status_code=400, detail="该身份证号已存在")
    
    db_investor = Investor(**investor.dict(), user_id=current_user.id)
    db.add(db_investor)
    db.commit()
    db.refresh(db_investor)
    return db_investor

@router.get("/", response_model=InvestorListResponse)
def get_investors(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    relationship: Optional[str] = Query(None, description="关系筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取投资人列表"""
    query = db.query(Investor).filter(Investor.user_id == current_user.id)
    
    # 搜索过滤
    if search:
        search_filter = or_(
            Investor.name.contains(search),
            Investor.id_number.contains(search),
            Investor.phone.contains(search)
        )
        query = query.filter(search_filter)
    
    # 关系过滤
    if relationship:
        query = query.filter(Investor.relationship == relationship)
    
    # 计算总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    # 计算总页数
    pages = math.ceil(total / size) if total > 0 else 1
    
    return InvestorListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{investor_id}", response_model=InvestorResponse)
def get_investor(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个投资人"""
    investor = db.query(Investor).filter(
        and_(Investor.id == investor_id, Investor.user_id == current_user.id)
    ).first()
    if not investor:
        raise HTTPException(status_code=404, detail="投资人不存在")
    return investor

@router.put("/{investor_id}", response_model=InvestorResponse)
def update_investor(
    investor_id: int,
    investor_update: InvestorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新投资人"""
    investor = db.query(Investor).filter(
        and_(Investor.id == investor_id, Investor.user_id == current_user.id)
    ).first()
    if not investor:
        raise HTTPException(status_code=404, detail="投资人不存在")
    
    # 如果更新身份证号，检查是否重复
    if investor_update.id_number and investor_update.id_number != investor.id_number:
        existing_investor = db.query(Investor).filter(
            and_(Investor.id_number == investor_update.id_number, Investor.id != investor_id)
        ).first()
        if existing_investor:
            raise HTTPException(status_code=400, detail="该身份证号已存在")
    
    # 更新字段
    update_data = investor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(investor, field, value)
    
    db.commit()
    db.refresh(investor)
    return investor

@router.delete("/{investor_id}")
def delete_investor(
    investor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除投资人"""
    investor = db.query(Investor).filter(
        and_(Investor.id == investor_id, Investor.user_id == current_user.id)
    ).first()
    if not investor:
        raise HTTPException(status_code=404, detail="投资人不存在")
    
    db.delete(investor)
    db.commit()
    return {"message": "投资人删除成功"}

@router.get("/stats/overview", response_model=InvestorStatsResponse)
def get_investor_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取投资人统计信息"""
    # 总投资人数
    total_investors = db.query(Investor).filter(Investor.user_id == current_user.id).count()
    
    # 按关系统计
    relationship_stats = db.query(
        Investor.relationship,
        db.func.count(Investor.id).label('count')
    ).filter(Investor.user_id == current_user.id).group_by(Investor.relationship).all()
    
    by_relationship = {stat.relationship: stat.count for stat in relationship_stats}
    
    return InvestorStatsResponse(
        total_investors=total_investors,
        by_relationship=by_relationship,
        by_user={current_user.username: total_investors}
    )