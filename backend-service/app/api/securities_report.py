from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, desc
from typing import List, Optional
from datetime import datetime
from app.core.database import get_db
from app.models.securities_report import (
    SecuritiesReport, 
    SecuritiesReportCreate, 
    SecuritiesReportUpdate, 
    SecuritiesReportResponse,
    SecuritiesReportWithFamilyResponse,
    SecuritiesReportListResponse,
    SecuritiesReportStatsResponse
)
from app.models.family_member import FamilyMember
from app.core.security import get_current_user
from app.models.user import User
import math

router = APIRouter()

@router.post("/", response_model=SecuritiesReportResponse)
def create_securities_report(
    report: SecuritiesReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建证券填报记录
    """
    # 检查家属亲戚是否存在
    family_member = db.query(FamilyMember).filter(
        FamilyMember.id == report.family_member_id
    ).first()
    if not family_member:
        raise HTTPException(status_code=404, detail="家属亲戚信息不存在")
    
    # 创建证券填报记录
    db_report = SecuritiesReport(**report.dict())
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    
    return db_report

@router.get("/", response_model=SecuritiesReportListResponse)
def get_securities_reports(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    family_member_id: Optional[int] = Query(None, description="家属亲戚ID"),
    employee_username: Optional[str] = Query(None, description="证券从业人员用户名"),
    securities_type: Optional[str] = Query(None, description="证券类型"),
    transaction_type: Optional[str] = Query(None, description="交易类型"),
    report_period: Optional[str] = Query(None, description="填报期间"),
    is_submitted: Optional[bool] = Query(None, description="是否已提交"),
    is_reviewed: Optional[bool] = Query(None, description="是否已审核"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取证券填报列表
    """
    query = db.query(SecuritiesReport).options(joinedload(SecuritiesReport.family_member))
    
    # 应用过滤条件
    if family_member_id:
        query = query.filter(SecuritiesReport.family_member_id == family_member_id)
    if employee_username:
        query = query.join(FamilyMember).filter(
            FamilyMember.employee_username == employee_username
        )
    if securities_type:
        query = query.filter(SecuritiesReport.securities_type == securities_type)
    if transaction_type:
        query = query.filter(SecuritiesReport.transaction_type == transaction_type)
    if report_period:
        query = query.filter(SecuritiesReport.report_period == report_period)
    if is_submitted is not None:
        query = query.filter(SecuritiesReport.is_submitted == is_submitted)
    if is_reviewed is not None:
        query = query.filter(SecuritiesReport.is_reviewed == is_reviewed)
    
    # 按创建时间倒序排列
    query = query.order_by(desc(SecuritiesReport.created_at))
    
    # 获取总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * size
    reports = query.offset(offset).limit(size).all()
    
    # 构建响应数据
    items = []
    for report in reports:
        item_data = SecuritiesReportResponse.from_orm(report).dict()
        item_data.update({
            'family_member_name': report.family_member.name,
            'family_member_relationship': report.family_member.relationship,
            'employee_username': report.family_member.employee_username
        })
        items.append(SecuritiesReportWithFamilyResponse(**item_data))
    
    # 计算总页数
    pages = math.ceil(total / size)
    
    return SecuritiesReportListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages
    )

@router.get("/{report_id}", response_model=SecuritiesReportResponse)
def get_securities_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取证券填报详情
    """
    report = db.query(SecuritiesReport).filter(
        SecuritiesReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="证券填报记录不存在")
    
    return report

@router.put("/{report_id}", response_model=SecuritiesReportResponse)
def update_securities_report(
    report_id: int,
    report_update: SecuritiesReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新证券填报记录
    """
    report = db.query(SecuritiesReport).filter(
        SecuritiesReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="证券填报记录不存在")
    
    # 如果已提交，只允许管理员修改
    if report.is_submitted and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="已提交的记录只能由管理员修改")
    
    # 更新字段
    update_data = report_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)
    
    # 如果提交状态发生变化，更新提交时间
    if 'is_submitted' in update_data and update_data['is_submitted']:
        report.submit_date = datetime.utcnow()
    
    db.commit()
    db.refresh(report)
    
    return report

