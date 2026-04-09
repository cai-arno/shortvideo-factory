import { useNavigate } from "react-router-dom"
import { Card, Row, Col, Statistic, List, Tag, Progress } from "antd"
import {
  VideoCameraOutlined,
  FileTextOutlined,
  AppstoreOutlined,
  SendOutlined,
  ArrowRightOutlined,
} from "@ant-design/icons"
import { useQuery } from "@tanstack/react-query"
import { scriptsApi, videosApi, publishingApi } from "../services/api"

const quickActions = [
  { icon: <FileTextOutlined />, title: "生成脚本", desc: "AI 批量生成爆款文案", path: "/scripts", color: "#6C5CE7" },
  { icon: <VideoCameraOutlined />, title: "视频剪辑", desc: "模板化自动剪辑", path: "/videos", color: "#00B894" },
  { icon: <AppstoreOutlined />, title: "素材中心", desc: "管理视频素材", path: "/materials", color: "#E17055" },
  { icon: <SendOutlined />, title: "发布管理", desc: "多平台定时发布", path: "/publishing", color: "#0984E3" },
]

export function HomePage() {
  const navigate = useNavigate()

  const { data: scriptsData } = useQuery({
    queryKey: ["scripts", "home"],
    queryFn: () => scriptsApi.list({ page_size: 5 }),
  })

  const { data: videosData } = useQuery({
    queryKey: ["videos", "home"],
    queryFn: () => videosApi.list({ page_size: 5 }),
  })

  const { data: publishData } = useQuery({
    queryKey: ["publishing", "home"],
    queryFn: () => publishingApi.list({ page_size: 5 }),
  })

  const scripts = scriptsData?.data?.items || []
  const videos = videosData?.data?.items || []
  const publishes = publishData?.data?.items || []

  return (
    <div className="space-y-6">
      {/* 统计数据 */}
      <Row gutter={16}>
        <Col span={6}>
          <Card size="small" hoverable onClick={() => navigate("/scripts")} className="cursor-pointer">
            <Statistic title="脚本" value={scriptsData?.data?.total || 0} prefix={<FileTextOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small" hoverable onClick={() => navigate("/videos")} className="cursor-pointer">
            <Statistic title="视频" value={videosData?.data?.total || 0} prefix={<VideoCameraOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small" hoverable onClick={() => navigate("/materials")} className="cursor-pointer">
            <Statistic title="素材" value="--" prefix={<AppstoreOutlined />} />
          </Card>
        </Col>
        <Col span={6}>
          <Card size="small" hoverable onClick={() => navigate("/publishing")} className="cursor-pointer">
            <Statistic title="发布" value={publishData?.data?.total || 0} prefix={<SendOutlined />} />
          </Card>
        </Col>
      </Row>

      {/* 快捷入口 */}
      <div>
        <h2 className="text-base font-semibold mb-3">快捷入口</h2>
        <Row gutter={[12, 12]}>
          {quickActions.map((action) => (
            <Col span={12} key={action.path}>
              <Card
                size="small"
                hoverable
                onClick={() => navigate(action.path)}
                className="text-center cursor-pointer"
              >
                <div className="text-2xl mb-2" style={{ color: action.color }}>
                  {action.icon}
                </div>
                <div className="font-medium text-sm">{action.title}</div>
                <div className="text-xs text-gray-400 mt-1">{action.desc}</div>
              </Card>
            </Col>
          ))}
        </Row>
      </div>

      {/* 最近任务 */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-base font-semibold">最近脚本</h2>
          <button onClick={() => navigate("/scripts")} className="text-purple-600 text-sm flex items-center gap-1">
            查看更多 <ArrowRightOutlined />
          </button>
        </div>
        <Card size="small">
          {scripts.length === 0 ? (
            <div className="text-center text-gray-400 py-4">暂无脚本</div>
          ) : (
            <List
              size="small"
              dataSource={scripts.slice(0, 3)}
              renderItem={(item: any) => (
                <List.Item className="px-0">
                  <div className="flex justify-between items-center w-full">
                    <span className="text-sm truncate max-w-[60%]">{item.title}</span>
                    <Tag
                      color={item.status === "completed" ? "success" : item.status === "generating" ? "processing" : "default"}
                      className="text-xs"
                    >
                      {item.status === "completed" ? "已完成" : item.status === "generating" ? "生成中" : "草稿"}
                    </Tag>
                  </div>
                </List.Item>
              )}
            />
          )}
        </Card>
      </div>

      {/* 最近视频 */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <h2 className="text-base font-semibold">最近视频</h2>
          <button onClick={() => navigate("/videos")} className="text-purple-600 text-sm flex items-center gap-1">
            查看更多 <ArrowRightOutlined />
          </button>
        </div>
        <Card size="small">
          {videos.length === 0 ? (
            <div className="text-center text-gray-400 py-4">暂无视频</div>
          ) : (
            <List
              size="small"
              dataSource={videos.slice(0, 3)}
              renderItem={(item: any) => (
                <List.Item className="px-0">
                  <div className="flex justify-between items-center w-full">
                    <span className="text-sm truncate max-w-[60%]">{item.title}</span>
                    <Progress percent={item.progress || 0} size="small" className="w-24" />
                  </div>
                </List.Item>
              )}
            />
          )}
        </Card>
      </div>
    </div>
  )
}
