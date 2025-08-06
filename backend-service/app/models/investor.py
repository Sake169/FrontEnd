from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from app.core.database import Base

# 证件类型
ID_TYPES = [
    "身份证",
    "护照",
    "港澳通行证",
    "台胞证",
    "其他"
]

# 关系类型
RELATIONSHIP_TYPES = [
    "配偶",
    "父母",
    "子女",
    "兄弟姐妹",
    "其他亲属",
    "本人"
]

# 数据库模型
class Investor(Base):
    __tablename__ = "investors"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的用户ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="关联用户ID")
    
    # 投资人基本信息
    name = Column(String(100), nullable=False, comment="姓名")
    relation_type = Column(String(50), nullable=False, default="配偶", comment="与证券从业人员的关系")
    
    # 证件信息
    id_type = Column(String(20), nullable=False, default="身份证", comment="证件类型")
    id_number = Column(String(50), nullable=False, unique=True, index=True, comment="证件号码")
    
    # 联系方式
    phone = Column(String(20), comment="手机号码")
    email = Column(String(100), comment="邮箱地址")
    address = Column(Text, comment="联系地址")
    
    # 网络信息
    qq = Column(String(20), comment="QQ号")
    wechat = Column(String(50), comment="微信号")
    weibo = Column(String(100), comment="微博账号")
    
    # 账号信息
    bank_account = Column(String(50), comment="银行账号")
    bank_name = Column(String(100), comment="开户银行")
    
    # 备注信息
    remarks = Column(Text, comment="备注")
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 关联关系
    user = relationship("User", back_populates="investors")
    portfolios = relationship("InvestmentPortfolio", back_populates="investor")

# Pydantic 模型
class InvestorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    relation_type: str = Field(..., description="与证券从业人员的关系")
    id_type: str = Field(default="身份证", description="证件类型")
    id_number: str = Field(..., min_length=1, max_length=50, description="证件号码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    email: Optional[str] = Field(None, max_length=100, description="邮箱地址")
    address: Optional[str] = Field(None, description="联系地址")
    qq: Optional[str] = Field(None, max_length=20, description="QQ号")
    wechat: Optional[str] = Field(None, max_length=50, description="微信号")
    weibo: Optional[str] = Field(None, max_length=100, description="微博账号")
    bank_account: Optional[str] = Field(None, max_length=50, description="银行账号")
    bank_name: Optional[str] = Field(None, max_length=100, description="开户银行")
    remarks: Optional[str] = Field(None, description="备注")

class InvestorCreate(InvestorBase):
    pass

class InvestorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="姓名")
    relation_type: Optional[str] = Field(None, description="与证券从业人员的关系")
    id_type: Optional[str] = Field(None, description="证件类型")
    id_number: Optional[str] = Field(None, min_length=1, max_length=50, description="证件号码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    email: Optional[str] = Field(None, max_length=100, description="邮箱地址")
    address: Optional[str] = Field(None, description="联系地址")
    qq: Optional[str] = Field(None, max_length=20, description="QQ号")
    wechat: Optional[str] = Field(None, max_length=50, description="微信号")
    weibo: Optional[str] = Field(None, max_length=100, description="微博账号")
    bank_account: Optional[str] = Field(None, max_length=50, description="银行账号")
    bank_name: Optional[str] = Field(None, max_length=100, description="开户银行")
    remarks: Optional[str] = Field(None, description="备注")

class InvestorResponse(InvestorBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class InvestorListResponse(BaseModel):
    items: List[InvestorResponse]
    total: int
    page: int
    size: int
    pages: int

class InvestorStatsResponse(BaseModel):
    total_investors: int
    by_relationship: dict
    by_user: dict