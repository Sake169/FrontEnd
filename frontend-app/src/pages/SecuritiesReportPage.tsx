import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  IconButton,
  Chip,
  Alert,
  Pagination,
  Grid,
  Container,
  Autocomplete,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assessment as AssessmentIcon,
  Send as SendIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

// 证券类型枚举
const SECURITIES_TYPES = [
  { value: 'stock', label: '股票' },
  { value: 'bond', label: '债券' },
  { value: 'fund', label: '基金' },
  { value: 'futures', label: '期货' },
  { value: 'options', label: '期权' },
  { value: 'other', label: '其他' }
];

// 交易类型枚举
const TRANSACTION_TYPES = [
  { value: 'buy', label: '买入' },
  { value: 'sell', label: '卖出' },
  { value: 'dividend', label: '分红' },
  { value: 'split', label: '拆股' },
  { value: 'merge', label: '合股' },
  { value: 'other', label: '其他' }
];

// 填报状态枚举
const REPORT_STATUS = [
  { value: 'draft', label: '草稿', color: 'default' },
  { value: 'submitted', label: '已提交', color: 'primary' },
  { value: 'approved', label: '已审核', color: 'success' },
  { value: 'rejected', label: '已拒绝', color: 'error' }
];

// 家属亲戚接口
interface FamilyMember {
  id: number;
  name: string;
  relationship_type: string;
}

// 证券填报接口
interface SecuritiesReport {
  id?: number;
  family_member_id: number;
  family_member?: FamilyMember;
  securities_type: string;
  securities_code?: string;
  securities_name?: string;
  transaction_type: string;
  transaction_date: string;
  quantity: number;
  price: number;
  amount: number;
  holding_quantity?: number;
  market_value?: number;
  report_period: string;
  status: string;
  submitted_at?: string;
  reviewed_at?: string;
  reviewer_username?: string;
  review_comments?: string;
  created_at?: string;
  updated_at?: string;
}

