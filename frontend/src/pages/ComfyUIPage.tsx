import { useState, useEffect } from "react"
import { Card, Input, Button, Select, Slider, Space, Tag, message, Spin, Alert, Radio } from "antd"
import { VideoCameraOutlined, PlayCircleOutlined, CheckCircleOutlined, MobileOutlined } from "@ant-design/icons"
import { comfyuiApi_status, comfyuiApi_workflow } from "../services/comfyuiApi"

const { TextArea } = Input

// 平台预设尺寸
const PLATFORM_PRESETS = [
  { key: "douyin", label: "抖音", width: 720, height: 1280, ratio: "9:16", icon: "📱" },
  { key: "xiaohongshu", label: "小红书", width: 1024, height: 1280, ratio: "4:5", icon: "📕" },
  { key: "kuaishou", label: "快手", width: 720, height: 1280, ratio: "9:16", icon: "⚡" },
  { key: "weixin", label: "微信视频号", width: 1080, height: 1920, ratio: "9:16", icon: "💬" },
  { key: "bilibili", label: "B站横屏", width: 1920, height: 1080, ratio: "16:9", icon: "📺" },
]

// 默认工作流模板
const defaultWorkflow = {
  "prompt": {
    "1": {
      "class_type": "LoadWanVideoT5TextEncoder",
      "inputs": {
        "model_name": "models_t5_umt5-xxl-enc-bf16.pth",
        "precision": "bf16"
      }
    },
    "2": {
      "class_type": "WanVideoTextEncode",
      "inputs": {
        "positive_prompt": "",
        "negative_prompt": "blurry, low quality, distorted, watermark, text, logo, bad anatomy, deformed, ugly",
        "force_offload": true,
        "t5": ["1", 0]
      }
    },
    "3": {
      "class_type": "WanVideoModelLoader",
      "inputs": {
        "model": "diffusion_pytorch_model.safetensors",
        "base_precision": "bf16",
        "quantization": "fp8_e4m3fn",
        "load_device": "offload_device"
      }
    },
    "4": {
      "class_type": "WanVideoEmptyEmbeds",
      "inputs": {
        "width": 832,
        "height": 480,
        "num_frames": 49,
        "batch_size": 1
      }
    },
    "5": {
      "class_type": "WanVideoVAELoader",
      "inputs": {
        "model_name": "Wan2.1_VAE.pth",
        "precision": "bf16"
      }
    },
    "6": {
      "class_type": "WanVideoSampler",
      "inputs": {
        "model": ["3", 0],
        "image_embeds": ["4", 0],
        "text_embeds": ["2", 0],
        "steps": 25,
        "cfg": 8.0,
        "shift": 5.0,
        "scheduler": "unipc",
        "seed": 42,
        "force_offload": true,
        "riflex_freq_index": 0
      }
    },
    "7": {
      "class_type": "WanVideoDecode",
      "inputs": {
        "vae": ["5", 0],
        "samples": ["6", 0],
        "enable_vae_tiling": true,
        "tile_x": 128,
        "tile_y": 128,
        "tile_stride_x": 64,
        "tile_stride_y": 64
      }
    },
    "8": {
      "class_type": "VHS_VideoCombine",
      "inputs": {
        "images": ["7", 0],
        "frame_rate": 16,
        "format": "video/h264-mp4",
        "filename_prefix": "video_factory",
        "loop_count": 0,
        "save_output": true,
        "pingpong": false
      }
    }
  }
}

