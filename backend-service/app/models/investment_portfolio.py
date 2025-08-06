from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.core.database import Base

class InvestmentPortfolio(Base):
    """投资情况表 - 存储投资人的投资组合信息"""
    __tablename__ = "investment_portfolios"
    
    id = Column(Integer, primary_key=True, index=True, comment="主键ID")
    investor_id = Column(Integer, ForeignKey("investors.id"), nullable=False, comment="投资人ID")
    quarter = Column(String(10), nullable=False, comment="季度，格式：2024Q1")
    year = Column(Integer, nullable=False, comment="年份")
    
    # 投资组合数据 - 可以存储为JSON格式
    portfolio_data = Column(Text, nullable=True, comment="投资组合数据（JSON格式）")
    
    # 或者按列存储主要字段
    stock_code = Column(String(20), nullable=True, comment="股票代码")
    stock_name = Column(String(100), nullable=True, comment="股票名称")
    holding_quantity = Column(Float, nullable=True, comment="持股数量")
    market_value = Column(Float, nullable=True, comment="市值")
    cost_price = Column(Float, nullable=True, comment="成本价")
    current_price = Column(Float, nullable=True, comment="当前价")
    profit_loss = Column(Float, nullable=True, comment="盈亏金额")
    profit_loss_ratio = Column(Float, nullable=True, comment="盈亏比例")
    
    # 文件信息
    original_filename = Column(String(255), nullable=True, comment="原始文件名")
    file_path = Column(String(500), nullable=True, comment="文件存储路径")
    file_size = Column(Integer, nullable=True, comment="文件大小")
    file_hash = Column(String(64), nullable=True, comment="文件哈希值")
    
    # 状态和审核
    status = Column(String(20), default="pending", comment="状态：pending/approved/rejected")
    is_editable = Column(Boolean, default=True, comment="是否可编辑")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    investor = relationship("Investor", back_populates="portfolios")

# Pydantic 模型
class InvestmentPortfolioBase(BaseModel):
    investor_id: int
    quarter: str
    year: int
    portfolio_data: Optional[str] = None
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    holding_quantity: Optional[float] = None
    market_value: Optional[float] = None
    cost_price: Optional[float] = None
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_ratio: Optional[float] = None
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    status: Optional[str] = "pending"
    is_editable: Optional[bool] = True
    notes: Optional[str] = None

class InvestmentPortfolioCreate(InvestmentPortfolioBase):
    pass

class InvestmentPortfolioUpdate(BaseModel):
    quarter: Optional[str] = None
    year: Optional[int] = None
    portfolio_data: Optional[str] = None
    stock_code: Optional[str] = None
    stock_name: Optional[str] = None
    holding_quantity: Optional[float] = None
    market_value: Optional[float] = None
    cost_price: Optional[float] = None
    current_price: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_ratio: Optional[float] = None
    original_filename: Optional[str] = None
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_hash: Optional[str] = None
    status: Optional[str] = None
    is_editable: Optional[bool] = None
    notes: Optional[str] = None

class InvestmentPortfolioResponse(InvestmentPortfolioBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InvestmentPortfolioListResponse(BaseModel):
    portfolios: List[InvestmentPortfolioResponse]
    total: int
    page: int
    size: int
    pages: int

class InvestmentPortfolioStatsResponse(BaseModel):
    total_portfolios: int
    portfolios_by_quarter: Dict[str, int]
    portfolios_by_status: Dict[str, int]
    total_market_value: float
    total_profit_loss: float