const SecuritiesReportPage: React.FC = () => {
  const { user } = useAuth();
  const [reports, setReports] = useState<SecuritiesReport[]>([]);
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // 分页状态
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  
  // 搜索和过滤状态
  const [filterStatus, setFilterStatus] = useState('');
  const [filterSecuritiesType, setFilterSecuritiesType] = useState('');
  const [filterPeriod, setFilterPeriod] = useState('');
  
  // 对话框状态
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingReport, setEditingReport] = useState<SecuritiesReport | null>(null);
  const [formData, setFormData] = useState<Partial<SecuritiesReport>>({});
  
  // 审核对话框状态
  const [reviewDialogOpen, setReviewDialogOpen] = useState(false);
  const [reviewingReport, setReviewingReport] = useState<SecuritiesReport | null>(null);
  const [reviewComments, setReviewComments] = useState('');

  // 获取家属亲戚列表
  const fetchFamilyMembers = async () => {
    try {
      const params = new URLSearchParams({ size: '1000' });
      
      // 如果不是管理员，只获取当前用户的家属亲戚
      if (user?.role !== 'admin') {
        params.append('securities_employee_username', user?.username || '');
      }
      
      const response = await fetch(`http://localhost:8000/api/family-members?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setFamilyMembers(data.items || []);
      }
    } catch (err) {
      console.error('获取家属亲戚列表失败:', err);
    }
  };

  // 获取证券填报列表
  const fetchReports = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        size: '10'
      });
      
      if (filterStatus) {
        params.append('status', filterStatus);
      }
      
      if (filterSecuritiesType) {
        params.append('securities_type', filterSecuritiesType);
      }
      
      if (filterPeriod) {
        params.append('report_period', filterPeriod);
      }
      
      // 如果不是管理员，只显示当前用户相关的填报
      if (user?.role !== 'admin') {
        params.append('securities_employee_username', user?.username || '');
      }
      
      const response = await fetch(`http://localhost:8000/api/securities-reports?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('获取证券填报列表失败');
      }
      
      const data = await response.json();
      setReports(data.items || []);
      setTotalPages(data.pages || 1);
      setTotalCount(data.total || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存证券填报信息
  const saveReport = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const reportData = {
        ...formData,
        quantity: Number(formData.quantity),
        price: Number(formData.price),
        amount: Number(formData.amount),
        holding_quantity: formData.holding_quantity ? Number(formData.holding_quantity) : undefined,
        market_value: formData.market_value ? Number(formData.market_value) : undefined
      };
      
      const url = editingReport 
        ? `http://localhost:8000/api/securities-reports/${editingReport.id}`
        : 'http://localhost:8000/api/securities-reports';
      
      const method = editingReport ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(reportData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '保存失败');
      }
      
      setSuccess(editingReport ? '更新成功' : '添加成功');
      setDialogOpen(false);
      setEditingReport(null);
      setFormData({});
      fetchReports();
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 提交填报
  const submitReport = async (id: number) => {
    if (!window.confirm('确定要提交这条填报记录吗？提交后将无法修改。')) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/api/securities-reports/${id}/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('提交失败');
      }
      
      setSuccess('提交成功');
      fetchReports();
    } catch (err) {
      setError(err instanceof Error ? err.message : '提交失败');
    } finally {
      setLoading(false);
    }
  };

  // 审核填报
  const reviewReport = async (approved: boolean) => {
    if (!reviewingReport) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/api/securities-reports/${reviewingReport.id}/review`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          approved,
          comments: reviewComments
        })
      });
      
      if (!response.ok) {
        throw new Error('审核失败');
      }
      
      setSuccess(approved ? '审核通过' : '审核拒绝');
      setReviewDialogOpen(false);
      setReviewingReport(null);
      setReviewComments('');
      fetchReports();
    } catch (err) {
      setError(err instanceof Error ? err.message : '审核失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除填报
  const deleteReport = async (id: number) => {
    if (!window.confirm('确定要删除这条记录吗？')) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/api/securities-reports/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('删除失败');
      }
      
      setSuccess('删除成功');
      fetchReports();
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开编辑对话框
  const openEditDialog = (report?: SecuritiesReport) => {
    setEditingReport(report || null);
    setFormData(report ? { ...report } : {
      family_member_id: 0,
      securities_type: '',
      transaction_type: '',
      transaction_date: new Date().toISOString().split('T')[0],
      quantity: 0,
      price: 0,
      amount: 0,
      report_period: new Date().toISOString().slice(0, 7)
    });
    setDialogOpen(true);
  };

  // 打开审核对话框
  const openReviewDialog = (report: SecuritiesReport) => {
    setReviewingReport(report);
    setReviewComments('');
    setReviewDialogOpen(true);
  };

  // 处理表单输入变化
  const handleFormChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // 自动计算金额
    if (field === 'quantity' || field === 'price') {
      const quantity = field === 'quantity' ? Number(value) : Number(formData.quantity || 0);
      const price = field === 'price' ? Number(value) : Number(formData.price || 0);
      setFormData(prev => ({ ...prev, amount: quantity * price }));
    }
  };

  // 获取状态标签
  const getStatusLabel = (status: string) => {
    const statusInfo = REPORT_STATUS.find(s => s.value === status);
    return statusInfo ? statusInfo.label : status;
  };

  // 获取状态颜色
  const getStatusColor = (status: string): any => {
    const statusInfo = REPORT_STATUS.find(s => s.value === status);
    return statusInfo ? statusInfo.color : 'default';
  };

  // 获取证券类型标签
  const getSecuritiesTypeLabel = (type: string) => {
    const typeInfo = SECURITIES_TYPES.find(t => t.value === type);
    return typeInfo ? typeInfo.label : type;
  };

  // 获取交易类型标签
  const getTransactionTypeLabel = (type: string) => {
    const typeInfo = TRANSACTION_TYPES.find(t => t.value === type);
    return typeInfo ? typeInfo.label : type;
  };

  useEffect(() => {
    fetchFamilyMembers();
  }, []);

  useEffect(() => {
    fetchReports();
  }, [page, filterStatus, filterSecuritiesType, filterPeriod]);

  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => setSuccess(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [success]);

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [error]);

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* 页面标题 */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <AssessmentIcon sx={{ fontSize: 40, color: 'primary.main' }} />
        <Typography variant="h4" component="h1" fontWeight="bold">
          证券填报管理
        </Typography>
      </Box>

      {/* 消息提示 */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* 搜索和过滤 */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>状态</InputLabel>
                <Select
                  value={filterStatus}
                  label="状态"
                  onChange={(e) => setFilterStatus(e.target.value)}
                >
                  <MenuItem value="">全部</MenuItem>
                  {REPORT_STATUS.map(status => (
                    <MenuItem key={status.value} value={status.value}>
                      {status.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth>
                <InputLabel>证券类型</InputLabel>
                <Select
                  value={filterSecuritiesType}
                  label="证券类型"
                  onChange={(e) => setFilterSecuritiesType(e.target.value)}
                >
                  <MenuItem value="">全部</MenuItem>
                  {SECURITIES_TYPES.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField
                fullWidth
                label="填报期间"
                type="month"
                value={filterPeriod}
                onChange={(e) => setFilterPeriod(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={fetchReports}
                  disabled={loading}
                >
                  刷新
                </Button>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => openEditDialog()}
                >
                  新增填报
                </Button>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* 数据表格 */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            证券填报列表 (共 {totalCount} 条记录)
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>家属姓名</TableCell>
                  <TableCell>证券类型</TableCell>
                  <TableCell>证券代码/名称</TableCell>
                  <TableCell>交易类型</TableCell>
                  <TableCell>交易日期</TableCell>
                  <TableCell>数量</TableCell>
                  <TableCell>价格</TableCell>
                  <TableCell>金额</TableCell>
                  <TableCell>状态</TableCell>
                  <TableCell>操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {reports.map((report) => (
                  <TableRow key={report.id}>
                    <TableCell>{report.family_member?.name || '-'}</TableCell>
                    <TableCell>{getSecuritiesTypeLabel(report.securities_type)}</TableCell>
                    <TableCell>
                      <Box>
                        <Typography variant="body2">{report.securities_code || '-'}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {report.securities_name || '-'}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{getTransactionTypeLabel(report.transaction_type)}</TableCell>
                    <TableCell>{report.transaction_date}</TableCell>
                    <TableCell>{report.quantity.toLocaleString()}</TableCell>
                    <TableCell>¥{report.price.toFixed(2)}</TableCell>
                    <TableCell>¥{report.amount.toLocaleString()}</TableCell>
                    <TableCell>
                      <Chip 
                        label={getStatusLabel(report.status)}
                        size="small"
                        color={getStatusColor(report.status)}
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        {report.status === 'draft' && (
                          <>
                            <Tooltip title="编辑">
                              <IconButton
                                size="small"
                                onClick={() => openEditDialog(report)}
                                color="primary"
                              >
                                <EditIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="提交">
                              <IconButton
                                size="small"
                                onClick={() => submitReport(report.id!)}
                                color="success"
                              >
                                <SendIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="删除">
                              <IconButton
                                size="small"
                                onClick={() => deleteReport(report.id!)}
                                color="error"
                              >
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                        {report.status === 'submitted' && user?.role === 'admin' && (
                          <Tooltip title="审核">
                            <IconButton
                              size="small"
                              onClick={() => openReviewDialog(report)}
                              color="warning"
                            >
                              <CheckIcon />
                            </IconButton>
                          </Tooltip>
                        )}
                        {(report.status === 'submitted' || report.status === 'approved') && user?.role === 'admin' && (
                          <Tooltip title="删除">
                            <IconButton
                              size="small"
                              onClick={() => deleteReport(report.id!)}
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
                {reports.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={10} align="center" sx={{ py: 4 }}>
                      <Typography color="text.secondary">
                        暂无数据
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>

          {/* 分页 */}
          {totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
              <Pagination
                count={totalPages}
                page={page}
                onChange={(_, newPage) => setPage(newPage)}
                color="primary"
              />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* 添加/编辑对话框 */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingReport ? '编辑证券填报' : '新增证券填报'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Autocomplete
                options={familyMembers}
                getOptionLabel={(option) => `${option.name} (${option.relationship_type})`}
                value={familyMembers.find(m => m.id === formData.family_member_id) || null}
                onChange={(_, newValue) => handleFormChange('family_member_id', newValue?.id || 0)}
                renderInput={(params) => (
                  <TextField {...params} label="选择家属亲戚 *" required />
                )}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>证券类型</InputLabel>
                <Select
                  value={formData.securities_type || ''}
                  label="证券类型"
                  onChange={(e) => handleFormChange('securities_type', e.target.value)}
                >
                  {SECURITIES_TYPES.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>交易类型</InputLabel>
                <Select
                  value={formData.transaction_type || ''}
                  label="交易类型"
                  onChange={(e) => handleFormChange('transaction_type', e.target.value)}
                >
                  {TRANSACTION_TYPES.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="证券代码"
                value={formData.securities_code || ''}
                onChange={(e) => handleFormChange('securities_code', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="证券名称"
                value={formData.securities_name || ''}
                onChange={(e) => handleFormChange('securities_name', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="交易日期 *"
                type="date"
                value={formData.transaction_date || ''}
                onChange={(e) => handleFormChange('transaction_date', e.target.value)}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="填报期间 *"
                type="month"
                value={formData.report_period || ''}
                onChange={(e) => handleFormChange('report_period', e.target.value)}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="数量 *"
                type="number"
                value={formData.quantity || ''}
                onChange={(e) => handleFormChange('quantity', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="价格 *"
                type="number"
                step="0.01"
                value={formData.price || ''}
                onChange={(e) => handleFormChange('price', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="金额"
                type="number"
                step="0.01"
                value={formData.amount || ''}
                onChange={(e) => handleFormChange('amount', e.target.value)}
                InputProps={{ readOnly: true }}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="持仓数量"
                type="number"
                value={formData.holding_quantity || ''}
                onChange={(e) => handleFormChange('holding_quantity', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="市值"
                type="number"
                step="0.01"
                value={formData.market_value || ''}
                onChange={(e) => handleFormChange('market_value', e.target.value)}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>取消</Button>
          <Button 
            onClick={saveReport} 
            variant="contained"
            disabled={!formData.family_member_id || !formData.securities_type || !formData.transaction_type || !formData.transaction_date || !formData.quantity || !formData.price || loading}
          >
            {loading ? '保存中...' : '保存'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 审核对话框 */}
      <Dialog open={reviewDialogOpen} onClose={() => setReviewDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>审核证券填报</DialogTitle>
        <DialogContent>
          {reviewingReport && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle1" gutterBottom>
                填报信息：{reviewingReport.family_member?.name} - {getSecuritiesTypeLabel(reviewingReport.securities_type)}
              </Typography>
              <TextField
                fullWidth
                label="审核意见"
                multiline
                rows={4}
                value={reviewComments}
                onChange={(e) => setReviewComments(e.target.value)}
                placeholder="请输入审核意见..."
                sx={{ mt: 2 }}
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setReviewDialogOpen(false)}>取消</Button>
          <Button 
            onClick={() => reviewReport(false)} 
            color="error"
            startIcon={<CloseIcon />}
            disabled={loading}
          >
            拒绝
          </Button>
          <Button 
            onClick={() => reviewReport(true)} 
            variant="contained"
            color="success"
            startIcon={<CheckIcon />}
            disabled={loading}
          >
            通过
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default SecuritiesReportPage;