import React, { useState, useEffect } from 'react'
import {
  Card,
  Select,
  Button,
  Space,
  Typography,
  Tag,
  message,
  Spin,
  Empty,
  Row,
  Col
} from 'antd'
import { PlusOutlined, UserOutlined, EditOutlined } from '@ant-design/icons'
import InvestorForm from './InvestorForm'
import { investorService, InvestorListResponse, InvestorResponse } from '../services/investorService'

const { Option } = Select
const { Text } = Typography

interface InvestorSelectorProps {
  selectedInvestor?: InvestorResponse | null
  onInvestorChange: (investor: InvestorResponse | null) => void
}

const InvestorSelector: React.FC<InvestorSelectorProps> = ({
  selectedInvestor,
  onInvestorChange
}) => {
  const [investors, setInvestors] = useState<InvestorListResponse[]>([])
  const [loading, setLoading] = useState(false)
  const [formVisible, setFormVisible] = useState(false)
  const [editingInvestor, setEditingInvestor] = useState<InvestorResponse | null>(null)

  // 加载投资人列表
  const loadInvestors = async () => {
    setLoading(true)
    try {
      const data = await investorService.getInvestors()
      setInvestors(data)
    } catch (error: any) {
      message.error('加载投资人列表失败')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadInvestors()
  }, [])

  // 处理投资人选择
  const handleInvestorSelect = async (investorId: number | null) => {
    if (!investorId) {
      onInvestorChange(null)
      return
    }

    try {
      const investor = await investorService.getInvestor(investorId)
      onInvestorChange(investor)
    } catch (error: any) {
      message.error('获取投资人详情失败')
    }
  }

  // 处理新增投资人
  const handleAddInvestor = () => {
    setEditingInvestor(null)
    setFormVisible(true)
  }

  // 处理编辑投资人
  const handleEditInvestor = async () => {
    if (!selectedInvestor) return
    
    try {
      const investor = await investorService.getInvestor(selectedInvestor.id)
      setEditingInvestor(investor)
      setFormVisible(true)
    } catch (error: any) {
      message.error('获取投资人详情失败')
    }
  }

  // 处理表单成功
  const handleFormSuccess = (investor: InvestorResponse) => {
    setFormVisible(false)
    setEditingInvestor(null)
    loadInvestors()
    onInvestorChange(investor)
  }

  // 处理表单取消
  const handleFormCancel = () => {
    setFormVisible(false)
    setEditingInvestor(null)
  }

  // 获取证件类型显示文本
  const getIdTypeText = (idType: string) => {
    const typeMap: Record<string, string> = {
      'id_card': '身份证',
      'passport': '护照',
      'other': '其他'
    }
    return typeMap[idType] || idType
  }

  return (
    <Card
      title={
        <Space>
          <UserOutlined />
          <span>投资人信息</span>
        </Space>
      }
      size="small"
      style={{ marginBottom: 16 }}
    >
      <Row gutter={16} align="middle">
        <Col flex="auto">
          <Select
            style={{ width: '100%' }}
            placeholder="请选择投资人或新增投资人"
            value={selectedInvestor?.id}
            onChange={handleInvestorSelect}
            loading={loading}
            allowClear
            showSearch
            optionFilterProp="children"
            filterOption={(input, option) => {
              if (!option?.value) return false
              const investor = investors.find(inv => inv.id === option.value)
              if (!investor) return false
              return investor.name.toLowerCase().includes(input.toLowerCase()) ||
                     investor.id_number.toLowerCase().includes(input.toLowerCase())
            }}
            notFoundContent={loading ? <Spin size="small" /> : <Empty description="暂无投资人" />}
          >
            {investors.map(investor => (
              <Option key={investor.id} value={investor.id}>
                <Space>
                  <Text strong>{investor.name}</Text>
                  <Text type="secondary">({investor.id_number})</Text>
                  {investor.relationship && (
                     <Tag>{investor.relationship}</Tag>
                   )}
                </Space>
              </Option>
            ))}
          </Select>
        </Col>
        <Col>
          <Space>
            <Button
              type="primary"
              icon={<PlusOutlined />}
              onClick={handleAddInvestor}
              size="small"
            >
              新增投资人
            </Button>
            {selectedInvestor && (
              <Button
                icon={<EditOutlined />}
                onClick={handleEditInvestor}
                size="small"
              >
                编辑
              </Button>
            )}
          </Space>
        </Col>
      </Row>

      {/* 显示选中的投资人信息 */}
      {selectedInvestor && (
        <Card size="small" style={{ marginTop: 12, backgroundColor: '#f8f9fa' }}>
          <Row gutter={[16, 8]}>
            <Col span={12}>
              <Text strong>姓名：</Text>
              <Text>{selectedInvestor.name}</Text>
            </Col>
            <Col span={12}>
              <Text strong>关系：</Text>
              <Text>{selectedInvestor.relationship || '未填写'}</Text>
            </Col>
            <Col span={12}>
              <Text strong>证件类型：</Text>
              <Text>{getIdTypeText(selectedInvestor.id_type)}</Text>
            </Col>
            <Col span={12}>
              <Text strong>证件号码：</Text>
              <Text>{selectedInvestor.id_number}</Text>
            </Col>
            {selectedInvestor.phone && (
              <Col span={12}>
                <Text strong>手机号：</Text>
                <Text>{selectedInvestor.phone}</Text>
              </Col>
            )}
            {selectedInvestor.bank_account && (
              <Col span={12}>
                <Text strong>银行账号：</Text>
                <Text>{selectedInvestor.bank_account}</Text>
              </Col>
            )}
          </Row>
        </Card>
      )}

      {/* 投资人表单弹窗 */}
      <InvestorForm
        visible={formVisible}
        onCancel={handleFormCancel}
        onSuccess={handleFormSuccess}
        editingInvestor={editingInvestor}
      />
    </Card>
  )
}

export default InvestorSelector