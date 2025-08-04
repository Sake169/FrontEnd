import React, { useState } from 'react'
import { 
  Upload, 
  Button, 
  Form, 
  Input, 
  Select, 
  Card, 
  App, 
  Row, 
  Col,
  Space,
  Typography
} from 'antd'
import { 
  UploadOutlined, 
  InboxOutlined, 
  FileImageOutlined, 
  FilePdfOutlined 
} from '@ant-design/icons'
import type { UploadFile, UploadProps } from 'antd'
import { uploadFileAndGetExcel, type UploadFileData } from '../services/api'

const { Dragger } = Upload
const { Option } = Select
const { TextArea } = Input
const { Title, Text } = Typography

interface FileUploadProps {
  onUploadSuccess: (excelUrl: string, fileName: string) => void
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const { message } = App.useApp()
  const [form] = Form.useForm()
  const [fileList, setFileList] = useState<UploadFile[]>([])
  const [uploading, setUploading] = useState(false)

  // 文件上传前的验证
  const beforeUpload = (file: File) => {
    const isValidType = file.type.startsWith('image/') || file.type === 'application/pdf'
    if (!isValidType) {
      message.error('只能上传图片或PDF文件！')
      return false
    }

    const isLt10M = file.size / 1024 / 1024 < 10
    if (!isLt10M) {
      message.error('文件大小不能超过10MB！')
      return false
    }

    return false // 阻止自动上传
  }

  // 处理文件选择
  const handleFileChange: UploadProps['onChange'] = (info) => {
    setFileList(info.fileList.slice(-1)) // 只保留最新的一个文件
  }

  // 提交表单
  const handleSubmit = async (values: any) => {
    if (fileList.length === 0) {
      message.error('请选择要上传的文件')
      return
    }

    const file = fileList[0].originFileObj as File
    if (!file) {
      message.error('文件获取失败')
      return
    }

    setUploading(true)
    try {
      const uploadData: UploadFileData = {
        file,
        relatedPersonInfo: {
          name: values.name,
          relationship: values.relationship,
          idNumber: values.idNumber,
          phone: values.phone,
          description: values.description
        }
      }

      const response = await uploadFileAndGetExcel(uploadData)
      
      if (response.success && response.excelUrl) {
        message.success(response.message || '文件上传成功')
        onUploadSuccess(response.excelUrl, response.fileName || 'result.xlsx')
        
        // 重置表单
        form.resetFields()
        setFileList([])
      } else {
        message.error(response.message || '上传失败')
      }
    } catch (error) {
      console.error('上传失败:', error)
      message.error('上传失败，请重试')
    } finally {
      setUploading(false)
    }
  }

  // 获取文件图标
  const getFileIcon = (file: UploadFile) => {
    if (file.type?.startsWith('image/')) {
      return <FileImageOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
    } else if (file.type === 'application/pdf') {
      return <FilePdfOutlined style={{ fontSize: '24px', color: '#f5222d' }} />
    }
    return <FileImageOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
  }

  return (
    <Card title="文件上传与信息填写" className="file-upload-card">
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
        initialValues={{
          relationship: 'spouse'
        }}
      >
        <Row gutter={[24, 16]}>
          {/* 文件上传区域 */}
          <Col xs={24} lg={12}>
            <Title level={5}>上传证券交易截图或PDF文件</Title>
            <Dragger
              fileList={fileList}
              onChange={handleFileChange}
              beforeUpload={beforeUpload}
              accept="image/*,.pdf"
              maxCount={1}
              style={{ marginBottom: 16 }}
            >
              <p className="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">
                支持图片格式（JPG、PNG、GIF等）和PDF文件，文件大小不超过10MB
              </p>
            </Dragger>
            
            {/* 显示已选择的文件 */}
            {fileList.length > 0 && (
              <Card size="small" style={{ marginTop: 8 }}>
                <Space>
                  {getFileIcon(fileList[0])}
                  <div>
                    <Text strong>{fileList[0].name}</Text>
                    <br />
                    <Text type="secondary">
                      {((fileList[0].size || 0) / 1024 / 1024).toFixed(2)} MB
                    </Text>
                  </div>
                </Space>
              </Card>
            )}
          </Col>

          {/* 相关人员信息填写 */}
          <Col xs={24} lg={12}>
            <Title level={5}>相关人员信息</Title>
            
            <Form.Item
              label="姓名"
              name="name"
              rules={[
                { required: true, message: '请输入姓名' },
                { min: 2, message: '姓名至少2个字符' }
              ]}
            >
              <Input placeholder="请输入相关人员姓名" />
            </Form.Item>

            <Form.Item
              label="关系"
              name="relationship"
              rules={[{ required: true, message: '请选择关系' }]}
            >
              <Select placeholder="请选择与员工的关系">
                <Option value="spouse">配偶</Option>
                <Option value="child">子女</Option>
                <Option value="parent">父母</Option>
                <Option value="sibling">兄弟姐妹</Option>
                <Option value="other">其他利害关系人</Option>
              </Select>
            </Form.Item>

            <Form.Item
              label="证件号码"
              name="idNumber"
              rules={[
                { required: true, message: '请输入证件号码' },
                { 
                  pattern: /^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$/,
                  message: '请输入正确的身份证号码'
                }
              ]}
            >
              <Input placeholder="请输入身份证号码" />
            </Form.Item>

            <Form.Item
              label="联系电话"
              name="phone"
              rules={[
                { required: true, message: '请输入联系电话' },
                { 
                  pattern: /^1[3-9]\d{9}$/,
                  message: '请输入正确的手机号码'
                }
              ]}
            >
              <Input placeholder="请输入手机号码" />
            </Form.Item>

            <Form.Item
              label="备注说明"
              name="description"
            >
              <TextArea 
                rows={3} 
                placeholder="请输入相关说明信息（选填）"
                maxLength={200}
                showCount
              />
            </Form.Item>
          </Col>
        </Row>

        {/* 提交按钮 */}
        <Row>
          <Col span={24} style={{ textAlign: 'center', marginTop: 24 }}>
            <Button 
              type="primary" 
              size="large"
              htmlType="submit" 
              loading={uploading}
              icon={<UploadOutlined />}
              style={{ minWidth: 120 }}
            >
              {uploading ? '处理中...' : '上传并处理'}
            </Button>
          </Col>
        </Row>
      </Form>
    </Card>
  )
}

export default FileUpload