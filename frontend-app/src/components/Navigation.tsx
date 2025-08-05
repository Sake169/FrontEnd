import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
  Menu,
  MenuItem,
  Avatar,
  Divider,
  Chip
} from '@mui/material';
import {
  AccountCircle,
  ExitToApp,
  People as FamilyIcon,
  Assessment as AssessmentIcon,
  Upload as UploadIcon,
  Dashboard as DashboardIcon,
  Security as SecurityIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../services/authService';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, isAdmin } = useAuth();
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    logout();
    handleClose();
    navigate('/login');
  };

  const navigationItems = [
    {
      label: '家属亲戚',
      path: '/family-members',
      icon: <FamilyIcon />,
      roles: [UserRole.USER, UserRole.ADMIN]
    },
    {
      label: '证券填报',
      path: '/securities-reports',
      icon: <AssessmentIcon />,
      roles: [UserRole.USER, UserRole.ADMIN]
    },
    {
      label: '文件上传',
      path: '/upload',
      icon: <UploadIcon />,
      roles: [UserRole.USER, UserRole.ADMIN]
    },
    {
      label: '管理面板',
      path: '/admin/dashboard',
      icon: <DashboardIcon />,
      roles: [UserRole.ADMIN]
    }
  ];

  const filteredItems = navigationItems.filter(item => 
    item.roles.includes(user?.role as UserRole)
  );

  return (
    <AppBar position="static" sx={{ mb: 0 }}>
      <Toolbar>
        {/* Logo和标题 */}
        <Box sx={{ display: 'flex', alignItems: 'center', flexGrow: 1 }}>
          <SecurityIcon sx={{ mr: 2, fontSize: 32 }} />
          <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
            证券公司员工配偶信息报备系统
          </Typography>
        </Box>

        {/* 导航菜单 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mr: 2 }}>
          {filteredItems.map((item) => (
            <Button
              key={item.path}
              color="inherit"
              startIcon={item.icon}
              onClick={() => navigate(item.path)}
              sx={{
                backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent',
                '&:hover': {
                  backgroundColor: 'rgba(255,255,255,0.2)'
                }
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        {/* 用户菜单 */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          {/* 用户角色标识 */}
          <Chip
            label={isAdmin() ? '管理员' : '用户'}
            size="small"
            color={isAdmin() ? 'secondary' : 'default'}
            variant="outlined"
            sx={{ color: 'white', borderColor: 'rgba(255,255,255,0.5)' }}
          />
          
          {/* 用户信息 */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
              {user?.username}
            </Typography>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'rgba(255,255,255,0.2)' }}>
                <AccountCircle />
              </Avatar>
            </IconButton>
          </Box>
        </Box>

        {/* 用户下拉菜单 */}
        <Menu
          id="menu-appbar"
          anchorEl={anchorEl}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          keepMounted
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          open={Boolean(anchorEl)}
          onClose={handleClose}
        >
          <MenuItem disabled>
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start' }}>
              <Typography variant="subtitle2">{user?.username}</Typography>
              <Typography variant="caption" color="text.secondary">
                {user?.email || '未设置邮箱'}
              </Typography>
            </Box>
          </MenuItem>
          <Divider />
          <MenuItem onClick={handleLogout}>
            <ExitToApp sx={{ mr: 2 }} />
            退出登录
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navigation;