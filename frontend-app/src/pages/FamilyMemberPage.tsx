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
  Fab,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Person as PersonIcon,
  People as FamilyIcon,
  Search as SearchIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';

// 关系类型枚举
const RELATIONSHIP_TYPES = [
  { value: 'spouse', label: '配偶' },
  { value: 'parent', label: '父母' },
  { value: 'child', label: '子女' },
  { value: 'sibling', label: '兄弟姐妹' },
  { value: 'grandparent', label: '祖父母/外祖父母' },
  { value: 'grandchild', label: '孙子女/外孙子女' },
  { value: 'other', label: '其他亲属' }
];

// 证件类型枚举
const ID_TYPES = [
  { value: 'id_card', label: '身份证' },
  { value: 'passport', label: '护照' },
  { value: 'other', label: '其他' }
];

// 家属亲戚接口
interface FamilyMember {
  id?: number;
  securities_employee_username: string;
  name: string;
  relationship_type: string;
  id_type: string;
  id_number: string;
  phone?: string;
  email?: string;
  address?: string;
  qq?: string;
  wechat?: string;
  alipay_account?: string;
  bank_account?: string;
  created_at?: string;
  updated_at?: string;
}

const FamilyMemberPage: React.FC = () => {
  const { user } = useAuth();
  const [familyMembers, setFamilyMembers] = useState<FamilyMember[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // 分页状态
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  
  // 搜索和过滤状态
  const [searchName, setSearchName] = useState('');
  const [filterRelationship, setFilterRelationship] = useState('');
  
  // 对话框状态
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingMember, setEditingMember] = useState<FamilyMember | null>(null);
  const [formData, setFormData] = useState<Partial<FamilyMember>>({});

  // 获取家属亲戚列表
  const fetchFamilyMembers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        size: '10'
      });
      
      if (searchName) {
        params.append('name', searchName);
      }
      
      if (filterRelationship) {
        params.append('relationship_type', filterRelationship);
      }
      
      // 如果不是管理员，只显示当前用户的家属亲戚
      if (user?.role !== 'admin') {
        params.append('securities_employee_username', user?.username || '');
      }
      
      const response = await fetch(`http://localhost:8000/api/family-members?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error('获取家属亲戚列表失败');
      }
      
      const data = await response.json();
      setFamilyMembers(data.items || []);
      setTotalPages(data.pages || 1);
      setTotalCount(data.total || 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : '获取数据失败');
    } finally {
      setLoading(false);
    }
  };

  // 保存家属亲戚信息
  const saveFamilyMember = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const memberData = {
        ...formData,
        securities_employee_username: user?.username || ''
      };
      
      const url = editingMember 
        ? `http://localhost:8000/api/family-members/${editingMember.id}`
        : 'http://localhost:8000/api/family-members';
      
      const method = editingMember ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(memberData)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '保存失败');
      }
      
      setSuccess(editingMember ? '更新成功' : '添加成功');
      setDialogOpen(false);
      setEditingMember(null);
      setFormData({});
      fetchFamilyMembers();
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 删除家属亲戚
  const deleteFamilyMember = async (id: number) => {
    if (!window.confirm('确定要删除这条记录吗？')) {
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`http://localhost:8000/api/family-members/${id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('删除失败');
      }
      
      setSuccess('删除成功');
      fetchFamilyMembers();
    } catch (err) {
      setError(err instanceof Error ? err.message : '删除失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开编辑对话框
  const openEditDialog = (member?: FamilyMember) => {
    setEditingMember(member || null);
    setFormData(member ? { ...member } : {
      name: '',
      relationship_type: '',
      id_type: 'id_card',
      id_number: '',
      phone: '',
      email: '',
      address: ''
    });
    setDialogOpen(true);
  };

  // 处理表单输入变化
  const handleFormChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  // 获取关系类型标签
  const getRelationshipLabel = (type: string) => {
    const relationship = RELATIONSHIP_TYPES.find(r => r.value === type);
    return relationship ? relationship.label : type;
  };

  // 获取证件类型标签
  const getIdTypeLabel = (type: string) => {
    const idType = ID_TYPES.find(t => t.value === type);
    return idType ? idType.label : type;
  };

  useEffect(() => {
    fetchFamilyMembers();
  }, [page, searchName, filterRelationship]);

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
    <Container maxWidth="lg" sx={{ py: 4 }}>
      {/* 页面标题 */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <FamilyIcon sx={{ fontSize: 40, color: 'primary.main' }} />
        <Typography variant="h4" component="h1" fontWeight="bold">
          家属亲戚管理
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
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="搜索姓名"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
                }}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <FormControl fullWidth>
                <InputLabel>关系类型</InputLabel>
                <Select
                  value={filterRelationship}
                  label="关系类型"
                  onChange={(e) => setFilterRelationship(e.target.value)}
                >
                  <MenuItem value="">全部</MenuItem>
                  {RELATIONSHIP_TYPES.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={4}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  startIcon={<RefreshIcon />}
                  onClick={fetchFamilyMembers}
                  disabled={loading}
                >
                  刷新
                </Button>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => openEditDialog()}
                >
                  添加家属
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
            家属亲戚列表 (共 {totalCount} 条记录)
          </Typography>
          
          <TableContainer component={Paper} variant="outlined">
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>姓名</TableCell>
                  <TableCell>关系</TableCell>
                  <TableCell>证件类型</TableCell>
                  <TableCell>证件号码</TableCell>
                  <TableCell>联系电话</TableCell>
                  <TableCell>邮箱</TableCell>
                  <TableCell>操作</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {familyMembers.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <PersonIcon sx={{ color: 'text.secondary' }} />
                        {member.name}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={getRelationshipLabel(member.relationship_type)}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>{getIdTypeLabel(member.id_type)}</TableCell>
                    <TableCell>{member.id_number}</TableCell>
                    <TableCell>{member.phone || '-'}</TableCell>
                    <TableCell>{member.email || '-'}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 1 }}>
                        <Tooltip title="编辑">
                          <IconButton
                            size="small"
                            onClick={() => openEditDialog(member)}
                            color="primary"
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="删除">
                          <IconButton
                            size="small"
                            onClick={() => deleteFamilyMember(member.id!)}
                            color="error"
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
                {familyMembers.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
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
          {editingMember ? '编辑家属亲戚' : '添加家属亲戚'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="姓名 *"
                value={formData.name || ''}
                onChange={(e) => handleFormChange('name', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>关系类型</InputLabel>
                <Select
                  value={formData.relationship_type || ''}
                  label="关系类型"
                  onChange={(e) => handleFormChange('relationship_type', e.target.value)}
                >
                  {RELATIONSHIP_TYPES.map(type => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth required>
                <InputLabel>证件类型</InputLabel>
                <Select
                  value={formData.id_type || 'id_card'}
                  label="证件类型"
                  onChange={(e) => handleFormChange('id_type', e.target.value)}
                >
                  {ID_TYPES.map(type => (
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
                label="证件号码 *"
                value={formData.id_number || ''}
                onChange={(e) => handleFormChange('id_number', e.target.value)}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="联系电话"
                value={formData.phone || ''}
                onChange={(e) => handleFormChange('phone', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="邮箱"
                type="email"
                value={formData.email || ''}
                onChange={(e) => handleFormChange('email', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="地址"
                value={formData.address || ''}
                onChange={(e) => handleFormChange('address', e.target.value)}
                multiline
                rows={2}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="QQ号"
                value={formData.qq || ''}
                onChange={(e) => handleFormChange('qq', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="微信号"
                value={formData.wechat || ''}
                onChange={(e) => handleFormChange('wechat', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField
                fullWidth
                label="支付宝账号"
                value={formData.alipay_account || ''}
                onChange={(e) => handleFormChange('alipay_account', e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="银行账号"
                value={formData.bank_account || ''}
                onChange={(e) => handleFormChange('bank_account', e.target.value)}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>取消</Button>
          <Button 
            onClick={saveFamilyMember} 
            variant="contained"
            disabled={!formData.name || !formData.relationship_type || !formData.id_number || loading}
          >
            {loading ? '保存中...' : '保存'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default FamilyMemberPage;