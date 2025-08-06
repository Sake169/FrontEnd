import { message } from 'antd'
import api from './api'

// 投资记录接口定义
export interface InvestmentRecord {
  id: number
  investor_id_number: string
  securities_code?: string
  securities_name?: string
  securities_type?: string
  transaction_type?: string
  transaction_date?: string
  quantity?: number
  price?: number
  amount?: number
  holding_quantity?: number
  market_value?: number
  report_period?: string
  source_file?: string
  created_at: string
  updated_at: string
}

export interface InvestmentRecordCreate {
  investor_id_number: string
  securities_code?: string
  securities_name?: string
  securities_type?: string
  transaction_type?: string
  transaction_date?: string
  quantity?: number
  price?: number
  amount?: number
  holding_quantity?: number
  market_value?: number
  report_period?: string
  source_file?: string
}

export interface InvestmentRecordUpdate {
  securities_code?: string
  securities_name?: string
  securities_type?: string
  transaction_type?: string
  transaction_date?: string
  quantity?: number
  price?: number
  amount?: number
  holding_quantity?: number
  market_value?: number
  report_period?: string
  source_file?: string
}

export interface InvestmentRecordListResponse {
  items: InvestmentRecord[]
  total: number
  page: number
  size: number
  pages: number
}

export interface InvestmentRecordQueryParams {
  page?: number
  size?: number
  investor_id_number?: string
  securities_code?: string
  report_period?: string
}



// 投资记录服务
export const investmentRecordService = {
  // 创建投资记录
  async createRecord(record: InvestmentRecordCreate): Promise<InvestmentRecord> {
    try {
      const response = await api.post(
        '/investment-records/',
        record
      )
      message.success('投资记录创建成功')
      return response.data
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '创建投资记录失败'
      message.error(errorMsg)
      throw error
    }
  },

  // 获取投资记录列表
  async getRecords(params: InvestmentRecordQueryParams = {}): Promise<InvestmentRecordListResponse> {
    try {
      const response = await api.get(
        '/investment-records/',
        {
          params
        }
      )
      return response.data
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '获取投资记录列表失败'
      message.error(errorMsg)
      throw error
    }
  },

  // 获取单个投资记录
  async getRecord(id: number): Promise<InvestmentRecord> {
    try {
      const response = await api.get(
        `/investment-records/${id}`
      )
      return response.data
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '获取投资记录失败'
      message.error(errorMsg)
      throw error
    }
  },

  // 更新投资记录
  async updateRecord(id: number, record: InvestmentRecordUpdate): Promise<InvestmentRecord> {
    try {
      const response = await api.put(
        `/investment-records/${id}`,
        record
      )
      message.success('投资记录更新成功')
      return response.data
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '更新投资记录失败'
      message.error(errorMsg)
      throw error
    }
  },

  // 删除投资记录
  async deleteRecord(id: number): Promise<void> {
    try {
      await api.delete(
        `/investment-records/${id}`
      )
      message.success('投资记录删除成功')
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '删除投资记录失败'
      message.error(errorMsg)
      throw error
    }
  },

  // 根据投资人身份证号获取投资记录
  async getRecordsByInvestor(investorIdNumber: string, reportPeriod?: string): Promise<InvestmentRecord[]> {
    try {
      const params = reportPeriod ? { report_period: reportPeriod } : {}
      const response = await api.get(
        `/investment-records/by-investor/${investorIdNumber}`,
        {
          params
        }
      )
      return response.data
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '获取投资人记录失败'
      message.error(errorMsg)
      throw error
    }
  },

  // 批量创建投资记录
  async createRecordsBatch(records: InvestmentRecordCreate[]): Promise<InvestmentRecord[]> {
    try {
      const response = await api.post(
        '/investment-records/batch',
        records
      )
      message.success(`成功创建 ${records.length} 条投资记录`)
      return response.data
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '批量创建投资记录失败'
      message.error(errorMsg)
      throw error
    }
  },

  // 删除指定投资人的投资记录
  async deleteRecordsByInvestor(investorIdNumber: string, reportPeriod?: string): Promise<void> {
    try {
      const params = reportPeriod ? { report_period: reportPeriod } : {}
      await api.delete(
        `/investment-records/by-investor/${investorIdNumber}`,
        {
          params
        }
      )
      message.success('投资记录删除成功')
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || '删除投资记录失败'
      message.error(errorMsg)
      throw error
    }
  }
}

export default investmentRecordService