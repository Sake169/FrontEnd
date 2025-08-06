import React, { useState, useEffect } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  DatePicker,
  InputNumber,
  Space,
  Popconfirm,
  Card,
  Row,
  Col,
  message,
  Tag,
  Tooltip
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  SearchOutlined,
  ReloadOutlined,
  FileTextOutlined
} from '@ant-design/icons'
import type { ColumnsType } from 'antd/es/table'
import dayjs from 'dayjs'
import {
  investmentRecordService,
  InvestmentRecord,
  InvestmentRecordCreate,
  InvestmentRecordUpdate,
  InvestmentRecordQueryParams
} from '../services/investmentRecordService'

const { Option } = Select
const { RangePicker } = DatePicker

const InvestmentRecords: React.FC = () => {
  const [records, setRecords] = useState<InvestmentRecord[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingRecord, setEditingRecord] = useState<InvestmentRecord | null>(null)
  const [form] = Form.useForm()
  const [searchForm] = Form.useForm()
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0
  })

  // 证券类型选项
  const securitiesTypes = [
    { value: '股票', label: '股票' },
    { value: '基金', label: '基金' },
    { value: '债券', label: '债券' },
    { value: '理财产品', label: '理财产品' },
    { value: '其他', label: '其他' }
  ]

  // 交易类型选项
  const transactionTypes = [
    { value: '买入', label: '买入' },
    { value: '卖出', label: '卖出' },
    { value: '持仓', label: '持仓' },
    { value: '分红', label: '分红' },
    { value: '配股', label: '配股' }
  ]

  // 表格列定义
  const columns: ColumnsType<InvestmentRecord> = [
    {
      title: '投资人身份证号',
      dataIndex: 'investor_id_number',
      key: 'investor_id_number',
      width: 150,
      render: (text: string) => (
        <Tooltip title={text}>
          <span>{text?.replace(/(\d{6})\d{8}(\d{4})/, '$1****$2')}</span>
        </Tooltip>
      )
    },
    {
      title: '证券代码',
      dataIndex: 'securities_code',
      key: 'securities_code',
      width: 100
    },
    {
      title: '证券名称',
      dataIndex: 'securities_name',
      key: 'securities_name',
      width: 150,
      ellipsis: true
    },
    {
      title: '证券类型',
      dataIndex: 'securities_type',
      key: 'securities_type',
      width: 100,
      render: (type: string) => (
        <Tag color={getTypeColor(type)}>{type}</Tag>
      )
    },
    {
      title: '交易类型',
      dataIndex: 'transaction_type',
      key: 'transaction_type',
      width: 100,
      render: (type: string) => (
        <Tag color={getTransactionColor(type)}>{type}</Tag>
      )
    },
    {
      title: '交易日期',
      dataIndex: 'transaction_date',
      key: 'transaction_date',
      width: 120,
      render: (date: string) => date ? dayjs(date).format('YYYY-MM-DD') : '-'
    },
    {
      title: '数量',
      dataIndex: 'quantity',
      key: 'quantity',
      width: 100,
      align: 'right',
      render: (value: number) => value ? value.toLocaleString() : '-'
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      align: 'right',
      render: (value: number) => value ? `¥${value.toFixed(2)}` : '-'
    },
    {
      title: '金额',
      dataIndex: 'amount',
      key: 'amount',
      width: 120,
      align: 'right',
      render: (value: number) => value ? `¥${value.toLocaleString()}` : '-'
    },
    {
      title: '持仓数量',
      dataIndex: 'holding_quantity',
      key: 'holding_quantity',
      width: 100,
      align: 'right',
      render: (value: number) => value ? value.toLocaleString() : '-'
    },
    {
      title: '市值',
      dataIndex: 'market_value',
      key: 'market_value',
      width: 120,
      align: 'right',
      render: (value: number) => value ? `¥${value.toLocaleString()}` : '-'
    },
    {
      title: '报告期间',
      dataIndex: 'report_period',
      key: 'report_period',
      width: 120
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      fixed: 'right',
      render: (_, record) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这条投资记录吗？"
            onConfirm={() => handleDelete(record.id)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  // 获取类型颜色
  const getTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      '股票': 'red',
      '基金': 'blue',
      '债券': 'green',
      '理财产品': 'orange',
      '其他': 'default'
    }
    return colors[type] || 'default'
  }

  // 获取交易类型颜色
  const getTransactionColor = (type: string) => {
    const colors: { [key: string]: string } = {
      '买入': 'red',
      '卖出': 'green',
      '持仓': 'blue',
      '分红': 'orange',
      '配股': 'purple'
    }
    return colors[type] || 'default'
  }

  // 加载投资记录列表
  const loadRecords = async (params: InvestmentRecordQueryParams = {}) => {
    setLoading(true)
    try {
      const response = await investmentRecordService.getRecords({
        page: pagination.current,
        size: pagination.pageSize,
        ...params
      })
      setRecords(response.items)
      setPagination(prev => ({
        ...prev,
        total: response.total
      }))
    } catch (error) {
      console.error('加载投资记录失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // 搜索
  const handleSearch = () => {
    const values = searchForm.getFieldsValue()
    setPagination(prev => ({ ...prev, current: 1 }))
    loadRecords(values)
  }

  // 重置搜索
  const handleReset = () => {
    searchForm.resetFields()
    setPagination(prev => ({ ...prev, current: 1 }))
    loadRecords()
  }

  // 新增记录
  const handleAdd = () => {
    setEditingRecord(null)
    form.resetFields()
    setModalVisible(true)
  }

  // 编辑记录
  const handleEdit = (record: InvestmentRecord) => {
    setEditingRecord(record)
    form.setFieldsValue({
      ...record,
      transaction_date: record.transaction_date ? dayjs(record.transaction_date) : null
    })
    setModalVisible(true)
  }

  // 删除记录
  const handleDelete = async (id: number) => {
    try {
      await investmentRecordService.deleteRecord(id)
      loadRecords()
    } catch (error) {
      console.error('删除投资记录失败:', error)
    }
  }

  // 保存记录
  const handleSave = async () => {
    try {
      const values = await form.validateFields()
      const formData = {
        ...values,
        transaction_date: values.transaction_date ? values.transaction_date.format('YYYY-MM-DD') : null
      }

      if (editingRecord) {
        await investmentRecordService.updateRecord(editingRecord.id, formData)
      } else {
        await investmentRecordService.createRecord(formData)
      }

      setModalVisible(false)
      loadRecords()
    } catch (error) {
      console.error('保存投资记录失败:', error)
    }
  }

  // 表格分页变化
  const handleTableChange = (page: number, pageSize: number) => {
    setPagination(prev => ({
      ...prev,
      current: page,
      pageSize
    }))
  }

  useEffect(() => {
    loadRecords()
  }, [pagination.current, pagination.pageSize])

  return (
    <div style={{ padding: '24px' }}>
      <Card title="投资记录管理" extra={<FileTextOutlined />}>
        {/* 搜索表单 */}
        <Form
          form={searchForm}
          layout="inline"
          style={{ marginBottom: 16 }}
          onFinish={handleSearch}
        >
          <Form.Item name="investor_id_number" label="投资人身份证号">
            <Input placeholder="请输入身份证号" style={{ width: 200 }} />
          </Form.Item>
          <Form.Item name="securities_code" label="证券代码">
            <Input placeholder="请输入证券代码" style={{ width: 150 }} />
          </Form.Item>
          <Form.Item name="report_period" label="报告期间">
            <Input placeholder="请输入报告期间" style={{ width: 150 }} />
          </Form.Item>
          <Form.Item>
            <Space>
              <Button type="primary" htmlType="submit" icon={<SearchOutlined />}>
                搜索
              </Button>
              <Button onClick={handleReset} icon={<ReloadOutlined />}>
                重置
              </Button>
              <Button type="primary" onClick={handleAdd} icon={<PlusOutlined />}>
                新增记录
              </Button>
            </Space>
          </Form.Item>
        </Form>

        {/* 数据表格 */}
        <Table
          columns={columns}
          dataSource={records}
          rowKey="id"
          loading={loading}
          scroll={{ x: 1500 }}
          pagination={{
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: pagination.total,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
            onChange: handleTableChange,
            onShowSizeChange: handleTableChange
          }}
        />
      </Card>

      {/* 新增/编辑模态框 */}
      <Modal
        title={editingRecord ? '编辑投资记录' : '新增投资记录'}
        open={modalVisible}
        onOk={handleSave}
        onCancel={() => setModalVisible(false)}
        width={800}
        destroyOnClose
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            securities_type: '股票',
            transaction_type: '买入'
          }}
        >
          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="investor_id_number"
                label="投资人身份证号"
                rules={[{ required: true, message: '请输入投资人身份证号' }]}
              >
                <Input placeholder="请输入身份证号" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="securities_code" label="证券代码">
                <Input placeholder="请输入证券代码" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="securities_name" label="证券名称">
                <Input placeholder="请输入证券名称" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="securities_type" label="证券类型">
                <Select placeholder="请选择证券类型">
                  {securitiesTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="transaction_type" label="交易类型">
                <Select placeholder="请选择交易类型">
                  {transactionTypes.map(type => (
                    <Option key={type.value} value={type.value}>
                      {type.label}
                    </Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="transaction_date" label="交易日期">
                <DatePicker style={{ width: '100%' }} placeholder="请选择交易日期" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="quantity" label="交易数量">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入数量"
                  min={0}
                  precision={4}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="price" label="交易价格">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入价格"
                  min={0}
                  precision={4}
                  addonBefore="¥"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="amount" label="交易金额">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入金额"
                  min={0}
                  precision={2}
                  addonBefore="¥"
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={8}>
              <Form.Item name="holding_quantity" label="持仓数量">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入持仓数量"
                  min={0}
                  precision={4}
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="market_value" label="市值">
                <InputNumber
                  style={{ width: '100%' }}
                  placeholder="请输入市值"
                  min={0}
                  precision={2}
                  addonBefore="¥"
                />
              </Form.Item>
            </Col>
            <Col span={8}>
              <Form.Item name="report_period" label="报告期间">
                <Input placeholder="如：2024Q1" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="source_file" label="来源文件">
            <Input placeholder="请输入来源文件名" />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}

export default InvestmentRecords