export function ComfyUIPage() {
  const [status, setStatus] = useState<"checking" | "online" | "offline">("checking")
  const [generating, setGenerating] = useState(false)
  const [promptId, setPromptId] = useState<string | null>(null)

  // 表单参数
  const [prompt, setPrompt] = useState("")
  const [negativePrompt] = useState("blurry, low quality, distorted, watermark, text, logo, bad anatomy, deformed, ugly")
  const [width, setWidth] = useState(832)
  const [height, setHeight] = useState(480)
  const [frames, setFrames] = useState(49)
  const [steps, setSteps] = useState(25)
  const [cfg, setCfg] = useState(8)
  const [seed, setSeed] = useState(-1)
  const [platform, setPlatform] = useState<string>("custom")

  // 检查ComfyUI状态
  useEffect(() => {
    checkStatus()
    const interval = setInterval(checkStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  const checkStatus = async () => {
    try {
      const res = await comfyuiApi_status.check()
      if (res.data.status === "online") {
        setStatus("online")
      } else {
        setStatus("offline")
      }
    } catch {
      setStatus("offline")
    }
  }

  // 切换平台预设
  const handlePlatformChange = (platformKey: string) => {
    setPlatform(platformKey)
    const preset = PLATFORM_PRESETS.find(p => p.key === platformKey)
    if (preset) {
      setWidth(preset.width)
      setHeight(preset.height)
    }
  }

  // 生成视频
  const handleGenerate = async () => {
    if (!prompt.trim()) {
      message.error("请输入视频描述")
      return
    }

    if (status !== "online") {
      message.error("ComfyUI未连接")
      return
    }

    setGenerating(true)

    // 构建工作流
    const workflow = JSON.parse(JSON.stringify(defaultWorkflow))
    workflow.prompt["2"].inputs.positive_prompt = prompt
    workflow.prompt["4"].inputs.width = width
    workflow.prompt["4"].inputs.height = height
    workflow.prompt["4"].inputs.num_frames = frames
    workflow.prompt["6"].inputs.steps = steps
    workflow.prompt["6"].inputs.cfg = cfg
    workflow.prompt["6"].inputs.seed = seed >= 0 ? seed : Math.floor(Math.random() * 2147483647)
    workflow.prompt["8"].inputs.filename_prefix = `video_factory_${Date.now()}`

    try {
      const res = await comfyuiApi_workflow.submitPrompt(workflow)
      const newPromptId = res.data.prompt_id
      setPromptId(newPromptId)
      message.success("任务已提交，等待生成...")
    } catch (err: any) {
      message.error("提交失败: " + (err.message || "未知错误"))
      setGenerating(false)
    }
  }

  // 打开视频
  const openVideo = () => {
    window.open("http://localhost:8188", "_blank")
  }

  const currentPreset = PLATFORM_PRESETS.find(p => p.key === platform)

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <div className="mb-4">
        <h2 className="text-lg font-bold flex items-center gap-2">
          <VideoCameraOutlined />
          Wan2.1 AI视频生成
        </h2>
        <p className="text-gray-500 text-sm mt-1">
          基于本地wan2.1模型生成视频，支持多平台尺寸
        </p>
      </div>

      {/* 状态指示 */}
      <Card size="small" className="mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {status === "checking" && <Spin size="small" />}
            {status === "online" && <CheckCircleOutlined className="text-green-500" />}
            {status === "offline" && <span className="text-red-500">●</span>}
            <span>
              {status === "checking" && "检查中..."}
              {status === "online" && "ComfyUI 已连接"}
              {status === "offline" && "ComfyUI 未连接"}
            </span>
          </div>
          {status === "online" && (
            <Button size="small" onClick={openVideo}>
              打开ComfyUI界面
            </Button>
          )}
        </div>
      </Card>

      {/* 平台选择 */}
      <Card title={<><MobileOutlined /> 选择发布平台</>} className="mb-4" size="small">
        <Radio.Group
          value={platform}
          onChange={(e) => handlePlatformChange(e.target.value)}
          className="flex flex-wrap gap-2"
        >
          {PLATFORM_PRESETS.map((preset) => (
            <Radio.Button key={preset.key} value={preset.key} className="h-auto py-2 px-3">
              <div className="text-center">
                <div className="text-lg">{preset.icon}</div>
                <div className="text-xs mt-1">{preset.label}</div>
                <div className="text-xs text-gray-400">{preset.ratio}</div>
              </div>
            </Radio.Button>
          ))}
        </Radio.Group>
        {currentPreset && (
          <div className="mt-2 text-sm text-gray-500">
            尺寸: {currentPreset.width} × {currentPreset.height} | {currentPreset.ratio}
          </div>
        )}
      </Card>

      {/* 参数表单 */}
      <Card title="视频描述" className="mb-4">
        <TextArea
          rows={4}
          placeholder="描述你想要的视频内容...
例如：1 person swimming underwater in the ocean, colorful tropical fish swimming towards the camera"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          disabled={generating}
        />
      </Card>

      <Card title="生成参数" className="mb-4" size="small">
        <Space direction="vertical" className="w-full">
          <div>
            <label>分辨率: {width} × {height}</label>
            <div className="flex gap-2 mt-1">
              <Slider
                style={{ flex: 1 }}
                min={480}
                max={1280}
                step={16}
                value={width}
                onChange={(v) => { setWidth(v); setPlatform("custom"); }}
                disabled={generating}
              />
              <span>×</span>
              <Slider
                style={{ flex: 1 }}
                min={480}
                max={1920}
                step={16}
                value={height}
                onChange={(v) => { setHeight(v); setPlatform("custom"); }}
                disabled={generating}
              />
            </div>
          </div>

          <div>
            <label>帧数: {frames}帧 ({Math.round(frames / 16)}秒)</label>
            <Slider
              min={17}
              max={81}
              step={4}
              value={frames}
              onChange={setFrames}
              disabled={generating}
              marks={{ 17: "1s", 49: "3s", 81: "5s" }}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label>采样步数: {steps}</label>
              <Slider min={10} max={50} value={steps} onChange={setSteps} disabled={generating} />
            </div>
            <div>
              <label>CFG强度: {cfg}</label>
              <Slider min={3} max={15} step={0.5} value={cfg} onChange={setCfg} disabled={generating} />
            </div>
          </div>

          <div>
            <label>随机种子: {seed < 0 ? "随机" : seed}</label>
            <Slider
              min={-1}
              max={2147483647}
              value={seed}
              onChange={setSeed}
              disabled={generating}
              marks={{ "-1": "随机", "0": "0", "2147483647": "最大" }}
            />
          </div>
        </Space>
      </Card>

      {/* 生成按钮 */}
      <Button
        type="primary"
        size="large"
        icon={<PlayCircleOutlined />}
        block
        onClick={handleGenerate}
        loading={generating}
        disabled={status !== "online" || !prompt.trim()}
        className="mb-4"
      >
        {generating ? "生成中..." : "生成视频"}
      </Button>

      {/* 进度提示 */}
      {generating && (
        <Alert
          type="info"
          message="视频生成中，请耐心等待..."
          description={
            <div>
              <p className="text-sm text-gray-500">
                • 采样阶段预计需要2-3分钟
              </p>
              <p className="text-sm text-gray-500">
                • 可点击"打开ComfyUI界面"查看详细进度
              </p>
            </div>
          }
        />
      )}

      {/* 提示 */}
      <div className="mt-4 text-xs text-gray-400">
        <p>支持的平台尺寸：</p>
        <ul className="list-disc list-inside">
          <li>抖音/快手/视频号: 9:16 竖屏 ({">"}720p)</li>
          <li>小红书: 4:5 竖屏 ({">"}1024p)</li>
          <li>B站: 16:9 横屏 (1080p)</li>
        </ul>
      </div>
    </div>
  )
}
