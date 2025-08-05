from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, UserRole, TokenData
import secrets
import string

# 密码加密配置
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
SECRET_KEY = "your-secret-key-change-in-production"  # 生产环境需要更改
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

# HTTP Bearer认证
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)

def generate_random_password(length: int = 12) -> str:
    """生成随机密码"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> TokenData:
    """验证令牌"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")
        
        if username is None or user_id is None:
            raise credentials_exception
            
        token_data = TokenData(
            username=username,
            user_id=user_id,
            role=role
        )
        return token_data
    except JWTError:
        raise credentials_exception

def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """认证用户"""
    user = db.query(User).filter(
        (User.username == username) | (User.email == username)
    ).first()
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.is_active:
        return None
        
    return user

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> User:
    """获取当前用户"""
    token = credentials.credentials
    token_data = verify_token(token)
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """要求管理员权限"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def require_admin_or_self(user_id: int, current_user: User = Depends(get_current_active_user)) -> User:
    """要求管理员权限或操作自己的数据"""
    if current_user.role != UserRole.ADMIN and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

def check_password_strength(password: str) -> dict:
    """检查密码强度"""
    result = {
        "is_valid": True,
        "score": 0,
        "messages": []
    }
    
    if len(password) < 8:
        result["is_valid"] = False
        result["messages"].append("密码长度至少8位")
    else:
        result["score"] += 1
    
    if not any(c.islower() for c in password):
        result["is_valid"] = False
        result["messages"].append("密码必须包含小写字母")
    else:
        result["score"] += 1
    
    if not any(c.isupper() for c in password):
        result["is_valid"] = False
        result["messages"].append("密码必须包含大写字母")
    else:
        result["score"] += 1
    
    if not any(c.isdigit() for c in password):
        result["is_valid"] = False
        result["messages"].append("密码必须包含数字")
    else:
        result["score"] += 1
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        result["messages"].append("建议包含特殊字符以提高安全性")
    else:
        result["score"] += 1
    
    if result["is_valid"]:
        if result["score"] >= 4:
            result["strength"] = "强"
        elif result["score"] >= 3:
            result["strength"] = "中"
        else:
            result["strength"] = "弱"
    
    return result