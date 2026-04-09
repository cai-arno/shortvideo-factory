import { Card, List, Tag, Button, Empty, message } from "antd"
import { SendOutlined, CheckCircleOutlined, ClockCircleOutlined } from "@ant-design/icons"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { publishingApi } from "../services/api"

const platformMap: Record<string, { name: string; color: string }> = {
  douyin: { name: "抖音", color: "#000" },
  kuaishou: { name: "快手", color: "#FF4906" },
  wechat: { name: "视频号", color: "#07C160" },
  xigua: { name: "西瓜视频", color: "#FF4D4D" },
  bilibili: { name: "B站", color: "#FB7299" },
}

const statusMap: Record<string, { color: string; text: string }> = {
  draft: { color: "default", text: "草稿" },
  pending: { color: "warning", text: "待发布" },
  publishing: { color: "processing", text: "发布中" },
  published: { color: "success", text: "已发布" },
  failed: { color: "error", text: "失败" },
}

export function PublishingPage() {
  const queryClient = useQueryClient()
  const [page] = [1]

  const { data, isLoading } = useQuery({
    queryKey: ["publishing", page],
    queryFn: () => publishingApi.list({ page, page_size: 20 }),
  })

  const deleteMutation = useMutation({
    mutationFn: publishingApi.delete,
    onSuccess: () => {
      message.destroy()
      message.success("发布记录已删除")
      queryClient.invalidateQueries({ queryKey: ["publishing"] })
    },
    onError: () => {
      message.destroy()
      message.error("删除失败")
    },
  })

  const records = data?.data?.items || []

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">发布管理</h1>

      {isLoading ? (
        <Card>加载中...</Card>
      ) : records.length === 0 ? (
        <Empty description="暂无发布记录" />
      ) : (
        <List
          dataSource={records}
          renderItem={(record: any) => (
            <List.Item
              actions={[
                <Button
                  key="delete"
                  size="small"
                  danger
                  onClick={() => deleteMutation.mutate(record.id)}
                  loading={deleteMutation.isPending}
                >
                  删除
                </Button>,
              ]}
            >
              <List.Item.Meta
                avatar={
                  <div className="w-10 h-10 bg-gray-100 rounded flex items-center justify-center text-lg">
                    {record.platform === "douyin" && "🎵"}
                    {record.platform === "kuaishou" && "📱"}
                    {record.platform === "wechat" && "💬"}
                    {record.platform === "xigua" && "🍉"}
                    {record.platform === "bilibili" && "📺"}
                  </div>
                }
                title={
                  <div className="flex justify-between items-center">
                    <span className="text-sm">
                      <span
                        className="inline-block w-2 h-2 rounded-full mr-1"
                        style={{ backgroundColor: platformMap[record.platform]?.color }}
                      />
                      {platformMap[record.platform]?.name || record.platform}
                    </span>
                    <Tag color={statusMap[record.status]?.color}>{statusMap[record.status]?.text}</Tag>
                  </div>
                }
                description={
                  <div className="text-xs text-gray-500 mt-1">
                    {record.scheduled_at && (
                      <span className="flex items-center gap-1">
                        <ClockCircleOutlined /> 定时: {record.scheduled_at}
                      </span>
                    )}
                    {record.published_at && (
                      <span className="flex items-center gap-1">
                        <CheckCircleOutlined /> 已发布: {record.published_at}
                      </span>
                    )}
                    {record.platform_url && (
                      <a href={record.platform_url} target="_blank" rel="noopener noreferrer" className="block mt-1">
                        查看链接 →
                      </a>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      )}
    </div>
  )
}
