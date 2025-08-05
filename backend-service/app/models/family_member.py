from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List
from app.models.user import Base

# 家属亲戚关系类型
class RelationshipType:
    SPOUSE = "配偶"
    CHILD = "子女"
    PARENT = "父母"
    SIBLING = "兄弟姐妹"
    GRANDPARENT = "祖父母/外祖父母"
    GRANDCHILD = "孙子女/外孙子女"
    UNCLE_AUNT = "叔伯姑舅姨"
    NEPHEW_NIECE = "侄子女/外甥女"
    COUSIN = "堂兄弟姐妹/表兄弟姐妹"
    IN_LAW = "姻亲"
    OTHER = "其他"

# 证件类型
class IDType:
    ID_CARD = "身份证"
    PASSPORT = "护照"
    MILITARY_ID = "军官证"
    OTHER = "其他"

# 数据库模型
class FamilyMember(Base):
    __tablename__ = "family_members"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 关联的证券从业人员用户名
    employee_username = Column(String(50), nullable=False, index=True, comment="证券从业人员用户名")
    
    # 家属基本信息
    name = Column(String(100), nullable=False, comment="姓名")
    relationship = Column(String(50), nullable=False, comment="与证券从业人员的关系")
    
    # 证件信息
    id_type = Column(String(20), nullable=False, default=IDType.ID_CARD, comment="证件类型")
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
    
    # 关联关系（稍后添加）
    # securities_reports = relationship("SecuritiesReport", back_populates="family_member")

# Pydantic 模型
class FamilyMemberBase(BaseModel):
    employee_username: str = Field(..., description="证券从业人员用户名")
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    relationship: str = Field(..., description="与证券从业人员的关系")
    id_type: str = Field(default=IDType.ID_CARD, description="证件类型")
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

class FamilyMemberCreate(FamilyMemberBase):
    pass

class FamilyMemberUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="姓名")
    relationship: Optional[str] = Field(None, description="与证券从业人员的关系")
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

class FamilyMemberResponse(FamilyMemberBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class FamilyMemberListResponse(BaseModel):
    items: List[FamilyMemberResponse]
    total: int
    page: int
    size: int
    pages: int

class FamilyMemberStatsResponse(BaseModel):
    total_members: int
    by_relationship: dict
    by_employee: dict