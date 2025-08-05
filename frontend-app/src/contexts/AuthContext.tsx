import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authService, User, UserRole } from '../services/authService';

// 认证上下文接口
interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (user: User) => void;
  refreshUser: () => Promise<void>;
  isAdmin: () => boolean;
  hasPermission: (role: UserRole) => boolean;
}

// 创建认证上下文
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// 认证提供者组件属性
interface AuthProviderProps {
  children: ReactNode;
}

// 认证提供者组件
export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // 初始化认证状态
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        setIsLoading(true);
        
        // 强制清除所有认证信息，确保用户必须重新登录
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_info');
        setUser(null);
      } catch (error) {
        console.error('初始化认证状态失败:', error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  // 登录函数
  const login = (userData: User, token: string) => {
    setUser(userData);
    // authService已经在login方法中处理了token和用户信息的存储
  };

  // 登出函数
  const logout = () => {
    setUser(null);
    authService.logout();
  };

  // 更新用户信息
  const updateUser = (userData: User) => {
    setUser(userData);
    localStorage.setItem('user_info', JSON.stringify(userData));
  };

  // 刷新用户信息
  const refreshUser = async () => {
    try {
      if (authService.isAuthenticated()) {
        const refreshedUser = await authService.getCurrentUser();
        setUser(refreshedUser);
      }
    } catch (error) {
      console.error('刷新用户信息失败:', error);
      // 如果刷新失败，可能是token过期，执行登出
      logout();
    }
  };

  // 检查是否为管理员
  const isAdmin = (): boolean => {
    return user?.role === UserRole.ADMIN;
  };

  // 检查用户权限
  const hasPermission = (requiredRole: UserRole): boolean => {
    if (!user) return false;
    
    if (requiredRole === UserRole.ADMIN) {
      return user.role === UserRole.ADMIN;
    }
    
    return true; // 普通用户权限
  };

  // 计算是否已认证
  const isAuthenticated = !!user && authService.isAuthenticated();

  const value: AuthContextType = {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    updateUser,
    refreshUser,
    isAdmin,
    hasPermission,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// 使用认证上下文的Hook
export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// 认证守卫组件
interface AuthGuardProps {
  children: ReactNode;
  requiredRole?: UserRole;
  fallback?: ReactNode;
}

export const AuthGuard: React.FC<AuthGuardProps> = ({ 
  children, 
  requiredRole, 
  fallback = null 
}) => {
  const { isAuthenticated, hasPermission, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh' 
      }}>
        <div>加载中...</div>
      </div>
    );
  }

  if (!isAuthenticated) {
    // 重定向到登录页
    window.location.href = '/login';
    return null;
  }

  if (requiredRole && !hasPermission(requiredRole)) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        flexDirection: 'column',
        gap: '16px'
      }}>
        <h2>访问被拒绝</h2>
        <p>您没有足够的权限访问此页面</p>
        {fallback}
      </div>
    );
  }

  return <>{children}</>;
};

// 管理员守卫组件
export const AdminGuard: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <AuthGuard requiredRole={UserRole.ADMIN}>
      {children}
    </AuthGuard>
  );
};

// 用户守卫组件（已登录即可）
export const UserGuard: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <AuthGuard>
      {children}
    </AuthGuard>
  );
};

export default AuthContext;