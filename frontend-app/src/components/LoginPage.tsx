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
  Security,
  PersonAdd,
  Email,
  Phone,
  Badge
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

interface RegisterFormData {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  phone: string;
  idNumber: string;
}

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [isRegisterMode, setIsRegisterMode] = useState(false);
  const [formData, setFormData] = useState<LoginFormData>({
    username: '',
    password: '',
    rememberMe: false,
  });
  const [registerData, setRegisterData] = useState<RegisterFormData>({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    fullName: '',
    phone: '',
    idNumber: '',
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
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

  const handleRegisterInputChange = (field: keyof RegisterFormData) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setRegisterData(prev => ({ ...prev, [field]: value }));
    if (error) setError('');
  };

  const handleModeSwitch = () => {
    setIsRegisterMode(!isRegisterMode);
    setError('');
    setFormData({ username: '', password: '', rememberMe: false });
    setRegisterData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      fullName: '',
      phone: '',
      idNumber: '',
    });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (isRegisterMode) {
      await handleRegisterSubmit();
    } else {
      await handleLoginSubmit();
    }
  };

  const handleLoginSubmit = async () => {
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

  const handleRegisterSubmit = async () => {
    // 验证必填字段
    if (!registerData.username.trim() || !registerData.email.trim() || 
        !registerData.password.trim() || !registerData.fullName.trim() || 
        !registerData.phone.trim() || !registerData.idNumber.trim()) {
      setError('请填写所有必填字段');
      return;
    }

    // 验证密码确认
    if (registerData.password !== registerData.confirmPassword) {
      setError('两次输入的密码不一致');
      return;
    }

    // 验证密码长度
    if (registerData.password.length < 6) {
      setError('密码长度至少6位');
      return;
    }

    // 验证邮箱格式
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(registerData.email)) {
      setError('请输入有效的邮箱地址');
      return;
    }

    // 验证手机号格式
    const phoneRegex = /^1[3-9]\d{9}$/;
    if (!phoneRegex.test(registerData.phone)) {
      setError('请输入有效的手机号码');
      return;
    }

    // 验证身份证号格式
    const idRegex = /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/;
    if (!idRegex.test(registerData.idNumber)) {
      setError('请输入有效的身份证号码');
      return;
    }

    setLoading(true);
    setError('');

    try {
      await authService.registerUser({
        username: registerData.username.trim(),
        email: registerData.email.trim(),
        password: registerData.password,
        full_name: registerData.fullName.trim(),
        phone: registerData.phone.trim(),
        id_number: registerData.idNumber.trim(),
      });

      // 注册成功，切换到登录模式
      setIsRegisterMode(false);
      setFormData({
        username: registerData.username,
        password: '',
        rememberMe: false,
      });
      setRegisterData({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        fullName: '',
        phone: '',
        idNumber: '',
      });
      setError('');
      // 可以显示成功消息
      alert('注册成功！请使用您的用户名和密码登录。');
    } catch (err: any) {
      setError(err.response?.data?.detail || '注册失败，请检查输入信息');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (role: 'admin' | 'user') => {
    const demoCredentials = {
      admin: { username: 'admin', password: 'admin123' },
      user: { username: 'demo', password: 'demo123' }
    };

    const credentials = demoCredentials[role];
    setFormData({
      username: credentials.username,
      password: credentials.password,
      rememberMe: false,
    });

    // 自动执行登录
    setLoading(true);
    setError('');

    try {
      const response = await authService.login({
        username: credentials.username,
        password: credentials.password,
        remember_me: false,
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
              证券人员填报系统
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

        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
          {/* 登录表单 - 居中显示 */}
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
                {isRegisterMode ? '用户注册' : '欢迎登录'}
              </Typography>

              <Typography
                variant="body2"
                align="center"
                color="text.secondary"
                sx={{ mb: 3 }}
              >
                {isRegisterMode ? '请填写注册信息' : '请输入您的登录凭据'}
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2, borderRadius: 2 }}>
                  {error}
                </Alert>
              )}

              {!isRegisterMode ? (
                // 登录表单
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

                  <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
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

                  <Divider sx={{ my: 2 }} />

                  <Button
                    fullWidth
                    variant="text"
                    onClick={() => setIsRegisterMode(true)}
                    startIcon={<PersonAdd />}
                    sx={{ borderRadius: 2 }}
                  >
                    还没有账户？立即注册
                  </Button>
                </Box>
              ) : (
                // 注册表单
                <Box component="form" onSubmit={handleRegisterSubmit} sx={{ mt: 2 }}>
                  <StyledTextField
                    fullWidth
                    label="用户名"
                    value={registerData.username}
                    onChange={handleRegisterInputChange('username')}
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
                    label="邮箱"
                    type="email"
                    value={registerData.email}
                    onChange={handleRegisterInputChange('email')}
                    margin="normal"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Email color="action" />
                        </InputAdornment>
                      ),
                    }}
                    disabled={loading}
                  />

                  <StyledTextField
                    fullWidth
                    label="真实姓名"
                    value={registerData.fullName}
                    onChange={handleRegisterInputChange('fullName')}
                    margin="normal"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Badge color="action" />
                        </InputAdornment>
                      ),
                    }}
                    disabled={loading}
                  />

                  <StyledTextField
                    fullWidth
                    label="手机号"
                    value={registerData.phone}
                    onChange={handleRegisterInputChange('phone')}
                    margin="normal"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Phone color="action" />
                        </InputAdornment>
                      ),
                    }}
                    disabled={loading}
                  />

                  <StyledTextField
                    fullWidth
                    label="身份证号"
                    value={registerData.idNumber}
                    onChange={handleRegisterInputChange('idNumber')}
                    margin="normal"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Badge color="action" />
                        </InputAdornment>
                      ),
                    }}
                    disabled={loading}
                  />

                  <StyledTextField
                    fullWidth
                    label="密码"
                    type={showPassword ? 'text' : 'password'}
                    value={registerData.password}
                    onChange={handleRegisterInputChange('password')}
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

                  <StyledTextField
                    fullWidth
                    label="确认密码"
                    type={showPassword ? 'text' : 'password'}
                    value={registerData.confirmPassword}
                    onChange={handleRegisterInputChange('confirmPassword')}
                    margin="normal"
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <Lock color="action" />
                        </InputAdornment>
                      ),
                    }}
                    disabled={loading}
                  />

                  <StyledButton
                    type="submit"
                    fullWidth
                    variant="contained"
                    size="large"
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <PersonAdd />}
                    sx={{ mt: 3, mb: 2 }}
                  >
                    {loading ? '注册中...' : '注册'}
                  </StyledButton>

                  <Button
                    fullWidth
                    variant="text"
                    onClick={() => setIsRegisterMode(false)}
                    startIcon={<LoginIcon />}
                    sx={{ borderRadius: 2 }}
                  >
                    已有账户？返回登录
                  </Button>
                </Box>
              )}
            </CardContent>
          </StyledCard>
        </Box>
      </Box>
    </StyledContainer>
  );
};

export default LoginPage;