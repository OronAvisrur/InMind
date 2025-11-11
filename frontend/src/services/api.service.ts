import axios, { AxiosInstance } from 'axios'
import {
  MessageRequest,
  MessageResponse,
  ConversationResponse,
  StartConversationResponse,
  HealthResponse,
  OllamaHealthResponse,
} from '../types/api.types'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health')
    return response.data
  }

  async ollamaHealthCheck(): Promise<OllamaHealthResponse> {
    const response = await this.client.get<OllamaHealthResponse>('/ollama/health')
    return response.data
  }

  async startConversation(userId: string): Promise<StartConversationResponse> {
    const response = await this.client.post<StartConversationResponse>(
      '/chat/conversations/start',
      { user_id: userId }
    )
    return response.data
  }

  async sendMessage(
    conversationId: string,
    message: string
  ): Promise<MessageResponse> {
    const request: MessageRequest = { user_message: message }
    const response = await this.client.post<MessageResponse>(
      `/chat/conversations/${conversationId}/message`,
      request
    )
    return response.data
  }

  async getConversation(conversationId: string): Promise<ConversationResponse> {
    const response = await this.client.get<ConversationResponse>(
      `/chat/conversations/${conversationId}`
    )
    return response.data
  }

  async endConversation(conversationId: string): Promise<{ message: string }> {
    const response = await this.client.post<{ message: string }>(
      `/chat/conversations/${conversationId}/end`
    )
    return response.data
  }
}

export const apiService = new ApiService()