from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.user import Base

# 证券类型
class SecuritiesType:
    STOCK = "股票"
    BOND = "债券"
    FUND = "基金"
    FUTURES = "期货"
    OPTIONS = "期权"
    WARRANT = "权证"
    ETF = "ETF"
    OTHER = "其他"

# 交易类型
class TransactionType:
    BUY = "买入"
    SELL = "卖出"
    TRANSFER_IN = "转入"
    TRANSFER_OUT = "转出"
    DIVIDEND = "分红"
    SPLIT = "拆股"
    MERGE = "并股"
    OTHER = "其他"

# 数据库模型
class SecuritiesReport(Base):
    __tablename__ = "securities_reports"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的家属亲戚ID
    family_member_id = Column(Integer, ForeignKey("family_members.id"), nullable=False, index=True, comment="家属亲戚ID")
    
    # 证券基本信息
    securities_code = Column(String(20), nullable=False, comment="证券代码")
    securities_name = Column(String(100), nullable=False, comment="证券名称")
    securities_type = Column(String(20), nullable=False, comment="证券类型")
    
    # 交易信息
    transaction_type = Column(String(20), nullable=False, comment="交易类型")
    transaction_date = Column(DateTime, nullable=False, comment="交易日期")
    quantity = Column(Numeric(15, 4), nullable=False, comment="数量")
    price = Column(Numeric(15, 4), nullable=False, comment="价格")
    amount = Column(Numeric(15, 2), nullable=False, comment="金额")
    
    # 账户信息
    account_number = Column(String(50), nullable=False, comment="证券账户号")
    broker_name = Column(String(100), nullable=False, comment="券商名称")
    
    # 持仓信息
    holding_quantity = Column(Numeric(15, 4), comment="持仓数量")
    market_value = Column(Numeric(15, 2), comment="市值")
    
    # 填报信息
    report_period = Column(String(20), nullable=False, comment="填报期间")
    report_date = Column(DateTime, nullable=False, default=datetime.utcnow, comment="填报日期")
    is_submitted = Column(Boolean, default=False, comment="是否已提交")
    submit_date = Column(DateTime, comment="提交日期")
    
    # 审核信息
    is_reviewed = Column(Boolean, default=False, comment="是否已审核")
    review_date = Column(DateTime, comment="审核日期")
    reviewer = Column(String(50), comment="审核人")
    review_status = Column(String(20), comment="审核状态")
    review_comments = Column(Text, comment="审核意见")
    
    # 附件信息
    attachment_path = Column(String(500), comment="附件路径")
    attachment_name = Column(String(200), comment="附件名称")
    
    # 备注信息
    remarks = Column(Text, comment="备注")
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系（稍后添加）
    # family_member = relationship("FamilyMember", back_populates="securities_reports")

# Pydantic 模型
class SecuritiesReportBase(BaseModel):
    family_member_id: int = Field(..., description="家属亲戚ID")
    securities_code: str = Field(..., min_length=1, max_length=20, description="证券代码")
    securities_name: str = Field(..., min_length=1, max_length=100, description="证券名称")
    securities_type: str = Field(..., description="证券类型")
    transaction_type: str = Field(..., description="交易类型")
    transaction_date: datetime = Field(..., description="交易日期")
    quantity: float = Field(..., gt=0, description="数量")
    price: float = Field(..., gt=0, description="价格")
    amount: float = Field(..., gt=0, description="金额")
    account_number: str = Field(..., min_length=1, max_length=50, description="证券账户号")
    broker_name: str = Field(..., min_length=1, max_length=100, description="券商名称")
    holding_quantity: Optional[float] = Field(None, description="持仓数量")
    market_value: Optional[float] = Field(None, description="市值")
    report_period: str = Field(..., min_length=1, max_length=20, description="填报期间")
    attachment_path: Optional[str] = Field(None, max_length=500, description="附件路径")
    attachment_name: Optional[str] = Field(None, max_length=200, description="附件名称")
    remarks: Optional[str] = Field(None, description="备注")

class SecuritiesReportCreate(SecuritiesReportBase):
    pass

class SecuritiesReportUpdate(BaseModel):
    securities_code: Optional[str] = Field(None, min_length=1, max_length=20, description="证券代码")
    securities_name: Optional[str] = Field(None, min_length=1, max_length=100, description="证券名称")
    securities_type: Optional[str] = Field(None, description="证券类型")
    transaction_type: Optional[str] = Field(None, description="交易类型")
    transaction_date: Optional[datetime] = Field(None, description="交易日期")
    quantity: Optional[float] = Field(None, gt=0, description="数量")
    price: Optional[float] = Field(None, gt=0, description="价格")
    amount: Optional[float] = Field(None, gt=0, description="金额")
    account_number: Optional[str] = Field(None, min_length=1, max_length=50, description="证券账户号")
    broker_name: Optional[str] = Field(None, min_length=1, max_length=100, description="券商名称")
    holding_quantity: Optional[float] = Field(None, description="持仓数量")
    market_value: Optional[float] = Field(None, description="市值")
    report_period: Optional[str] = Field(None, min_length=1, max_length=20, description="填报期间")
    attachment_path: Optional[str] = Field(None, max_length=500, description="附件路径")
    attachment_name: Optional[str] = Field(None, max_length=200, description="附件名称")
    remarks: Optional[str] = Field(None, description="备注")
    is_submitted: Optional[bool] = Field(None, description="是否已提交")
    review_status: Optional[str] = Field(None, description="审核状态")
    review_comments: Optional[str] = Field(None, description="审核意见")

class SecuritiesReportResponse(SecuritiesReportBase):
    id: int
    report_date: datetime
    is_submitted: bool
    submit_date: Optional[datetime]
    is_reviewed: bool
    review_date: Optional[datetime]
    reviewer: Optional[str]
    review_status: Optional[str]
    review_comments: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class SecuritiesReportWithFamilyResponse(SecuritiesReportResponse):
    family_member_name: str
    family_member_relationship: str
    employee_username: str

class SecuritiesReportListResponse(BaseModel):
    items: List[SecuritiesReportWithFamilyResponse]
    total: int
    page: int
    size: int
    pages: int

class SecuritiesReportStatsResponse(BaseModel):
    total_reports: int
    submitted_reports: int
    reviewed_reports: int
    pending_reports: int
    by_securities_type: dict
    by_transaction_type: dict
    by_period: dict
    total_amount: float
    total_market_value: float