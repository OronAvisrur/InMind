export interface MessageRequest {
  user_message: string
}

export interface MessageResponse {
  conversation_id: string
  response: string
  intent: string
  entities: Record<string, string>
  state: string
}

export interface ConversationResponse {
  conversation_id: string
  user_id: string
  state: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface StartConversationResponse {
  conversation_id: string
  message: string
}

export interface HealthResponse {
  status: string
  timestamp: string
}

export interface OllamaHealthResponse {
  status: string
  models: string[]
}

export interface Product {
  id: string
  name: string
  description: string
  price: number
  category: string
  features: string[]
}

export interface ProductIngestRequest {
  products: Product[]
}

export interface ProductSearchRequest {
  query: string
  limit?: number
  category?: string
  min_price?: number
  max_price?: number
}

export interface ProductSearchResponse {
  products: Product[]
  total: number
}