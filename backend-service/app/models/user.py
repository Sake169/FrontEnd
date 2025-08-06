from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum
from app.core.database import Base

class UserRole(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"  # 管理员
    USER = "user"   # 普通用户

class User(Base):
    """用户数据模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    hashed_password = Column(String(255), nullable=False, comment="加密密码")
    full_name = Column(String(100), nullable=True, comment="真实姓名")
    role = Column(String(20), default=UserRole.USER, nullable=False, comment="用户角色")
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    is_verified = Column(Boolean, default=False, nullable=False, comment="是否验证")
    phone = Column(String(20), nullable=True, comment="手机号")
    id_number = Column(String(50), nullable=True, comment="身份证号")
    department = Column(String(100), nullable=True, comment="部门")
    position = Column(String(100), nullable=True, comment="职位")
    avatar_url = Column(String(255), nullable=True, comment="头像URL")
    last_login = Column(DateTime, nullable=True, comment="最后登录时间")
    login_count = Column(Integer, default=0, comment="登录次数")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
    created_by = Column(Integer, nullable=True, comment="创建者ID")
    notes = Column(Text, nullable=True, comment="备注")
    
    # 关联关系 - 使用字符串引用避免循环导入
    investors = relationship("Investor", back_populates="user")

# Pydantic 模型用于API
class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    id_number: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    role: UserRole = UserRole.USER
    is_active: bool = True
    notes: Optional[str] = None

class UserCreate(UserBase):
    """创建用户模型"""
    password: str

class UserUpdate(BaseModel):
    """更新用户模型"""
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    id_number: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    notes: Optional[str] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_verified: bool
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    login_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str
    remember_me: bool = False

class Token(BaseModel):
    """令牌模型"""
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse

class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None

class PasswordChange(BaseModel):
    """密码修改模型"""
    old_password: str
    new_password: str

class PasswordReset(BaseModel):
    """密码重置模型"""
    email: str

class UserStats(BaseModel):
    """用户统计模型"""
    total_users: int
    active_users: int
    admin_users: int
    new_users_today: int
    new_users_this_week: int
    new_users_this_month: int