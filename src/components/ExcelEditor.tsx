import React, { useEffect, useRef, useState, useMemo } from 'react'
import { Button, App, Spin, Card } from 'antd'
import { DownloadOutlined, SaveOutlined } from '@ant-design/icons'
import { AgGridReact } from 'ag-grid-react'
import { ModuleRegistry, AllCommunityModule } from 'ag-grid-community'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import { saveExcelData } from '../services/api'
import type { ColDef, GridReadyEvent, CellValueChangedEvent } from 'ag-grid-community'

// 注册AG Grid模块
ModuleRegistry.registerModules([AllCommunityModule])

interface ExcelEditorProps {
  excelUrl?: string
  fileName?: string
  onSave?: (data: any[][]) => void
}

const ExcelEditor: React.FC<ExcelEditorProps> = ({ excelUrl, fileName, onSave }) => {
  const { message } = App.useApp()
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
      // 构建完整的URL
      const fullUrl = url.startsWith('http') ? url : `http://localhost:8000${url}`
      
      const response = await fetch(fullUrl)
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
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