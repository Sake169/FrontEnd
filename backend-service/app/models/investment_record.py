from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Numeric, Date
from sqlalchemy.orm import relationship
from datetime import datetime, date
from pydantic import BaseModel, Field
from typing import Optional, List
from app.core.database import Base

# 数据库模型
class InvestmentRecord(Base):
    __tablename__ = "investment_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联投资人身份证号
    investor_id_number = Column(String(50), nullable=False, index=True, comment="投资人身份证号")
    
    # 证券信息
    securities_code = Column(String(20), comment="证券代码")
    securities_name = Column(String(100), comment="证券名称")
    securities_type = Column(String(50), comment="证券类型")
    
    # 交易信息
    transaction_type = Column(String(20), comment="交易类型")
    transaction_date = Column(Date, comment="交易日期")
    quantity = Column(Numeric(15, 4), comment="交易数量")
    price = Column(Numeric(15, 4), comment="交易价格")
    amount = Column(Numeric(15, 2), comment="交易金额")
    
    # 持仓信息
    holding_quantity = Column(Numeric(15, 4), comment="持仓数量")
    market_value = Column(Numeric(15, 2), comment="市值")
    
    # 报告期间
    report_period = Column(String(20), comment="报告期间")
    
    # 数据来源
    source_file = Column(String(255), comment="来源文件")
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")

# Pydantic 模型
class InvestmentRecordBase(BaseModel):
    investor_id_number: str = Field(..., description="投资人身份证号")
    securities_code: Optional[str] = Field(None, description="证券代码")
    securities_name: Optional[str] = Field(None, description="证券名称")
    securities_type: Optional[str] = Field(None, description="证券类型")
    transaction_type: Optional[str] = Field(None, description="交易类型")
    transaction_date: Optional[date] = Field(None, description="交易日期")
    quantity: Optional[float] = Field(None, description="交易数量")
    price: Optional[float] = Field(None, description="交易价格")
    amount: Optional[float] = Field(None, description="交易金额")
    holding_quantity: Optional[float] = Field(None, description="持仓数量")
    market_value: Optional[float] = Field(None, description="市值")
    report_period: Optional[str] = Field(None, description="报告期间")
    source_file: Optional[str] = Field(None, description="来源文件")

class InvestmentRecordCreate(InvestmentRecordBase):
    pass

class InvestmentRecordUpdate(BaseModel):
    securities_code: Optional[str] = Field(None, description="证券代码")
    securities_name: Optional[str] = Field(None, description="证券名称")
    securities_type: Optional[str] = Field(None, description="证券类型")
    transaction_type: Optional[str] = Field(None, description="交易类型")
    transaction_date: Optional[date] = Field(None, description="交易日期")
    quantity: Optional[float] = Field(None, description="交易数量")
    price: Optional[float] = Field(None, description="交易价格")
    amount: Optional[float] = Field(None, description="交易金额")
    holding_quantity: Optional[float] = Field(None, description="持仓数量")
    market_value: Optional[float] = Field(None, description="市值")
    report_period: Optional[str] = Field(None, description="报告期间")
    source_file: Optional[str] = Field(None, description="来源文件")

class InvestmentRecordResponse(InvestmentRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InvestmentRecordListResponse(BaseModel):
    items: List[InvestmentRecordResponse]
    total: int
    page: int
    size: int
    pages: int