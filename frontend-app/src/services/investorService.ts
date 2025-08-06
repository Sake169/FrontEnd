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
  weibo?: string
  bank_account?: string
  bank_name?: string
  relationship?: string
  remarks?: string
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
  weibo?: string
  bank_account?: string
  bank_name?: string
  relationship?: string
  remarks?: string
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
  weibo?: string
  bank_account?: string
  bank_name?: string
  relationship?: string
  created_at: string
  updated_at: string
  remarks?: string
}

export interface InvestorListResponse {
  id: number
  name: string
  id_number: string
  phone?: string
  relationship?: string
  created_at: string
}

export interface InvestorStats {
  total_investors: number
  employee_username: string
}

class InvestorService {
  // 创建投资人
  async createInvestor(data: InvestorCreate): Promise<InvestorResponse> {
    const response = await api.post('/v1/family-members/', data)
    return response.data
  }

  // 获取投资人列表
  async getInvestors(params?: {
    skip?: number
    limit?: number
    search?: string
  }): Promise<InvestorListResponse[]> {
    const response = await api.get('/v1/family-members/', { params })
    return response.data.items || []
  }

  // 获取投资人详情
  async getInvestor(id: number): Promise<InvestorResponse> {
    const response = await api.get(`/v1/family-members/${id}`)
    return response.data
  }

  // 更新投资人
  async updateInvestor(id: number, data: InvestorUpdate): Promise<InvestorResponse> {
    const response = await api.put(`/v1/family-members/${id}`, data)
    return response.data
  }

  // 删除投资人
  async deleteInvestor(id: number): Promise<{ message: string }> {
    const response = await api.delete(`/v1/family-members/${id}`)
    return response.data
  }

  // 获取投资人统计
  async getInvestorStats(): Promise<InvestorStats> {
    const response = await api.get('/v1/family-members/stats/overview')
    return response.data
  }
}

export const investorService = new InvestorService()
export default investorService