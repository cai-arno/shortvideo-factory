import { Card, Row, Col, Statistic } from "antd"
import { useQuery } from "@tanstack/react-query"
import { analyticsApi } from "../services/api"

const platformColors: Record<string, string> = {
  douyin: "#fe2c55",
  kuaishou: "#ff4906",
  wechat: "#07c160",
  xigua: "#ff6e14",
  bilibili: "#fb7299",
}

export function AnalyticsPage() {
  const { data: overview } = useQuery({
    queryKey: ["analytics", "overview"],
    queryFn: analyticsApi.overview,
    refetchInterval: 30000,
  })

  const { data: trends } = useQuery({
    queryKey: ["analytics", "trends"],
    queryFn: () => analyticsApi.trends(7),
    refetchInterval: 60000,
  })

  const { data: platforms } = useQuery({
    queryKey: ["analytics", "platforms"],
    queryFn: analyticsApi.platforms,
    refetchInterval: 30000,
  })

  const { data: topVideos } = useQuery({
    queryKey: ["analytics", "top"],
    queryFn: () => analyticsApi.topVideos(10),
  })

  const scriptsData = trends?.data?.scripts || []
  const videosData = trends?.data?.videos || []
  const publishesData = trends?.data?.publishes || []

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">数据看板</h1>

      {/* 核心指标 */}
      <Row gutter={[12, 12]}>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="总脚本"
              value={overview?.data?.scripts?.total || 0}
              suffix={<span className="text-xs text-green-500">已完成 {overview?.data?.scripts?.completed || 0}</span>}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="总视频"
              value={overview?.data?.videos?.total || 0}
              suffix={<span className="text-xs text-green-500">已完成 {overview?.data?.videos?.completed || 0}</span>}
            />
          </Card>
        </Col>
        <Col span={8}>
          <Card size="small">
            <Statistic
              title="总发布"
              value={overview?.data?.publishing?.total || 0}
              suffix={<span className="text-xs text-green-500">已发布 {overview?.data?.publishing?.published || 0}</span>}
            />
          </Card>
        </Col>
      </Row>

      {/* 平台分布 */}
      <Card size="small" title="各平台发布量">
        <Row gutter={[8, 8]}>
          {platforms?.data?.platforms?.map((p: any) => (
            <Col span={8} key={p.platform}>
              <Card size="small" className="text-center">
                <div
                  className="text-2xl font-bold"
                  style={{ color: platformColors[p.platform] || "#666" }}
                >
                  {p.published}
                </div>
                <div className="text-xs text-gray-500 capitalize">{p.platform}</div>
                <div className="text-xs text-gray-400">总计 {p.total}</div>
              </Card>
            </Col>
          )) || <div className="p-4 text-gray-400">暂无数据</div>}
        </Row>
      </Card>

      {/* TOP 视频 */}
      <Card size="small" title="热门视频 TOP10">
        <div className="space-y-2">
          {topVideos?.data?.items?.map((v: any, idx: number) => (
            <div key={v.id} className="flex items-center justify-between py-1 border-b border-gray-100 last:border-0">
              <div className="flex items-center gap-2">
                <span className={`w-6 h-6 rounded-full text-xs flex items-center justify-center font-bold ${
                  idx === 0 ? "bg-yellow-400 text-white" : idx === 1 ? "bg-gray-300 text-white" : idx === 2 ? "bg-orange-400 text-white" : "bg-gray-100 text-gray-500"
                }`}>
                  {idx + 1}
                </span>
                <span className="text-sm truncate max-w-[120px]">{v.title}</span>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium">{v.views?.toLocaleString()}</div>
                <div className="text-xs text-gray-400">播放</div>
              </div>
            </div>
          )) || <div className="text-center text-gray-400 py-4">暂无数据</div>}
        </div>
      </Card>
    </div>
  )
}
