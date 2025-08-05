import React, { useState, useEffect } from 'react'
import {
  Modal,
  Form,
  Input,
  Select,
  Button,
  Row,
  Col,
  message,
  Space,
  Divider
} from 'antd'
import { PlusOutlined, UserOutlined } from '@ant-design/icons'
import { investorService, InvestorCreate, InvestorResponse } from '../services/investorService'

const { Option } = Select
const { TextArea } = Input

interface InvestorFormProps {
  visible: boolean
  onCancel: () => void
  onSuccess: (investor: InvestorResponse) => void
  editingInvestor?: InvestorResponse | null
}

const InvestorForm: React.FC<InvestorFormProps> = ({
  visible,
  onCancel,
  onSuccess,
  editingInvestor
}) => {
  const [form] = Form.useForm()
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (visible) {
      if (editingInvestor) {
        form.setFieldsValue(editingInvestor)
      } else {
        form.resetFields()
      }
    }
  }, [visible, editingInvestor, form])

  const handleSubmit = async (values: InvestorCreate) => {
    setLoading(true)
    try {
      let result: InvestorResponse
      if (editingInvestor) {
        result = await investorService.updateInvestor(editingInvestor.id, values)
        message.success('投资人信息更新成功')
      } else {
        result = await investorService.createInvestor(values)
        message.success('投资人信息创建成功')
      }
      onSuccess(result)
      form.resetFields()
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title={
        <Space>
          <UserOutlined />
          {editingInvestor ? '编辑投资人信息' : '新增投资人信息'}
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={800}
      destroyOnClose
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          id_type: 'id_card',
          relationship_type: '配偶'
        }}
      >
        <Divider orientation="left">基本信息</Divider>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="name"
              label="姓名"
              rules={[{ required: true, message: '请输入姓名' }]}
            >
              <Input placeholder="请输入投资人姓名" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="relationship_type"
              label="与从业人员关系"
              rules={[{ required: true, message: '请选择关系' }]}
            >
              <Select placeholder="请选择关系">
                <Option value="配偶">配偶</Option>
                <Option value="父母">父母</Option>
                <Option value="子女">子女</Option>
                <Option value="兄弟姐妹">兄弟姐妹</Option>
                <Option value="其他亲属">其他亲属</Option>
              </Select>
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left">证件信息</Divider>
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item
              name="id_type"
              label="证件类型"
              rules={[{ required: true, message: '请选择证件类型' }]}
            >
              <Select>
                <Option value="id_card">身份证</Option>
                <Option value="passport">护照</Option>
                <Option value="other">其他</Option>
              </Select>
            </Form.Item>
          </Col>
          <Col span={16}>
            <Form.Item
              name="id_number"
              label="证件号码"
              rules={[{ required: true, message: '请输入证件号码' }]}
            >
              <Input placeholder="请输入证件号码" />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left">联系方式</Divider>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item
              name="phone"
              label="手机号"
              rules={[
                { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号' }
              ]}
            >
              <Input placeholder="请输入手机号" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item
              name="email"
              label="邮箱"
              rules={[
                { type: 'email', message: '请输入正确的邮箱地址' }
              ]}
            >
              <Input placeholder="请输入邮箱地址" />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={24}>
            <Form.Item name="address" label="联系地址">
              <Input placeholder="请输入联系地址" />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left">网络信息</Divider>
        <Row gutter={16}>
          <Col span={8}>
            <Form.Item name="wechat" label="微信号">
              <Input placeholder="请输入微信号" />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="qq" label="QQ号">
              <Input placeholder="请输入QQ号" />
            </Form.Item>
          </Col>
          <Col span={8}>
            <Form.Item name="other_social" label="其他社交账号">
              <Input placeholder="请输入其他社交账号" />
            </Form.Item>
          </Col>
        </Row>

        <Divider orientation="left">账号信息</Divider>
        <Row gutter={16}>
          <Col span={12}>
            <Form.Item name="securities_account" label="证券账号">
              <Input placeholder="请输入证券账号" />
            </Form.Item>
          </Col>
          <Col span={12}>
            <Form.Item name="bank_name" label="开户银行">
              <Input placeholder="请输入开户银行" />
            </Form.Item>
          </Col>
        </Row>
        <Row gutter={16}>
          <Col span={24}>
            <Form.Item name="bank_account" label="银行账号">
              <Input placeholder="请输入银行账号" />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item name="notes" label="备注">
          <TextArea rows={3} placeholder="请输入备注信息" />
        </Form.Item>

        <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
          <Space>
            <Button onClick={onCancel}>
              取消
            </Button>
            <Button type="primary" htmlType="submit" loading={loading}>
              {editingInvestor ? '更新' : '创建'}
            </Button>
          </Space>
        </Form.Item>
      </Form>
    </Modal>
  )
}

export default InvestorForm