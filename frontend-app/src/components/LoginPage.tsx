import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  InputAdornment,
  IconButton,
  FormControlLabel,
  Checkbox,
  Divider,
  Avatar,
  Container,
  Paper,
  Fade,
  CircularProgress
} from '@mui/material';
import {
  Visibility,
  VisibilityOff,
  Person,
  Lock,
  Login as LoginIcon,
  AdminPanelSettings,
  Upload,
  Security
} from '@mui/icons-material';
import { styled, keyframes } from '@mui/material/styles';
import { authService } from '../services/authService';
import { useAuth } from '../contexts/AuthContext';

// 动画定义
const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const float = keyframes`
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
`;

const gradient = keyframes`
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
`;

// 样式组件
const StyledContainer = styled(Container)(({ theme }) => ({
  minHeight: '100vh',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  background: `linear-gradient(-45deg, #667eea, #764ba2, #f093fb, #f5576c)`,
  backgroundSize: '400% 400%',
  animation: `${gradient} 15s ease infinite`,
  padding: theme.spacing(2),
}));

const StyledCard = styled(Card)(({ theme }) => ({
  maxWidth: 450,
  width: '100%',
  borderRadius: 20,
  boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
  backdropFilter: 'blur(10px)',
  background: 'rgba(255, 255, 255, 0.95)',
  animation: `${fadeInUp} 0.8s ease-out`,
  overflow: 'visible',
  position: 'relative',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: -2,
    left: -2,
    right: -2,
    bottom: -2,
    background: 'linear-gradient(45deg, #667eea, #764ba2, #f093fb, #f5576c)',
    borderRadius: 22,
    zIndex: -1,
    backgroundSize: '400% 400%',
    animation: `${gradient} 15s ease infinite`,
  },
}));

const StyledAvatar = styled(Avatar)(({ theme }) => ({
  width: 80,
  height: 80,
  margin: '0 auto 20px',
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  animation: `${float} 3s ease-in-out infinite`,
  boxShadow: '0 10px 20px rgba(102, 126, 234, 0.3)',
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
  '& .MuiOutlinedInput-root': {
    borderRadius: 12,
    transition: 'all 0.3s ease',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: '0 5px 15px rgba(0,0,0,0.1)',
    },
    '&.Mui-focused': {
      transform: 'translateY(-2px)',
      boxShadow: '0 5px 15px rgba(102, 126, 234, 0.2)',
    },
  },
}));

const StyledButton = styled(Button)(({ theme }) => ({
  borderRadius: 12,
  padding: '12px 24px',
  fontSize: '16px',
  fontWeight: 600,
  textTransform: 'none',
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  transition: 'all 0.3s ease',
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 10px 25px rgba(102, 126, 234, 0.3)',
    background: 'linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%)',
  },
  '&:active': {
    transform: 'translateY(0)',
  },
}));

const FeatureCard = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  borderRadius: 12,
  textAlign: 'center',
  background: 'rgba(255, 255, 255, 0.8)',
  backdropFilter: 'blur(10px)',
  transition: 'all 0.3s ease',
  cursor: 'pointer',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: '0 10px 25px rgba(0,0,0,0.1)',
  },
}));

