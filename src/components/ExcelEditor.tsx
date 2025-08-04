import React, { useEffect, useRef, useState } from 'react'
import { Button, message, Spin, Card } from 'antd'
import { DownloadOutlined, SaveOutlined } from '@ant-design/icons'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import { saveExcelData } from '../services/api'

interface ExcelEditorProps {
  excelUrl?: string
  fileName?: string
  onSave?: (data: any[][]) => void
}

const ExcelEditor: React.FC<ExcelEditorProps> = ({ excelUrl, fileName, onSave }) => {
  const [loading, setLoading] = useState(false)
  const [excelData, setExcelData] = useState<any[][]>([])
  const [workbook, setWorkbook] = useState<XLSX.WorkBook | null>(null)
  const [currentSheet, setCurrentSheet] = useState<string>('')
  const tableRef = useRef<HTMLDivElement>(null)

  // 加载Excel文件
  useEffect(() => {
    if (excelUrl) {
      loadExcelFile(excelUrl)
    }
  }, [excelUrl])

  const loadExcelFile = async (url: string) => {
    setLoading(true)
    try {
      const response = await fetch(url)
      const arrayBuffer = await response.arrayBuffer()
      const wb = XLSX.read(arrayBuffer, { type: 'array' })
      setWorkbook(wb)
      
      // 获取第一个工作表
      const firstSheetName = wb.SheetNames[0]
      setCurrentSheet(firstSheetName)
      
      // 转换为数组格式
      const worksheet = wb.Sheets[firstSheetName]
      const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1, defval: '' })
      setExcelData(jsonData as any[][])
      
      message.success('Excel文件加载成功')
    } catch (error) {
      console.error('加载Excel文件失败:', error)
      message.error('加载Excel文件失败')
    } finally {
      setLoading(false)
    }
  }

  // 处理单元格编辑
  const handleCellEdit = (rowIndex: number, colIndex: number, value: string) => {
    const newData = [...excelData]
    if (!newData[rowIndex]) {
      newData[rowIndex] = []
    }
    newData[rowIndex][colIndex] = value
    setExcelData(newData)
  }

  // 保存Excel数据
  const handleSave = async () => {
    try {
      setLoading(true)
      await saveExcelData({
        fileName: fileName || 'edited_excel.xlsx',
        data: excelData,
        sheets: workbook?.SheetNames
      })
      message.success('Excel数据保存成功')
      onSave?.(excelData)
    } catch (error) {
      console.error('保存失败:', error)
      message.error('保存失败')
    } finally {
      setLoading(false)
    }
  }

  // 下载Excel文件
  const handleDownload = () => {
    try {
      // 创建新的工作簿
      const wb = XLSX.utils.book_new()
      const ws = XLSX.utils.aoa_to_sheet(excelData)
      XLSX.utils.book_append_sheet(wb, ws, currentSheet || 'Sheet1')
      
      // 生成Excel文件
      const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
      const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
      
      // 下载文件
      saveAs(blob, fileName || 'edited_excel.xlsx')
      message.success('文件下载成功')
    } catch (error) {
      console.error('下载失败:', error)
      message.error('下载失败')
    }
  }

  // 渲染Excel表格
  const renderTable = () => {
    if (!excelData.length) {
      return (
        <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
          暂无数据
        </div>
      )
    }

    const maxCols = Math.max(...excelData.map(row => row?.length || 0))
    
    return (
      <div className="excel-table-container" style={{ overflow: 'auto', maxHeight: '500px' }}>
        <table 
          style={{ 
            width: '100%', 
            borderCollapse: 'collapse',
            fontSize: '12px'
          }}
        >
          <tbody>
            {excelData.map((row, rowIndex) => (
              <tr key={rowIndex}>
                {Array.from({ length: maxCols }, (_, colIndex) => (
                  <td
                    key={colIndex}
                    style={{
                      border: '1px solid #d9d9d9',
                      padding: '4px 8px',
                      minWidth: '80px',
                      maxWidth: '200px'
                    }}
                  >
                    <input
                      type="text"
                      value={row?.[colIndex] || ''}
                      onChange={(e) => handleCellEdit(rowIndex, colIndex, e.target.value)}
                      style={{
                        width: '100%',
                        border: 'none',
                        outline: 'none',
                        background: 'transparent',
                        fontSize: '12px'
                      }}
                    />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )
  }

  return (
    <Card 
      title={`Excel编辑器 - ${fileName || '未命名文件'}`}
      extra={
        <div className="action-buttons">
          <Button 
            type="primary" 
            icon={<SaveOutlined />} 
            onClick={handleSave}
            loading={loading}
          >
            保存
          </Button>
          <Button 
            icon={<DownloadOutlined />} 
            onClick={handleDownload}
          >
            下载
          </Button>
        </div>
      }
    >
      <Spin spinning={loading}>
        <div ref={tableRef} className="excel-editor-container">
          {renderTable()}
        </div>
      </Spin>
    </Card>
  )
}

export default ExcelEditor