from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
import json
import hashlib
import os
from pathlib import Path

from app.core.database import get_db
from app.models.investment_portfolio import (
    InvestmentPortfolio,
    InvestmentPortfolioCreate,
    InvestmentPortfolioUpdate,
    InvestmentPortfolioResponse,
    InvestmentPortfolioListResponse,
    InvestmentPortfolioStatsResponse
)
from app.models.investor import Investor
from app.models.user import User
from app.core.security import get_current_active_user

router = APIRouter(prefix="/v1/investment-portfolios", tags=["investment-portfolios"])

# 文件上传目录
UPLOAD_DIR = Path("data/portfolios")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def calculate_file_hash(file_content: bytes) -> str:
    """计算文件哈希值"""
    return hashlib.sha256(file_content).hexdigest()

@router.post("/", response_model=InvestmentPortfolioResponse)
async def create_portfolio(
    portfolio_data: InvestmentPortfolioCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """创建投资组合记录"""
    
    # 检查投资人是否存在
    investor = db.query(Investor).filter(
        Investor.id_number == portfolio_data.investor_id_number
    ).first()
    
    if not investor:
        raise HTTPException(status_code=404, detail="投资人不存在")
    
    # 检查是否已存在相同季度的记录
    existing = db.query(InvestmentPortfolio).filter(
        and_(
            InvestmentPortfolio.investor_id_number == portfolio_data.investor_id_number,
            InvestmentPortfolio.quarter == portfolio_data.quarter,
            InvestmentPortfolio.year == portfolio_data.year
        )
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="该投资人在此季度已有投资记录")
    
    # 创建投资组合记录
    db_portfolio = InvestmentPortfolio(**portfolio_data.dict())
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    
    return db_portfolio

@router.post("/upload/{investor_id_number}")
async def upload_portfolio_file(
    investor_id_number: str,
    quarter: str = Query(..., description="季度，格式：2024Q1"),
    year: int = Query(..., description="年份"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """上传投资组合文件"""
    
    # 检查投资人是否存在
    investor = db.query(Investor).filter(
        Investor.id_number == investor_id_number
    ).first()
    
    if not investor:
        raise HTTPException(status_code=404, detail="投资人不存在")
    
    # 检查文件类型
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(status_code=400, detail="只支持Excel和CSV文件")
    
    # 读取文件内容
    file_content = await file.read()
    file_hash = calculate_file_hash(file_content)
    
    # 保存文件
    file_path = UPLOAD_DIR / f"{investor_id_number}_{quarter}_{file.filename}"
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # 检查是否已存在记录
    existing = db.query(InvestmentPortfolio).filter(
        and_(
            InvestmentPortfolio.investor_id_number == investor_id_number,
            InvestmentPortfolio.quarter == quarter,
            InvestmentPortfolio.year == year
        )
    ).first()
    
    if existing:
        # 更新现有记录
        existing.original_filename = file.filename
        existing.file_path = str(file_path)
        existing.file_size = len(file_content)
        existing.file_hash = file_hash
        existing.status = "pending"
        db.commit()
        db.refresh(existing)
        return existing
    else:
        # 创建新记录
        db_portfolio = InvestmentPortfolio(
            investor_id_number=investor_id_number,
            quarter=quarter,
            year=year,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size=len(file_content),
            file_hash=file_hash,
            status="pending"
        )
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio

@router.get("/", response_model=InvestmentPortfolioListResponse)
def get_portfolios(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    investor_id_number: Optional[str] = Query(None, description="投资人身份证号"),
    quarter: Optional[str] = Query(None, description="季度"),
    year: Optional[int] = Query(None, description="年份"),
    status: Optional[str] = Query(None, description="状态"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取投资组合列表"""
    
    query = db.query(InvestmentPortfolio)
    
    # 搜索过滤
    if search:
        query = query.filter(
            or_(
                InvestmentPortfolio.investor_id_number.contains(search),
                InvestmentPortfolio.stock_name.contains(search),
                InvestmentPortfolio.stock_code.contains(search)
            )
        )
    
    # 其他过滤条件
    if investor_id_number:
        query = query.filter(InvestmentPortfolio.investor_id_number == investor_id_number)
    
    if quarter:
        query = query.filter(InvestmentPortfolio.quarter == quarter)
    
    if year:
        query = query.filter(InvestmentPortfolio.year == year)
    
    if status:
        query = query.filter(InvestmentPortfolio.status == status)
    
    # 计算总数
    total = query.count()
    
    # 分页
    portfolios = query.offset(skip).limit(limit).all()
    
    return InvestmentPortfolioListResponse(
        portfolios=portfolios,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/{portfolio_id}", response_model=InvestmentPortfolioResponse)
def get_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取单个投资组合"""
    
    portfolio = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.id == portfolio_id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    return portfolio

@router.put("/{portfolio_id}", response_model=InvestmentPortfolioResponse)
def update_portfolio(
    portfolio_id: int,
    portfolio_data: InvestmentPortfolioUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新投资组合"""
    
    portfolio = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.id == portfolio_id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 检查是否可编辑
    if not portfolio.is_editable:
        raise HTTPException(status_code=400, detail="该投资组合不可编辑")
    
    # 更新字段
    update_data = portfolio_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(portfolio, field, value)
    
    db.commit()
    db.refresh(portfolio)
    
    return portfolio

@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """删除投资组合"""
    
    portfolio = db.query(InvestmentPortfolio).filter(
        InvestmentPortfolio.id == portfolio_id
    ).first()
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="投资组合不存在")
    
    # 删除关联文件
    if portfolio.file_path and os.path.exists(portfolio.file_path):
        os.remove(portfolio.file_path)
    
    db.delete(portfolio)
    db.commit()
    
    return {"message": "投资组合删除成功"}

@router.get("/stats/overview", response_model=InvestmentPortfolioStatsResponse)
def get_portfolio_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取投资组合统计信息"""
    
    # 总投资组合数
    total_portfolios = db.query(InvestmentPortfolio).count()
    
    # 按季度统计
    quarter_stats = db.query(
        InvestmentPortfolio.quarter,
        func.count(InvestmentPortfolio.id)
    ).group_by(InvestmentPortfolio.quarter).all()
    
    portfolios_by_quarter = {quarter: count for quarter, count in quarter_stats}
    
    # 按状态统计
    status_stats = db.query(
        InvestmentPortfolio.status,
        func.count(InvestmentPortfolio.id)
    ).group_by(InvestmentPortfolio.status).all()
    
    portfolios_by_status = {status: count for status, count in status_stats}
    
    # 总市值和盈亏
    market_value_sum = db.query(func.sum(InvestmentPortfolio.market_value)).scalar() or 0
    profit_loss_sum = db.query(func.sum(InvestmentPortfolio.profit_loss)).scalar() or 0
    
    return InvestmentPortfolioStatsResponse(
        total_portfolios=total_portfolios,
        portfolios_by_quarter=portfolios_by_quarter,
        portfolios_by_status=portfolios_by_status,
        total_market_value=float(market_value_sum),
        total_profit_loss=float(profit_loss_sum)
    )