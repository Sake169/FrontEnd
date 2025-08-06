import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './components/LoginPage';
import AdminDashboard from './components/AdminDashboard';
import FileUploadPage from './pages/FileUploadPage';
import FamilyMemberPage from './pages/FamilyMemberPage';
import SecuritiesReportPage from './pages/SecuritiesReportPage';
import InvestmentRecords from './pages/InvestmentRecords';
import QuarterlyReportPage from './pages/QuarterlyReportPage';
import Layout from './components/Layout';
import { UserRole } from './services/authService';
import './App.css';

// Material-UI主题配置
const theme = createTheme({
  palette: {
    primary: {
      main: '#667eea',
    },
    secondary: {
      main: '#764ba2',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
      },
    },
  },
});

// 路由保护组件
const ProtectedRoute: React.FC<{ children: React.ReactNode; requiredRole?: UserRole }> = ({ 
  children, 
  requiredRole 
}) => {
  const { isAuthenticated, user, isLoading } = useAuth();

  if (isLoading) {
    return <div>加载中...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    // 如果需要管理员权限但用户不是管理员，重定向到用户页面
    if (requiredRole === UserRole.ADMIN && user?.role === UserRole.USER) {
      return <Navigate to="/upload" replace />;
    }
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// 主应用组件
const AppContent: React.FC = () => {
  const { isAuthenticated, user } = useAuth();

  return (
    <Routes>
      {/* 登录页面 */}
      <Route 
        path="/login" 
        element={
          isAuthenticated ? (
            user?.role === UserRole.ADMIN ? (
              <Navigate to="/admin/dashboard" replace />
            ) : (
              <Navigate to="/upload" replace />
            )
          ) : (
            <LoginPage />
          )
        } 
      />
      
      {/* 管理员仪表板 */}
      <Route 
        path="/admin/dashboard" 
        element={
          <ProtectedRoute requiredRole={UserRole.ADMIN}>
            <Layout>
              <AdminDashboard />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      {/* 文件上传页面 */}
      <Route 
        path="/upload" 
        element={
          <ProtectedRoute>
            <Layout>
              <FileUploadPage />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      {/* 家属亲戚管理页面 */}
      <Route 
        path="/family-members" 
        element={
          <ProtectedRoute>
            <Layout>
              <FamilyMemberPage />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      {/* 证券填报管理页面 */}
      <Route 
        path="/securities-reports" 
        element={
          <ProtectedRoute>
            <Layout>
              <SecuritiesReportPage />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      {/* 投资记录管理页面 */}
      <Route 
        path="/investment-records" 
        element={
          <ProtectedRoute>
            <Layout>
              <InvestmentRecords />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      {/* 季度投资报告页面 */}
      <Route 
        path="/quarterly-report" 
        element={
          <ProtectedRoute>
            <Layout>
              <QuarterlyReportPage />
            </Layout>
          </ProtectedRoute>
        } 
      />
      
      {/* 根路径重定向 */}
      <Route 
        path="/" 
        element={
          isAuthenticated ? (
            user?.role === UserRole.ADMIN ? (
              <Navigate to="/admin/dashboard" replace />
            ) : (
              <Navigate to="/family-members" replace />
            )
          ) : (
            <Navigate to="/login" replace />
          )
        } 
      />
      
      {/* 404页面 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <AppContent />
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
};

export default App;