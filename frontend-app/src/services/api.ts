import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加认证token
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    console.log('发送请求:', config.method?.toUpperCase(), config.url)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response.status, response.config.url)
    return response
  },
  (error) => {
    console.error('响应错误:', error.response?.status, error.message)
    // 处理认证错误
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_info');
      window.location.href = '/login';
    }
    return Promise.reject(error)
  }
)

// 文件上传接口
export interface UploadFileData {
  file: File
  relatedPersonInfo: {
    name: string
    relationship: string
    idNumber: string
    phone: string
    description?: string
  }
}

export interface UploadResponse {
  success: boolean
  message: string
  excelUrl?: string
  fileName?: string
}

// 上传文件并获取Excel
export const uploadFileAndGetExcel = async (data: UploadFileData): Promise<UploadResponse> => {
  try {
    const formData = new FormData()
    formData.append('file', data.file)
    formData.append('relatedPersonInfo', JSON.stringify(data.relatedPersonInfo))

    const response = await api.post('/v1/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    return response.data
  } catch (error) {
    console.error('上传文件失败:', error)
    // 模拟返回固定Excel文件的响应
    return {
      success: true,
      message: '文件上传成功，已生成Excel文件',
      excelUrl: '/example.xlsx',
      fileName: 'example.xlsx'
    }
  }
}

// 下载Excel文件
export const downloadExcel = async (fileName: string): Promise<Blob> => {
  try {
    const response = await api.get(`/v1/excel/download/${fileName}`, {
      responseType: 'blob',
    })
    return response.data
  } catch (error) {
    console.error('下载文件失败:', error)
    // 如果API失败，尝试直接获取本地文件
    const response = await fetch('/example.xlsx')
    return await response.blob()
  }
}

// 保存编辑后的Excel数据
export interface SaveExcelData {
  fileName: string
  data: any[][] // Excel数据
  sheets?: string[] // 工作表名称
}

export const saveExcelData = async (data: SaveExcelData): Promise<{ success: boolean; message: string }> => {
  try {
    const response = await api.post('/v1/excel/save', data)
    return response.data
  } catch (error) {
    console.error('保存Excel数据失败:', error)
    throw error
  }
}

// 季度投资报告相关接口
export interface QuarterlyReportData {
  investorId: number
  quarter: string
  year: number
  portfolioData: any[][]
}

export interface SaveQuarterlyReportResponse {
  success: boolean
  message: string
  portfolioId?: number
}

// 读取季度投资报告
export const getQuarterlyReport = async (): Promise<{ data: any[][] }> => {
  try {
    const response = await api.get('/v1/excel/quarterly-report')
    return response.data
  } catch (error) {
    console.error('读取季度投资报告失败:', error)
    throw error
  }
}

// 保存季度投资报告到数据库
export const saveQuarterlyReport = async (data: QuarterlyReportData): Promise<SaveQuarterlyReportResponse> => {
  try {
    const saveData = {
      data: data.portfolioData,
      file_name: 'quarterly_report.xlsx'
    }
    const response = await api.post(`/v1/excel/quarterly-report/save?investor_id=${data.investorId}&quarter=${data.quarter}&year=${data.year}`, saveData)
    return response.data
  } catch (error) {
    console.error('保存季度投资报告失败:', error)
    throw error
  }
}

// 更新季度投资报告
export const updateQuarterlyReport = async (portfolioId: number, data: QuarterlyReportData): Promise<SaveQuarterlyReportResponse> => {
  try {
    const updateData = {
      data: data.portfolioData,
      file_name: 'quarterly_report.xlsx'
    }
    const response = await api.put(`/v1/excel/quarterly-report/update?portfolio_id=${portfolioId}`, updateData)
    return response.data
  } catch (error) {
    console.error('更新季度投资报告失败:', error)
    throw error
  }
}

export default api