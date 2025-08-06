import React from 'react'
import { Card, Typography } from 'antd'
import ExcelEditor from '../components/ExcelEditor'

const { Title, Paragraph } = Typography

const QuarterlyReportPage: React.FC = () => {
  const handleSave = (data: any[][]) => {
    console.log('季度投资报告已保存:', data)
  }

  return (
    <div style={{ padding: '24px' }}>
      <Card style={{ marginBottom: '24px' }}>
        <Title level={2}>季度投资报告管理</Title>
        <Paragraph>
          在这里您可以查看、编辑和保存季度投资报告。系统会自动加载 QuarterlyInvestmentReport.xlsx 文件，
          您可以在线编辑数据并将结果保存到数据库中。
        </Paragraph>
      </Card>
      
      <ExcelEditor
        investorId={1}
        quarter="2024Q1"
        year={2024}
        showDatabaseSave={true}
        onSave={handleSave}
      />
    </div>
  )
}

export default QuarterlyReportPage