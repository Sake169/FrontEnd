from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.models.investment_record import (
    InvestmentRecord,
    InvestmentRecordCreate,
    InvestmentRecordUpdate,
    InvestmentRecordResponse,
    InvestmentRecordListResponse
)
from app.core.security import get_current_user
from app.models.user import User
from sqlalchemy import and_, or_
import math

router = APIRouter(prefix="/investment-records", tags=["investment-records"])

@router.post("/", response_model=InvestmentRecordResponse)
def create_investment_record(
    record: InvestmentRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建投资记录"""
    db_record = InvestmentRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@router.get("/", response_model=InvestmentRecordListResponse)
def get_investment_records(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    investor_id_number: Optional[str] = Query(None, description="投资人身份证号"),
    securities_code: Optional[str] = Query(None, description="证券代码"),
    report_period: Optional[str] = Query(None, description="报告期间"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取投资记录列表"""
    query = db.query(InvestmentRecord)
    
    # 添加过滤条件
    if investor_id_number:
        query = query.filter(InvestmentRecord.investor_id_number == investor_id_number)
    if securities_code:
        query = query.filter(InvestmentRecord.securities_code.like(f"%{securities_code}%"))
    if report_period:
        query = query.filter(InvestmentRecord.report_period == report_period)
    
    # 计算总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * size
    items = query.offset(offset).limit(size).all()
    
    # 计算总页数
    pages = math.ceil(total / size) if total > 0 else 1
    
    return InvestmentRecordListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{record_id}", response_model=InvestmentRecordResponse)
def get_investment_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个投资记录"""
    record = db.query(InvestmentRecord).filter(InvestmentRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="投资记录不存在")
    return record

@router.put("/{record_id}", response_model=InvestmentRecordResponse)
def update_investment_record(
    record_id: int,
    record_update: InvestmentRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新投资记录"""
    record = db.query(InvestmentRecord).filter(InvestmentRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="投资记录不存在")
    
    # 更新字段
    update_data = record_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    
    db.commit()
    db.refresh(record)
    return record

@router.delete("/{record_id}")
def delete_investment_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除投资记录"""
    record = db.query(InvestmentRecord).filter(InvestmentRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="投资记录不存在")
    
    db.delete(record)
    db.commit()
    return {"message": "投资记录删除成功"}

@router.get("/by-investor/{investor_id_number}", response_model=List[InvestmentRecordResponse])
def get_records_by_investor(
    investor_id_number: str,
    report_period: Optional[str] = Query(None, description="报告期间"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """根据投资人身份证号获取投资记录"""
    query = db.query(InvestmentRecord).filter(
        InvestmentRecord.investor_id_number == investor_id_number
    )
    
    if report_period:
        query = query.filter(InvestmentRecord.report_period == report_period)
    
    return query.all()

@router.post("/batch", response_model=List[InvestmentRecordResponse])
def create_investment_records_batch(
    records: List[InvestmentRecordCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量创建投资记录"""
    db_records = []
    for record in records:
        db_record = InvestmentRecord(**record.dict())
        db.add(db_record)
        db_records.append(db_record)
    
    db.commit()
    for record in db_records:
        db.refresh(record)
    
    return db_records

@router.delete("/by-investor/{investor_id_number}")
def delete_records_by_investor(
    investor_id_number: str,
    report_period: Optional[str] = Query(None, description="报告期间"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除指定投资人的投资记录"""
    query = db.query(InvestmentRecord).filter(
        InvestmentRecord.investor_id_number == investor_id_number
    )
    
    if report_period:
        query = query.filter(InvestmentRecord.report_period == report_period)
    
    deleted_count = query.count()
    query.delete()
    db.commit()
    
    return {"message": f"删除了 {deleted_count} 条投资记录"}