import React, { useEffect, useRef, useState, useMemo } from 'react'
import { Button, App, Spin, Card, Space, Modal, Form, Input, InputNumber, Select } from 'antd'
import { DownloadOutlined, SaveOutlined, DatabaseOutlined, ReloadOutlined } from '@ant-design/icons'
import { AgGridReact } from 'ag-grid-react'
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import api, { saveExcelData, getQuarterlyReport, saveQuarterlyReport, updateQuarterlyReport, QuarterlyReportData } from '../services/api'
import type { ColDef, GridReadyEvent, CellValueChangedEvent } from 'ag-grid-community'

// 注册AG Grid模块
ModuleRegistry.registerModules([AllCommunityModule])

interface ExcelEditorProps {
  excelUrl?: string
  fileName?: string
  onSave?: (data: any[][]) => void
  investorId?: number
  quarter?: string
  year?: number
  portfolioId?: number
  showDatabaseSave?: boolean
}

const ExcelEditor: React.FC<ExcelEditorProps> = ({ 
  excelUrl, 
  fileName, 
  onSave,
  investorId = 1,
  quarter = '2024Q1',
  year = 2024,
  portfolioId,
  showDatabaseSave = true
}) => {
  const { message } = App.useApp()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [excelData, setExcelData] = useState<any[][]>([])
  const [workbook, setWorkbook] = useState<XLSX.WorkBook | null>(null)
  const [currentSheet, setCurrentSheet] = useState<string>('')
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [form] = Form.useForm()
  const tableRef = useRef<HTMLDivElement>(null)

  // 加载Excel文件
  useEffect(() => {
    if (excelUrl) {
      loadExcelFile(excelUrl)
    } else {
      // 如果没有提供URL，加载默认的季度报告
      loadQuarterlyReport()
    }
  }, [excelUrl])

  // 加载季度投资报告
  const loadQuarterlyReport = async () => {
    setLoading(true)
    try {
      const response = await getQuarterlyReport()
      if (response && response.data) {
        setExcelData(response.data)
        setFileName('季度投资报告')
        message.success('季度投资报告加载成功')
      }
    } catch (error) {
      console.error('加载季度投资报告失败:', error)
      message.error('加载季度投资报告失败')
    } finally {
      setLoading(false)
    }
  }

  const loadExcelFile = async (url: string) => {
    setLoading(true)
    try {
      // 使用api实例获取文件
      const response = await api.get(url, { responseType: 'arraybuffer' })
      const arrayBuffer = response.data
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
      message.error(`加载Excel文件失败: ${error instanceof Error ? error.message : '未知错误'}`)
    } finally {
      setLoading(false)
    }
  }

  // 处理单元格编辑
  const onCellValueChanged = (event: CellValueChangedEvent) => {
    // AG Grid会自动更新数据，这里可以添加额外的处理逻辑
    console.log('Cell value changed:', event)
  }

  // 转换数据为AG Grid格式
  const { rowData, columnDefs } = useMemo(() => {
    if (!excelData.length) {
      return { rowData: [], columnDefs: [] }
    }

    // 使用第一行作为列标题，如果第一行是数据则生成默认列名
    const headers = excelData[0] || []
    const hasHeaders = headers.every(header => typeof header === 'string' && header.trim() !== '')
    
    const cols: ColDef[] = []
    const maxCols = Math.max(...excelData.map(row => row?.length || 0))
    
    for (let i = 0; i < maxCols; i++) {
      const headerName = hasHeaders && headers[i] ? String(headers[i]) : `列${i + 1}`
      cols.push({
        field: `col${i}`,
        headerName,
        editable: true,
        sortable: true,
        filter: true,
        resizable: true,
        minWidth: 100,
        cellEditor: 'agTextCellEditor'
      })
    }

    // 转换行数据
    const startRow = hasHeaders ? 1 : 0
    const rows = excelData.slice(startRow).map((row, index) => {
      const rowObj: any = { id: index }
      for (let i = 0; i < maxCols; i++) {
        rowObj[`col${i}`] = row?.[i] || ''
      }
      return rowObj
    })

    return { rowData: rows, columnDefs: cols }
  }, [excelData])

  // 从AG Grid获取数据
  const getGridData = () => {
    const gridApi = gridRef.current?.api
    if (!gridApi) return []

    const allRows: any[] = []
    gridApi.forEachNode(node => {
      if (node.data) {
        allRows.push(node.data)
      }
    })

    // 转换回二维数组格式
    const headers = columnDefs.map(col => col.headerName || '')
    const dataRows = allRows.map(row => {
      return columnDefs.map(col => row[col.field || ''] || '')
    })

    return [headers, ...dataRows]
  }

  const gridRef = useRef<AgGridReact>(null)

  // 保存Excel数据
  const handleSave = async () => {
    try {
      setLoading(true)
      const currentData = getGridData()
      await saveExcelData({
        fileName: fileName || 'edited_excel.xlsx',
        data: currentData,
        sheets: workbook?.SheetNames
      })
      message.success('Excel数据保存成功')
      onSave?.(currentData)
    } catch (error) {
      console.error('保存失败:', error)
      message.error('保存失败')
    } finally {
      setLoading(false)
    }
  }

  // 保存到数据库
  const handleSaveToDatabase = async () => {
    try {
      setSaving(true)
      const currentData = getGridData()
      
      const saveData: QuarterlyReportData = {
        investorId,
        quarter,
        year,
        portfolioData: currentData
      }

      let response
      if (portfolioId) {
        // 更新现有记录
        response = await updateQuarterlyReport(portfolioId, saveData)
      } else {
        // 创建新记录
        response = await saveQuarterlyReport(saveData)
      }

      if (response.success) {
        message.success(response.message)
        onSave?.(currentData)
      }
    } catch (error) {
      console.error('保存到数据库失败:', error)
      message.error('保存到数据库失败')
    } finally {
      setSaving(false)
    }
  }

  // 显示保存配置模态框
  const showSaveModal = () => {
    form.setFieldsValue({
      investorId,
      quarter,
      year
    })
    setIsModalVisible(true)
  }

  // 处理模态框确认
  const handleModalOk = async () => {
    try {
      const values = await form.validateFields()
      setSaving(true)
      
      const currentData = getGridData()
      const saveData: QuarterlyReportData = {
        investorId: values.investorId,
        quarter: values.quarter,
        year: values.year,
        portfolioData: currentData
      }

      const response = await saveQuarterlyReport(saveData)

      if (response.success) {
        message.success(response.message)
        setIsModalVisible(false)
        onSave?.(currentData)
      }
    } catch (error) {
      console.error('保存失败:', error)
      message.error('保存失败')
    } finally {
      setSaving(false)
    }
  }

  // 处理模态框取消
  const handleModalCancel = () => {
    setIsModalVisible(false)
  }

  // 下载Excel文件
  const handleDownload = () => {
    try {
      // 获取当前表格数据
      const currentData = getGridData()
      
      // 创建新的工作簿
      const wb = XLSX.utils.book_new()
      const ws = XLSX.utils.aoa_to_sheet(currentData)
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

    return (
      <div className="ag-theme-alpine" style={{ height: '500px', width: '100%' }}>
        <AgGridReact
          ref={gridRef}
          theme="legacy"
          rowData={rowData}
          columnDefs={columnDefs}
          defaultColDef={{
            editable: true,
            sortable: true,
            filter: true,
            resizable: true,
            minWidth: 100
          }}
          onCellValueChanged={onCellValueChanged}
          suppressRowClickSelection={true}
          rowSelection="multiple"
          animateRows={true}
          undoRedoCellEditing={true}
          undoRedoCellEditingLimit={20}
        />
      </div>
    )
  }

  return (
    <>
      <Card 
        title={`Excel编辑器 - ${fileName || '季度投资报告'}`}
        extra={
          <Space>
            <Button 
              icon={<ReloadOutlined />} 
              onClick={loadQuarterlyReport}
              loading={loading}
            >
              重新加载
            </Button>
            <Button 
              type="primary" 
              icon={<SaveOutlined />} 
              onClick={handleSave}
              loading={loading}
            >
              保存文件
            </Button>
            {showDatabaseSave && (
              <Button 
                type="primary" 
                icon={<DatabaseOutlined />} 
                onClick={portfolioId ? handleSaveToDatabase : showSaveModal}
                loading={saving}
              >
                保存到数据库
              </Button>
            )}
            <Button 
              icon={<DownloadOutlined />} 
              onClick={handleDownload}
            >
              下载
            </Button>
          </Space>
        }
      >
        <Spin spinning={loading}>
          <div ref={tableRef} className="excel-editor-container">
            {renderTable()}
          </div>
        </Spin>
      </Card>

      {/* 保存配置模态框 */}
      <Modal
        title="保存到数据库"
        open={isModalVisible}
        onOk={handleModalOk}
        onCancel={handleModalCancel}
        confirmLoading={saving}
        okText="保存"
        cancelText="取消"
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            investorId,
            quarter,
            year
          }}
        >
          <Form.Item
            label="投资人ID"
            name="investorId"
            rules={[{ required: true, message: '请输入投资人ID' }]}
          >
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>
          
          <Form.Item
            label="季度"
            name="quarter"
            rules={[{ required: true, message: '请选择季度' }]}
          >
            <Select>
              <Select.Option value="2024Q1">2024年第一季度</Select.Option>
              <Select.Option value="2024Q2">2024年第二季度</Select.Option>
              <Select.Option value="2024Q3">2024年第三季度</Select.Option>
              <Select.Option value="2024Q4">2024年第四季度</Select.Option>
            </Select>
          </Form.Item>
          
          <Form.Item
            label="年份"
            name="year"
            rules={[{ required: true, message: '请输入年份' }]}
          >
            <InputNumber min={2020} max={2030} style={{ width: '100%' }} />
          </Form.Item>
        </Form>
      </Modal>
    </>
  )
}

export default ExcelEditor