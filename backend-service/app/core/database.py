from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import os
from pathlib import Path

# 数据库配置
DATABASE_DIR = Path("data")
DATABASE_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATABASE_DIR}/app.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # SQLite特有配置
        "timeout": 20  # 连接超时时间
    },
    poolclass=StaticPool,
    echo=False  # 设置为True可以看到SQL语句
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库"""
    from app.models.user import Base as UserBase
    from app.models.family_member import Base as FamilyMemberBase
    from app.models.securities_report import Base as SecuritiesReportBase
    
    # 创建所有表
    UserBase.metadata.create_all(bind=engine)
    FamilyMemberBase.metadata.create_all(bind=engine)
    SecuritiesReportBase.metadata.create_all(bind=engine)
    
    # 创建默认管理员用户
    create_default_admin()

def create_default_admin():
    """创建默认管理员用户和demo用户"""
    from app.models.user import User, UserRole
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        # 检查是否已存在管理员用户
        admin_user = db.query(User).filter(
            User.role == UserRole.ADMIN
        ).first()
        
        if not admin_user:
            # 创建默认管理员
            default_admin = User(
                username="admin",
                email="admin@securities.com",
                hashed_password=get_password_hash("admin123"),
                full_name="系统管理员",
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                department="信息技术部",
                position="系统管理员",
                notes="系统默认管理员账户"
            )
            db.add(default_admin)
            print("✅ 默认管理员用户创建成功")
            print("   用户名: admin")
            print("   密码: admin123")
            print("   邮箱: admin@securities.com")
        else:
            print("ℹ️ 管理员用户已存在")
            
        # 检查是否已存在demo用户
        demo_user = db.query(User).filter(
            User.username == "demo"
        ).first()
        
        if not demo_user:
            # 创建demo用户
            default_demo = User(
                username="demo",
                email="demo@securities.com",
                hashed_password=get_password_hash("demo123"),
                full_name="演示用户",
                role=UserRole.USER,
                is_active=True,
                is_verified=True,
                department="演示部门",
                position="普通用户",
                notes="系统演示用户账户"
            )
            db.add(default_demo)
            print("[SUCCESS] 默认demo用户创建成功")
            print("   用户名: demo")
            print("   密码: demo123")
            print("   邮箱: demo@securities.com")
        else:
            print("[INFO] demo用户已存在")
            
        db.commit()
            
    except Exception as e:
        print(f"[ERROR] 创建默认用户失败: {e}")
        db.rollback()
    finally:
        db.close()

def reset_database():
    """重置数据库（仅开发环境使用）"""
    from app.models.user import Base as UserBase
    from app.models.investor import Base as InvestorBase
    
    # 删除所有表
    UserBase.metadata.drop_all(bind=engine)
    FamilyMemberBase.metadata.drop_all(bind=engine)
    SecuritiesReportBase.metadata.drop_all(bind=engine)
    
    # 重新创建表
    UserBase.metadata.create_all(bind=engine)
    InvestorBase.metadata.create_all(bind=engine)
    
    # 创建默认管理员
    create_default_admin()
    
    print("✅ 数据库重置完成")

def get_db_stats():
    """获取数据库统计信息"""
    from app.models.user import User, UserRole
    
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admin_users = db.query(User).filter(User.role == UserRole.ADMIN).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admin_users,
            "database_url": DATABASE_URL
        }
    finally:
        db.close()