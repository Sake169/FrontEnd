import axios, { AxiosResponse } from 'axios';

// API基础URL
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// 创建axios实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 处理认证错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期或无效，清除本地存储并跳转到登录页
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// 用户角色枚举
export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
}

// 用户信息接口
export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  phone?: string;
  department?: string;
  position?: string;
  role: UserRole;
  is_active: boolean;
  is_verified: boolean;
  avatar_url?: string;
  last_login?: string;
  login_count: number;
  created_at: string;
  updated_at: string;
}

// 登录请求接口
export interface LoginRequest {
  username: string;
  password: string;
  remember_me?: boolean;
}

// 登录响应接口
export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

// 用户创建接口
export interface UserCreateRequest {
  username: string;
  email: string;
  password: string;
  full_name?: string;
  phone?: string;
  department?: string;
  position?: string;
  role?: UserRole;
  is_active?: boolean;
  notes?: string;
}

// 用户更新接口
export interface UserUpdateRequest {
  username?: string;
  email?: string;
  full_name?: string;
  phone?: string;
  department?: string;
  position?: string;
  role?: UserRole;
  is_active?: boolean;
  is_verified?: boolean;
  notes?: string;
  password?: string;
}

// 密码修改接口
export interface PasswordChangeRequest {
  old_password: string;
  new_password: string;
}

// 用户统计接口
export interface UserStats {
  total_users: number;
  active_users: number;
  admin_users: number;
  new_users_today: number;
  new_users_this_week: number;
  new_users_this_month: number;
}

// 用户列表查询参数
export interface UserListParams {
  skip?: number;
  limit?: number;
  search?: string;
  role?: UserRole;
  is_active?: boolean;
}

// 认证服务类
class AuthService {
  /**
   * 用户登录
   */
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response: AxiosResponse<LoginResponse> = await api.post('/auth/login', credentials);
    
    // 保存token和用户信息到本地存储
    localStorage.setItem('access_token', response.data.access_token);
    localStorage.setItem('user_info', JSON.stringify(response.data.user));
    
    return response.data;
  }

  /**
   * 用户登出
   */
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_info');
    window.location.href = '/login';
  }

  /**
   * 获取当前用户信息
   */
  async getCurrentUser(): Promise<User> {
    const response: AxiosResponse<User> = await api.get('/auth/me');
    
    // 更新本地存储的用户信息
    localStorage.setItem('user_info', JSON.stringify(response.data));
    
    return response.data;
  }

  /**
   * 更新当前用户信息
   */
  async updateCurrentUser(userData: UserUpdateRequest): Promise<User> {
    const response: AxiosResponse<User> = await api.put('/auth/me', userData);
    
    // 更新本地存储的用户信息
    localStorage.setItem('user_info', JSON.stringify(response.data));
    
    return response.data;
  }

  /**
   * 修改密码
   */
  async changePassword(passwordData: PasswordChangeRequest): Promise<void> {
    await api.post('/auth/change-password', passwordData);
  }

  /**
   * 注册新用户（仅管理员）
   */
  async registerUser(userData: UserCreateRequest): Promise<User> {
    const response: AxiosResponse<User> = await api.post('/auth/register', userData);
    return response.data;
  }

  /**
   * 获取用户列表（仅管理员）
   */
  async getUsers(params?: UserListParams): Promise<User[]> {
    const response: AxiosResponse<User[]> = await api.get('/auth/users', { params });
    return response.data;
  }

  /**
   * 获取用户详情
   */
  async getUser(userId: number): Promise<User> {
    const response: AxiosResponse<User> = await api.get(`/auth/users/${userId}`);
    return response.data;
  }

  /**
   * 更新用户信息（仅管理员）
   */
  async updateUser(userId: number, userData: UserUpdateRequest): Promise<User> {
    const response: AxiosResponse<User> = await api.put(`/auth/users/${userId}`, userData);
    return response.data;
  }

  /**
   * 删除用户（仅管理员）
   */
  async deleteUser(userId: number): Promise<void> {
    await api.delete(`/auth/users/${userId}`);
  }

  /**
   * 获取用户统计（仅管理员）
   */
  async getUserStats(): Promise<UserStats> {
    const response: AxiosResponse<UserStats> = await api.get('/auth/stats');
    return response.data;
  }

  /**
   * 重置用户密码（仅管理员）
   */
  async resetUserPassword(userId: number): Promise<{ message: string; new_password: string; username: string }> {
    const response = await api.post(`/auth/reset-password/${userId}`);
    return response.data;
  }

  /**
   * 检查是否已登录
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    const userInfo = localStorage.getItem('user_info');
    return !!(token && userInfo);
  }

  /**
   * 获取本地存储的用户信息
   */
  getStoredUser(): User | null {
    const userInfo = localStorage.getItem('user_info');
    return userInfo ? JSON.parse(userInfo) : null;
  }

  /**
   * 获取本地存储的token
   */
  getStoredToken(): string | null {
    return localStorage.getItem('access_token');
  }

  /**
   * 检查用户是否为管理员
   */
  isAdmin(): boolean {
    const user = this.getStoredUser();
    return user?.role === UserRole.ADMIN;
  }

  /**
   * 检查用户权限
   */
  hasPermission(requiredRole: UserRole): boolean {
    const user = this.getStoredUser();
    if (!user) return false;
    
    if (requiredRole === UserRole.ADMIN) {
      return user.role === UserRole.ADMIN;
    }
    
    return true; // 普通用户权限
  }

  /**
   * 刷新用户信息
   */
  async refreshUserInfo(): Promise<User | null> {
    try {
      if (this.isAuthenticated()) {
        return await this.getCurrentUser();
      }
      return null;
    } catch (error) {
      console.error('刷新用户信息失败:', error);
      return null;
    }
  }
}

// 导出单例实例
export const authService = new AuthService();
export default authService;