import React, { useState } from 'react'
import { 
  Upload, 
  Button, 
  Card, 
  App, 
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
const { Title, Text } = Typography

interface FileUploadProps {
  onUploadSuccess: (excelUrl: string, fileName: string) => void
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadSuccess }) => {
  const { message } = App.useApp()
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
  const handleSubmit = async () => {
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
          name: '',
          relationship: '',
          idNumber: '',
          phone: '',
          description: ''
        }
      }

      const response = await uploadFileAndGetExcel(uploadData)
      
      if (response.success && response.excelUrl) {
        message.success(response.message || '文件上传成功')
        onUploadSuccess(response.excelUrl, response.fileName || 'result.xlsx')
        
        // 重置文件列表
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
    <Card title="文件上传" className="file-upload-card">
      <div style={{ textAlign: 'center' }}>
        <Title level={5}>上传证券交易截图或PDF文件</Title>
        <Dragger
          fileList={fileList}
          onChange={handleFileChange}
          beforeUpload={beforeUpload}
          accept="image/*,.pdf"
          maxCount={1}
          style={{ marginBottom: 16, maxWidth: 600, margin: '0 auto 16px auto' }}
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
          <Card size="small" style={{ marginTop: 8, maxWidth: 400, margin: '8px auto' }}>
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

        {/* 提交按钮 */}
        <div style={{ marginTop: 24 }}>
          <Button 
            type="primary" 
            size="large"
            onClick={handleSubmit}
            loading={uploading}
            icon={<UploadOutlined />}
            style={{ minWidth: 120 }}
            disabled={fileList.length === 0}
          >
            {uploading ? '处理中...' : '上传并处理'}
          </Button>
        </div>
      </div>
    </Card>
  )
}

export default FileUpload