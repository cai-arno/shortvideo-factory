import axios from "axios"

const COMFYUI_API = import.meta.env.VITE_COMFYUI_URL || "http://localhost:8189"

const comfyuiApi = axios.create({
  baseURL: COMFYUI_API,
  timeout: 300000, // 5分钟超时，视频生成需要更长
})

// ============ ComfyUI 状态 ============
export const comfyuiApi_status = {
  check: () => comfyuiApi.get("/status"),
}

// ============ 视频生成 ============
export interface GenerateRequest {
  prompt: string
  negative_prompt?: string
  width?: number
  height?: number
  frames?: number
  steps?: number
  cfg?: number
  seed?: number
}

export const comfyuiApi_generate = {
  // 提交文生视频任务
  submit: (data: GenerateRequest) =>
    comfyuiApi.post("/generate/wan21", data, {
      baseURL: "http://localhost:8189",
    }),

  // 查询任务历史
  history: (promptId: string) => comfyuiApi.get(`/history/${promptId}`),

  // 获取输出文件
  getHistory: () => comfyuiApi.get("/history"),
}

// ============ 工作流 ============
export const comfyuiApi_workflow = {
  // 直接提交工作流
  submitPrompt: (prompt: any) =>
    comfyuiApi.post("/prompt", prompt, {
      baseURL: "http://localhost:8188",
    }),

  // 查询对象信息
  getObjectInfo: () =>
    comfyuiApi.get("/api/object_info", {
      baseURL: "http://localhost:8188",
    }),
}

export default comfyuiApi
