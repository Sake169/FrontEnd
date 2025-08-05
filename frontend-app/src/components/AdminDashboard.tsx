import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
  Alert,
  Chip,
  Avatar,
  IconButton,
  Tooltip,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  InputAdornment,
  Fab,
  AppBar,
  Toolbar,
  Menu,
  MenuItem as MenuItemComponent,
  Divider,
  CircularProgress,
  LinearProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon,
  People as PeopleIcon,
  PersonAdd as PersonAddIcon,
  AdminPanelSettings as AdminIcon,
  Person as PersonIcon,
  Email as EmailIcon,
  Phone as PhoneIcon,
  Business as BusinessIcon,
  Work as WorkIcon,
  CalendarToday as CalendarIcon,
  Login as LoginIcon,
  Logout as LogoutIcon,
  Settings as SettingsIcon,
  Dashboard as DashboardIcon,
  Security as SecurityIcon,
  VpnKey as KeyIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useAuth } from '../contexts/AuthContext';
import { authService, User, UserRole, UserCreateRequest, UserUpdateRequest, UserStats } from '../services/authService';
import { useNavigate } from 'react-router-dom';

// 样式组件
const StyledCard = styled(Card)(({ theme }) => ({
  borderRadius: 16,
  boxShadow: '0 8px 32px rgba(0,0,0,0.1)',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 12px 40px rgba(0,0,0,0.15)',
  },
}));

const StatsCard = styled(Card)(({ theme }) => ({
  borderRadius: 16,
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 8px 25px rgba(102, 126, 234, 0.3)',
  },
}));

const AdminDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  // 状态管理
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [roleFilter, setRoleFilter] = useState<UserRole | ''>('');
  const [activeFilter, setActiveFilter] = useState<boolean | ''>('');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  
  // 对话框状态
  const [openUserDialog, setOpenUserDialog] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [userFormData, setUserFormData] = useState<UserCreateRequest>({
    username: '',
    email: '',
    password: '',
    full_name: '',
    phone: '',
    department: '',
    position: '',
    role: UserRole.USER,
    is_active: true,
    notes: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [formError, setFormError] = useState('');
  const [formLoading, setFormLoading] = useState(false);
  
  // 菜单状态
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  
  // 密码重置对话框
  const [resetPasswordDialog, setResetPasswordDialog] = useState(false);
  const [resetPasswordUser, setResetPasswordUser] = useState<User | null>(null);
  const [newPassword, setNewPassword] = useState('');

  // 加载数据
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [usersData, statsData] = await Promise.all([
        authService.getUsers({ limit: 1000 }),
        authService.getUserStats()
      ]);
      setUsers(usersData);
      setStats(statsData);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  // 过滤用户
  const filteredUsers = users.filter(user => {
    const matchesSearch = !searchTerm || 
      user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (user.full_name && user.full_name.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (user.department && user.department.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesRole = !roleFilter || user.role === roleFilter;
    const matchesActive = activeFilter === '' || user.is_active === activeFilter;
    
    return matchesSearch && matchesRole && matchesActive;
  });

  // 分页数据
  const paginatedUsers = filteredUsers.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  // 处理用户表单
  const handleUserSubmit = async () => {
    try {
      setFormLoading(true);
      setFormError('');
      
      if (editingUser) {
        // 更新用户
        const updateData: UserUpdateRequest = { ...userFormData };
        if (!updateData.password) {
          delete updateData.password;
        }
        await authService.updateUser(editingUser.id, updateData);
      } else {
        // 创建用户
        await authService.registerUser(userFormData);
      }
      
      setOpenUserDialog(false);
      resetUserForm();
      await loadData();
    } catch (error: any) {
      setFormError(error.response?.data?.detail || '操作失败');
    } finally {
      setFormLoading(false);
    }
  };

  // 重置用户表单
  const resetUserForm = () => {
    setUserFormData({
      username: '',
      email: '',
      password: '',
      full_name: '',
      phone: '',
      department: '',
      position: '',
      role: UserRole.USER,
      is_active: true,
      notes: '',
    });
    setEditingUser(null);
    setFormError('');
    setShowPassword(false);
  };

  // 编辑用户
  const handleEditUser = (user: User) => {
    setEditingUser(user);
    setUserFormData({
      username: user.username,
      email: user.email,
      password: '',
      full_name: user.full_name || '',
      phone: user.phone || '',
      department: user.department || '',
      position: user.position || '',
      role: user.role,
      is_active: user.is_active,
      notes: '',
    });
    setOpenUserDialog(true);
  };

  // 删除用户
  const handleDeleteUser = async (userId: number) => {
    if (window.confirm('确定要删除这个用户吗？此操作不可撤销。')) {
      try {
        await authService.deleteUser(userId);
        await loadData();
      } catch (error: any) {
        alert(error.response?.data?.detail || '删除失败');
      }
    }
  };

  // 重置密码
  const handleResetPassword = async () => {
    if (!resetPasswordUser) return;
    
    try {
      const result = await authService.resetUserPassword(resetPasswordUser.id);
      setNewPassword(result.new_password);
      await loadData();
    } catch (error: any) {
      alert(error.response?.data?.detail || '重置密码失败');
    }
  };

  // 格式化日期
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  // 获取角色显示
  const getRoleDisplay = (role: UserRole) => {
    return role === UserRole.ADMIN ? '管理员' : '普通用户';
  };

  // 获取角色颜色
  const getRoleColor = (role: UserRole) => {
    return role === UserRole.ADMIN ? 'error' : 'primary';
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box sx={{ flexGrow: 1 }}>
      {/* 顶部导航栏 */}
      <AppBar position="static" sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
        <Toolbar>
          <DashboardIcon sx={{ mr: 2 }} />
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            管理员仪表板
          </Typography>
          <Button
            color="inherit"
            onClick={(e) => setAnchorEl(e.currentTarget)}
            startIcon={<Avatar sx={{ width: 32, height: 32 }}>{user?.username?.charAt(0).toUpperCase()}</Avatar>}
          >
            {user?.full_name || user?.username}
          </Button>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={() => setAnchorEl(null)}
          >
            <MenuItemComponent onClick={() => navigate('/upload')}>
              <LoginIcon sx={{ mr: 1 }} />
              切换到用户界面
            </MenuItemComponent>
            <Divider />
            <MenuItemComponent onClick={logout}>
              <LogoutIcon sx={{ mr: 1 }} />
              退出登录
            </MenuItemComponent>
          </Menu>
        </Toolbar>
      </AppBar>

      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        {/* 统计卡片 */}
        {stats && (
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {stats.total_users}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8 }}>
                        总用户数
                      </Typography>
                    </Box>
                    <PeopleIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </StatsCard>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {stats.active_users}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8 }}>
                        活跃用户
                      </Typography>
                    </Box>
                    <PersonIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </StatsCard>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {stats.admin_users}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8 }}>
                        管理员
                      </Typography>
                    </Box>
                    <AdminIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </StatsCard>
            </Grid>
            
            <Grid item xs={12} sm={6} md={3}>
              <StatsCard sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="h4" sx={{ fontWeight: 'bold' }}>
                        {stats.new_users_this_month}
                      </Typography>
                      <Typography variant="body2" sx={{ opacity: 0.8 }}>
                        本月新增
                      </Typography>
                    </Box>
                    <PersonAddIcon sx={{ fontSize: 40, opacity: 0.8 }} />
                  </Box>
                </CardContent>
              </StatsCard>
            </Grid>
          </Grid>
        )}

        {/* 用户管理 */}
        <StyledCard>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                用户管理
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={loadData}
                >
                  刷新
                </Button>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => {
                    resetUserForm();
                    setOpenUserDialog(true);
                  }}
                  sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}
                >
                  添加用户
                </Button>
              </Box>
            </Box>

            {/* 搜索和过滤 */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  placeholder="搜索用户名、邮箱、姓名或部门"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <SearchIcon />
                      </InputAdornment>
                    ),
                  }}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>角色筛选</InputLabel>
                  <Select
                    value={roleFilter}
                    onChange={(e) => setRoleFilter(e.target.value as UserRole | '')}
                    label="角色筛选"
                  >
                    <MenuItem value="">全部角色</MenuItem>
                    <MenuItem value={UserRole.ADMIN}>管理员</MenuItem>
                    <MenuItem value={UserRole.USER}>普通用户</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={3}>
                <FormControl fullWidth>
                  <InputLabel>状态筛选</InputLabel>
                  <Select
                    value={activeFilter}
                    onChange={(e) => setActiveFilter(e.target.value as boolean | '')}
                    label="状态筛选"
                  >
                    <MenuItem value="">全部状态</MenuItem>
                    <MenuItem value={true}>活跃</MenuItem>
                    <MenuItem value={false}>禁用</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>

            {/* 用户表格 */}
            <TableContainer component={Paper} sx={{ borderRadius: 2 }}>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                    <TableCell>用户信息</TableCell>
                    <TableCell>角色</TableCell>
                    <TableCell>部门/职位</TableCell>
                    <TableCell>状态</TableCell>
                    <TableCell>最后登录</TableCell>
                    <TableCell>操作</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {paginatedUsers.map((user) => (
                    <TableRow key={user.id} hover>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <Avatar sx={{ bgcolor: getRoleColor(user.role) === 'error' ? '#f44336' : '#2196f3' }}>
                            {user.username.charAt(0).toUpperCase()}
                          </Avatar>
                          <Box>
                            <Typography variant="subtitle2" sx={{ fontWeight: 'bold' }}>
                              {user.full_name || user.username}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              {user.email}
                            </Typography>
                            {user.phone && (
                              <Typography variant="caption" color="text.secondary">
                                {user.phone}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={getRoleDisplay(user.role)}
                          color={getRoleColor(user.role) as 'error' | 'primary'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {user.department || '-'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {user.position || '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={user.is_active ? '活跃' : '禁用'}
                          color={user.is_active ? 'success' : 'default'}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {user.last_login ? formatDate(user.last_login) : '从未登录'}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          登录 {user.login_count} 次
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="编辑用户">
                            <IconButton
                              size="small"
                              onClick={() => handleEditUser(user)}
                              color="primary"
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="重置密码">
                            <IconButton
                              size="small"
                              onClick={() => {
                                setResetPasswordUser(user);
                                setResetPasswordDialog(true);
                                setNewPassword('');
                              }}
                              color="warning"
                            >
                              <KeyIcon />
                            </IconButton>
                          </Tooltip>
                          {user.id !== user?.id && (
                            <Tooltip title="删除用户">
                              <IconButton
                                size="small"
                                onClick={() => handleDeleteUser(user.id)}
                                color="error"
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>

            {/* 分页 */}
            <TablePagination
              component="div"
              count={filteredUsers.length}
              page={page}
              onPageChange={(_, newPage) => setPage(newPage)}
              rowsPerPage={rowsPerPage}
              onRowsPerPageChange={(e) => {
                setRowsPerPage(parseInt(e.target.value, 10));
                setPage(0);
              }}
              labelRowsPerPage="每页行数:"
              labelDisplayedRows={({ from, to, count }) => `${from}-${to} 共 ${count} 条`}
            />
          </CardContent>
        </StyledCard>
      </Container>

      {/* 用户表单对话框 */}
      <Dialog
        open={openUserDialog}
        onClose={() => setOpenUserDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editingUser ? '编辑用户' : '添加用户'}
        </DialogTitle>
        <DialogContent>
          {formError && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {formError}
            </Alert>
          )}
          
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="用户名"
                value={userFormData.username}
                onChange={(e) => setUserFormData({ ...userFormData, username: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="邮箱"
                type="email"
                value={userFormData.email}
                onChange={(e) => setUserFormData({ ...userFormData, email: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={editingUser ? "新密码（留空不修改）" : "密码"}
                type={showPassword ? 'text' : 'password'}
                value={userFormData.password}
                onChange={(e) => setUserFormData({ ...userFormData, password: e.target.value })}
                required={!editingUser}
                InputProps={{
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                      >
                        {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="真实姓名"
                value={userFormData.full_name}
                onChange={(e) => setUserFormData({ ...userFormData, full_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="手机号"
                value={userFormData.phone}
                onChange={(e) => setUserFormData({ ...userFormData, phone: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="部门"
                value={userFormData.department}
                onChange={(e) => setUserFormData({ ...userFormData, department: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="职位"
                value={userFormData.position}
                onChange={(e) => setUserFormData({ ...userFormData, position: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>角色</InputLabel>
                <Select
                  value={userFormData.role}
                  onChange={(e) => setUserFormData({ ...userFormData, role: e.target.value as UserRole })}
                  label="角色"
                >
                  <MenuItem value={UserRole.USER}>普通用户</MenuItem>
                  <MenuItem value={UserRole.ADMIN}>管理员</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={userFormData.is_active}
                    onChange={(e) => setUserFormData({ ...userFormData, is_active: e.target.checked })}
                  />
                }
                label="激活用户"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="备注"
                multiline
                rows={3}
                value={userFormData.notes}
                onChange={(e) => setUserFormData({ ...userFormData, notes: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUserDialog(false)}>取消</Button>
          <Button
            onClick={handleUserSubmit}
            variant="contained"
            disabled={formLoading}
            startIcon={formLoading ? <CircularProgress size={20} /> : null}
          >
            {formLoading ? '处理中...' : (editingUser ? '更新' : '创建')}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 重置密码对话框 */}
      <Dialog
        open={resetPasswordDialog}
        onClose={() => setResetPasswordDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>重置用户密码</DialogTitle>
        <DialogContent>
          <Typography sx={{ mb: 2 }}>
            确定要重置用户 <strong>{resetPasswordUser?.username}</strong> 的密码吗？
          </Typography>
          {newPassword && (
            <Alert severity="success" sx={{ mt: 2 }}>
              新密码：<strong>{newPassword}</strong>
              <br />
              请将此密码告知用户，并提醒用户及时修改。
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetPasswordDialog(false)}>取消</Button>
          {!newPassword && (
            <Button
              onClick={handleResetPassword}
              variant="contained"
              color="warning"
            >
              重置密码
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AdminDashboard;