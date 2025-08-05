import api from './api'

export interface InvestorCreate {
  name: string
  id_type: 'id_card' | 'passport' | 'other'
  id_number: string
  phone?: string
  email?: string
  address?: string
  wechat?: string
  qq?: string
  other_social?: string
  securities_account?: string
  bank_account?: string
  bank_name?: string
  relationship_type?: string
  notes?: string
}

export interface InvestorUpdate {
  name?: string
  id_type?: 'id_card' | 'passport' | 'other'
  id_number?: string
  phone?: string
  email?: string
  address?: string
  wechat?: string
  qq?: string
  other_social?: string
  securities_account?: string
  bank_account?: string
  bank_name?: string
  relationship_type?: string
  is_active?: boolean
  notes?: string
}

export interface InvestorResponse {
  id: number
  employee_username: string
  name: string
  id_type: 'id_card' | 'passport' | 'other'
  id_number: string
  phone?: string
  email?: string
  address?: string
  wechat?: string
  qq?: string
  other_social?: string
  securities_account?: string
  bank_account?: string
  bank_name?: string
  relationship_type?: string
  is_active: boolean
  created_at: string
  updated_at: string
  notes?: string
}

export interface InvestorListResponse {
  id: number
  name: string
  id_number: string
  phone?: string
  relationship_type?: string
  created_at: string
}

export interface InvestorStats {
  total_investors: number
  employee_username: string
}

class InvestorService {
  // 创建投资人
  async createInvestor(data: InvestorCreate): Promise<InvestorResponse> {
    const response = await api.post('/api/v1/investors/', data)
    return response.data
  }

  // 获取投资人列表
  async getInvestors(params?: {
    skip?: number
    limit?: number
    search?: string
  }): Promise<InvestorListResponse[]> {
    const response = await api.get('/api/v1/investors/', { params })
    return response.data
  }

  // 获取投资人详情
  async getInvestor(id: number): Promise<InvestorResponse> {
    const response = await api.get(`/api/v1/investors/${id}`)
    return response.data
  }

  // 更新投资人
  async updateInvestor(id: number, data: InvestorUpdate): Promise<InvestorResponse> {
    const response = await api.put(`/api/v1/investors/${id}`, data)
    return response.data
  }

  // 删除投资人
  async deleteInvestor(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/api/v1/investors/${id}`)
    return response.data
  }

  // 获取投资人统计
  async getInvestorStats(): Promise<InvestorStats> {
    const response = await api.get('/api/v1/investors/stats/summary')
    return response.data
  }
}

export const investorService = new InvestorService()
export default investorService