@router.delete("/{report_id}")
def delete_securities_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除证券填报记录
    """
    report = db.query(SecuritiesReport).filter(
        SecuritiesReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="证券填报记录不存在")
    
    # 如果已提交，只允许管理员删除
    if report.is_submitted and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="已提交的记录只能由管理员删除")
    
    db.delete(report)
    db.commit()
    
    return {"message": "证券填报记录删除成功"}

@router.post("/{report_id}/submit")
def submit_securities_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    提交证券填报记录
    """
    report = db.query(SecuritiesReport).filter(
        SecuritiesReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="证券填报记录不存在")
    
    if report.is_submitted:
        raise HTTPException(status_code=400, detail="该记录已经提交")
    
    report.is_submitted = True
    report.submit_date = datetime.utcnow()
    
    db.commit()
    db.refresh(report)
    
    return {"message": "证券填报记录提交成功"}

@router.post("/{report_id}/review")
def review_securities_report(
    report_id: int,
    review_status: str,
    review_comments: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    审核证券填报记录（仅管理员）
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="只有管理员可以审核")
    
    report = db.query(SecuritiesReport).filter(
        SecuritiesReport.id == report_id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="证券填报记录不存在")
    
    if not report.is_submitted:
        raise HTTPException(status_code=400, detail="只能审核已提交的记录")
    
    report.is_reviewed = True
    report.review_date = datetime.utcnow()
    report.reviewer = current_user.username
    report.review_status = review_status
    report.review_comments = review_comments
    
    db.commit()
    db.refresh(report)
    
    return {"message": "证券填报记录审核完成"}

@router.get("/family/{family_member_id}", response_model=List[SecuritiesReportResponse])
def get_reports_by_family_member(
    family_member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取指定家属亲戚的所有证券填报记录
    """
    reports = db.query(SecuritiesReport).filter(
        SecuritiesReport.family_member_id == family_member_id
    ).order_by(desc(SecuritiesReport.created_at)).all()
    
    return reports

@router.get("/stats/overview", response_model=SecuritiesReportStatsResponse)
def get_securities_report_stats(
    employee_username: Optional[str] = Query(None, description="证券从业人员用户名"),
    report_period: Optional[str] = Query(None, description="填报期间"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取证券填报统计信息
    """
    query = db.query(SecuritiesReport)
    
    if employee_username:
        query = query.join(FamilyMember).filter(
            FamilyMember.employee_username == employee_username
        )
    if report_period:
        query = query.filter(SecuritiesReport.report_period == report_period)
    
    # 基础统计
    total_reports = query.count()
    submitted_reports = query.filter(SecuritiesReport.is_submitted == True).count()
    reviewed_reports = query.filter(SecuritiesReport.is_reviewed == True).count()
    pending_reports = total_reports - submitted_reports
    
    # 按证券类型统计
    securities_type_stats = query.with_entities(
        SecuritiesReport.securities_type,
        func.count(SecuritiesReport.id).label('count')
    ).group_by(SecuritiesReport.securities_type).all()
    by_securities_type = {item.securities_type: item.count for item in securities_type_stats}
    
    # 按交易类型统计
    transaction_type_stats = query.with_entities(
        SecuritiesReport.transaction_type,
        func.count(SecuritiesReport.id).label('count')
    ).group_by(SecuritiesReport.transaction_type).all()
    by_transaction_type = {item.transaction_type: item.count for item in transaction_type_stats}
    
    # 按期间统计
    period_stats = query.with_entities(
        SecuritiesReport.report_period,
        func.count(SecuritiesReport.id).label('count')
    ).group_by(SecuritiesReport.report_period).all()
    by_period = {item.report_period: item.count for item in period_stats}
    
    # 金额统计
    amount_stats = query.with_entities(
        func.sum(SecuritiesReport.amount).label('total_amount'),
        func.sum(SecuritiesReport.market_value).label('total_market_value')
    ).first()
    
    total_amount = float(amount_stats.total_amount or 0)
    total_market_value = float(amount_stats.total_market_value or 0)
    
    return SecuritiesReportStatsResponse(
        total_reports=total_reports,
        submitted_reports=submitted_reports,
        reviewed_reports=reviewed_reports,
        pending_reports=pending_reports,
        by_securities_type=by_securities_type,
        by_transaction_type=by_transaction_type,
        by_period=by_period,
        total_amount=total_amount,
        total_market_value=total_market_value
    )