interface LoginFormData {
  username: string;
  password: string;
  rememberMe: boolean;
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: '',
    rememberMe: false,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showFeatures, setShowFeatures] = useState(false);

  useEffect(() => {
    // 延迟显示功能介绍
    const timer = setTimeout(() => setShowFeatures(true), 1000);
    return () => clearTimeout(timer);
  }, []);

  const handleInputChange = (field: keyof LoginFormData) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = field === 'rememberMe' ? event.target.checked : event.target.value;
    setFormData(prev => ({ ...prev, [field]: value }));
    if (error) setError('');
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!formData.username.trim() || !formData.password.trim()) {
      setError('请输入用户名和密码');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await authService.login({
        username: formData.username.trim(),
        password: formData.password,
        remember_me: formData.rememberMe,
      });

      // 保存认证信息
      login(response.user, response.access_token);

      // 根据用户角色跳转
      if (response.user.role === 'admin') {
        navigate('/admin/dashboard');
      } else {
        navigate('/upload');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '登录失败，请检查用户名和密码');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (role: 'admin' | 'user') => {
    const demoCredentials = {
      admin: { username: 'admin', password: 'admin123' },
      user: { username: 'demo', password: 'demo123' }
    };

    setFormData({
      username: demoCredentials[role].username,
      password: demoCredentials[role].password,
      rememberMe: false,
    });
  };

  return (
    <StyledContainer maxWidth={false}>
      <Box sx={{ width: '100%', maxWidth: 1200 }}>
        <Fade in timeout={800}>
          <Box sx={{ textAlign: 'center', mb: 4 }}>
            <Typography
              variant="h2"
              sx={{
                fontWeight: 700,
                background: 'linear-gradient(135deg, #fff 0%, #f0f0f0 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
                mb: 1,
              }}
            >
              证券人员管理系统
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255, 255, 255, 0.9)',
                fontWeight: 300,
              }}
            >
              安全 · 高效 · 智能
            </Typography>
          </Box>
        </Fade>

        <Box sx={{ display: 'flex', gap: 4, alignItems: 'flex-start' }}>
          {/* 登录表单 */}
          <StyledCard>
            <CardContent sx={{ p: 4 }}>
              <StyledAvatar>
                <Security sx={{ fontSize: 40 }} />
              </StyledAvatar>

              <Typography
                variant="h4"
                align="center"
                sx={{
                  fontWeight: 700,
                  mb: 1,
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                欢迎登录
              </Typography>

              <Typography
                variant="body2"
                align="center"
                color="text.secondary"
                sx={{ mb: 3 }}
              >
                请输入您的登录凭据
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
                <StyledTextField
                  fullWidth
                  label="用户名/邮箱"
                  value={formData.username}
                  onChange={handleInputChange('username')}
                  margin="normal"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Person color="action" />
                      </InputAdornment>
                    ),
                  }}
                  disabled={loading}
                />

                <StyledTextField
                  fullWidth
                  label="密码"
                  type={showPassword ? 'text' : 'password'}
                  value={formData.password}
                  onChange={handleInputChange('password')}
                  margin="normal"
                  InputProps={{
                    startAdornment: (
                      <InputAdornment position="start">
                        <Lock color="action" />
                      </InputAdornment>
                    ),
                    endAdornment: (
                      <InputAdornment position="end">
                        <IconButton
                          onClick={() => setShowPassword(!showPassword)}
                          edge="end"
                        >
                          {showPassword ? <VisibilityOff /> : <Visibility />}
                        </IconButton>
                      </InputAdornment>
                    ),
                  }}
                  disabled={loading}
                />

                <FormControlLabel
                  control={
                    <Checkbox
                      checked={formData.rememberMe}
                      onChange={handleInputChange('rememberMe')}
                      color="primary"
                    />
                  }
                  label="记住我"
                  sx={{ mt: 1, mb: 2 }}
                />

                <StyledButton
                  type="submit"
                  fullWidth
                  variant="contained"
                  size="large"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <LoginIcon />}
                  sx={{ mt: 2, mb: 2 }}
                >
                  {loading ? '登录中...' : '登录'}
                </StyledButton>

                <Divider sx={{ my: 2 }}>
                  <Typography variant="body2" color="text.secondary">
                    快速体验
                  </Typography>
                </Divider>

                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleDemoLogin('admin')}
                    startIcon={<AdminPanelSettings />}
                    sx={{ flex: 1, borderRadius: 2 }}
                  >
                    管理员
                  </Button>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={() => handleDemoLogin('user')}
                    startIcon={<Upload />}
                    sx={{ flex: 1, borderRadius: 2 }}
                  >
                    普通用户
                  </Button>
                </Box>
              </Box>
            </CardContent>
          </StyledCard>

          {/* 功能介绍 */}
          <Fade in={showFeatures} timeout={1000}>
            <Box sx={{ flex: 1, minWidth: 300 }}>
              <Typography
                variant="h5"
                sx={{
                  color: 'white',
                  fontWeight: 600,
                  mb: 3,
                  textAlign: 'center',
                }}
              >
                系统功能
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FeatureCard elevation={3}>
                  <AdminPanelSettings
                    sx={{ fontSize: 40, color: '#667eea', mb: 1 }}
                  />
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    管理员功能
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    用户管理、权限控制、数据统计、系统监控
                  </Typography>
                </FeatureCard>

                <FeatureCard elevation={3}>
                  <Upload sx={{ fontSize: 40, color: '#764ba2', mb: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    文件处理
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Excel文件上传、数据处理、智能分析、报告生成
                  </Typography>
                </FeatureCard>

                <FeatureCard elevation={3}>
                  <Security sx={{ fontSize: 40, color: '#f093fb', mb: 1 }} />
                  <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                    安全保障
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    数据加密、权限验证、操作日志、安全审计
                  </Typography>
                </FeatureCard>
              </Box>

              <Box sx={{ mt: 3, p: 2, borderRadius: 2, background: 'rgba(255,255,255,0.1)' }}>
                <Typography variant="body2" sx={{ color: 'white', textAlign: 'center' }}>
                  💡 提示：管理员可以查看所有用户数据，普通用户只能上传和处理文件
                </Typography>
              </Box>
            </Box>
          </Fade>
        </Box>
      </Box>
    </StyledContainer>
  );
};

export default LoginPage;