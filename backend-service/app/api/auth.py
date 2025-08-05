from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from app.core.database import get_db
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    require_admin,
    require_admin_or_self,
    get_password_hash,
    verify_password,
    check_password_strength,
    generate_random_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.user import (
    User,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    PasswordChange,
    PasswordReset,
    UserStats,
    UserRole
)

router = APIRouter(tags=["认证"])

@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    user_credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """用户登录接口"""
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 更新登录信息
    user.last_login = datetime.utcnow()
    user.login_count += 1
    db.commit()
    
    # 创建访问令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if user_credentials.remember_me:
        access_token_expires = timedelta(days=30)  # 记住我：30天
    
    access_token = create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role
        },
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds()),
        "user": UserResponse.from_orm(user)
    }

@router.post("/public-register", response_model=UserResponse, summary="公开注册新用户")
async def public_register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """公开注册新用户"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 检查密码强度
    password_check = check_password_strength(user_data.password)
    if not password_check["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"密码不符合要求: {', '.join(password_check['messages'])}"
        )
    
    # 创建新用户（公开注册默认为普通用户）
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name or user_data.username,
        phone=user_data.phone,
        department=user_data.department,
        position=user_data.position,
        role=UserRole.USER,  # 公开注册默认为普通用户
        is_active=True,  # 默认激活
        is_verified=True,  # 默认已验证
        notes="公开注册用户"
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)

@router.post("/register", response_model=UserResponse, summary="注册新用户")
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)  # 只有管理员可以注册新用户
):
    """注册新用户（仅管理员）"""
    # 检查用户名是否已存在
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )
    
    # 检查密码强度
    password_check = check_password_strength(user_data.password)
    if not password_check["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"密码不符合要求: {', '.join(password_check['messages'])}"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        department=user_data.department,
        position=user_data.position,
        role=user_data.role,
        is_active=user_data.is_active,
        is_verified=True,  # 管理员创建的用户默认已验证
        notes=user_data.notes,
        created_by=current_user.id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserResponse.from_orm(db_user)

@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """获取当前登录用户信息"""
    return UserResponse.from_orm(current_user)

@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_current_user(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """更新当前用户信息"""
    # 普通用户不能修改角色
    if current_user.role != UserRole.ADMIN and user_update.role is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权限修改用户角色"
        )
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    
    # 处理密码更新
    if "password" in update_data:
        password_check = check_password_strength(update_data["password"])
        if not password_check["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"密码不符合要求: {', '.join(password_check['messages'])}"
            )
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.from_orm(current_user)

@router.post("/change-password", summary="修改密码")
async def change_password(
    password_data: PasswordChange,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """修改当前用户密码"""
    # 验证旧密码
    if not verify_password(password_data.old_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 检查新密码强度
    password_check = check_password_strength(password_data.new_password)
    if not password_check["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"新密码不符合要求: {', '.join(password_check['messages'])}"
        )
    
    # 更新密码
    current_user.hashed_password = get_password_hash(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "密码修改成功"}

@router.get("/users", response_model=List[UserResponse], summary="获取用户列表")
async def get_users(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    role: Optional[UserRole] = Query(None, description="用户角色筛选"),
    is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取用户列表（仅管理员）"""
    query = db.query(User)
    
    # 搜索过滤
    if search:
        search_filter = or_(
            User.username.contains(search),
            User.email.contains(search),
            User.full_name.contains(search),
            User.department.contains(search),
            User.position.contains(search)
        )
        query = query.filter(search_filter)
    
    # 角色过滤
    if role:
        query = query.filter(User.role == role)
    
    # 激活状态过滤
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    # 排序和分页
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()
    
    return [UserResponse.from_orm(user) for user in users]

@router.get("/users/{user_id}", response_model=UserResponse, summary="获取用户详情")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_self)
):
    """获取指定用户详情"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return UserResponse.from_orm(user)

@router.put("/users/{user_id}", response_model=UserResponse, summary="更新用户信息")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """更新用户信息（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    
    # 处理密码更新
    if "password" in update_data:
        password_check = check_password_strength(update_data["password"])
        if not password_check["is_valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"密码不符合要求: {', '.join(password_check['messages'])}"
            )
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return UserResponse.from_orm(user)

@router.delete("/users/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """删除用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己的账户"
        )
    
    db.delete(user)
    db.commit()
    
    return {"message": "用户删除成功"}

@router.get("/stats", response_model=UserStats, summary="获取用户统计")
async def get_user_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """获取用户统计信息（仅管理员）"""
    now = datetime.utcnow()
    today = now.date()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
    
    new_users_today = db.query(User).filter(
        func.date(User.created_at) == today
    ).count()
    
    new_users_this_week = db.query(User).filter(
        User.created_at >= week_ago
    ).count()
    
    new_users_this_month = db.query(User).filter(
        User.created_at >= month_ago
    ).count()
    
    return UserStats(
        total_users=total_users,
        active_users=active_users,
        admin_users=admin_users,
        new_users_today=new_users_today,
        new_users_this_week=new_users_this_week,
        new_users_this_month=new_users_this_month
    )

@router.post("/reset-password/{user_id}", summary="重置用户密码")
async def reset_user_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """重置用户密码（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 生成随机密码
    new_password = generate_random_password()
    user.hashed_password = get_password_hash(new_password)
    user.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "密码重置成功",
        "new_password": new_password,
        "username": user.username
    }