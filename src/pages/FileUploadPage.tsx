import React, { useState } from 'react'
import { Card, Steps, Divider, Alert, Space, Typography } from 'antd'
import { 
  UploadOutlined, 
  FileExcelOutlined, 
  CheckCircleOutlined 
} from '@ant-design/icons'
import FileUpload from '../components/FileUpload'
import ExcelEditor from '../components/ExcelEditor'

const { Title, Paragraph } = Typography

const FileUploadPage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0)
  const [excelUrl, setExcelUrl] = useState<string>('')
  const [fileName, setFileName] = useState<string>('')

  // 处理上传成功
  const handleUploadSuccess = (url: string, name: string) => {
    setExcelUrl(url)
    setFileName(name)
    setCurrentStep(1)
  }

  // 处理Excel保存
  const handleExcelSave = (data: any[][]) => {
    console.log('Excel数据已保存:', data)
    setCurrentStep(2)
  }

  // 重新开始
  const handleRestart = () => {
    setCurrentStep(0)
    setExcelUrl('')
    setFileName('')
  }

  const steps = [
    {
      title: '上传文件',
      description: '上传证券交易截图或PDF文件，并填写相关人员信息',
      icon: <UploadOutlined />
    },
    {
      title: '编辑Excel',
      description: '查看和编辑系统生成的Excel文件',
      icon: <FileExcelOutlined />
    },
    {
      title: '完成',
      description: '文件处理完成，可以下载最终结果',
      icon: <CheckCircleOutlined />
    }
  ]

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 16px' }}>
      {/* 页面标题和说明 */}
      <Card style={{ marginBottom: 24 }}>
        <Title level={2} style={{ textAlign: 'center', marginBottom: 16 }}>
          证券公司员工配偶信息报备系统
        </Title>
        <Paragraph style={{ textAlign: 'center', fontSize: '16px', color: '#666' }}>
          上传配偶或利害关系人的证券交易截图，系统将自动识别并生成Excel报表
        </Paragraph>
        
        <Alert
          message="系统说明"
          description={
            <div>
              <p>• 支持上传图片格式（JPG、PNG、GIF等）和PDF文件</p>
              <p>• 系统将使用AI模型识别交易信息并生成结构化Excel文件</p>
              <p>• 生成的Excel文件支持在线编辑和下载</p>
              <p>• 请确保上传的文件清晰可读，包含完整的交易信息</p>
            </div>
          }
          type="info"
          showIcon
          style={{ marginTop: 16 }}
        />
      </Card>

      {/* 步骤指示器 */}
      <Card style={{ marginBottom: 24 }}>
        <Steps
          current={currentStep}
          items={steps}
          size="small"
        />
      </Card>

      {/* 主要内容区域 */}
      <div style={{ minHeight: '500px' }}>
        {currentStep === 0 && (
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        )}

        {currentStep === 1 && (
          <div>
            <ExcelEditor 
              excelUrl={excelUrl}
              fileName={fileName}
              onSave={handleExcelSave}
            />
            <Card style={{ marginTop: 16, textAlign: 'center' }}>
              <Space>
                <span>如需重新上传文件，请</span>
                <a onClick={handleRestart}>点击这里</a>
              </Space>
            </Card>
          </div>
        )}

        {currentStep === 2 && (
          <Card>
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <CheckCircleOutlined 
                style={{ fontSize: '64px', color: '#52c41a', marginBottom: 16 }} 
              />
              <Title level={3} style={{ color: '#52c41a' }}>
                处理完成！
              </Title>
              <Paragraph style={{ fontSize: '16px', marginBottom: 24 }}>
                文件已成功处理并保存，您可以继续编辑或下载最终文件。
              </Paragraph>
              <Space size="large">
                <a onClick={() => setCurrentStep(1)}>继续编辑</a>
                <Divider type="vertical" />
                <a onClick={handleRestart}>处理新文件</a>
              </Space>
            </div>
          </Card>
        )}
      </div>

      {/* 页脚信息 */}
      <Card style={{ marginTop: 24, textAlign: 'center' }}>
        <Paragraph type="secondary" style={{ margin: 0 }}>
          证券公司员工配偶信息报备系统 v1.0 | 技术支持：AI智能识别
        </Paragraph>
      </Card>
    </div>
  )
}

export default FileUploadPage