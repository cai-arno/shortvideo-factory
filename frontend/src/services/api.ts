import axios from "axios"

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1"

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
})

// 拦截器：添加 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token")
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 拦截器：统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message || "请求失败"
    console.error("API Error:", message)
    return Promise.reject(error)
  }
)

// ============ Scripts ============
export const scriptsApi = {
  list: (params: { page?: number; page_size?: number; status?: string }) =>
    api.get("/scripts", { params }),

  generate: (data: { topic: string; script_type: string; quantity?: number; style?: string }) =>
    api.post("/scripts/generate", data),

  get: (id: number) => api.get(`/scripts/${id}`),

  delete: (id: number) => api.delete(`/scripts/${id}`),
}

// ============ Videos ============
export const videosApi = {
  list: (params: { page?: number; page_size?: number; status?: string }) =>
    api.get("/videos", { params }),

  create: (data: { script_id: number; template_id?: number; material_ids?: number[] }) =>
    api.post("/videos", data),

  render: (videoId: number) => api.post("/videos/render", { video_id: videoId }),

  get: (id: number) => api.get(`/videos/${id}`),
}

// ============ Materials ============
export const materialsApi = {
  list: (params: {
    page?: number
    page_size?: number
    material_type?: string
    category?: string
    keyword?: string
  }) => api.get("/materials", { params }),

  upload: (formData: FormData) =>
    api.post("/materials/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),

  get: (id: number) => api.get(`/materials/${id}`),

  delete: (id: number) => api.delete(`/materials/${id}`),
}

// ============ Templates ============
export const templatesApi = {
  list: (params?: { template_type?: string; script_type?: string }) =>
    api.get("/templates", { params }),

  get: (id: number) => api.get(`/templates/${id}`),
}

// ============ Publishing ============
export const publishingApi = {
  list: (params?: { page?: number; page_size?: number; platform?: string; status?: string }) =>
    api.get("/publishing", { params }),

  create: (data: { video_id: number; platform: string; scheduled_at?: string }) =>
    api.post("/publishing", data),

  get: (id: number) => api.get(`/publishing/${id}`),
}

// ============ Analytics ============
export const analyticsApi = {
  overview: () => api.get("/analytics/overview"),

  trends: (days = 7) => api.get("/analytics/trends", { params: { days } }),

  platforms: () => api.get("/analytics/platforms"),

  topVideos: (limit = 10) => api.get("/analytics/top", { params: { limit } }),
}

// ============ Auth ============
export const authApi = {
  sendCode: (phone: string) => api.post("/auth/phone/send-code", { phone }),

  login: (phone: string, code: string) =>
    api.post("/auth/phone/login", { phone, code }),
}

export default api
