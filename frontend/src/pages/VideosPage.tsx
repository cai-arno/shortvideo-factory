import { Card, List, Tag, Button, Progress, Empty, message, Modal } from "antd"
import { PlayCircleOutlined } from "@ant-design/icons"
import { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { videosApi } from "../services/api"

const statusMap: Record<string, { color: string; text: string }> = {
  pending: { color: "default", text: "待处理" },
  rendering: { color: "processing", text: "渲染中" },
  completed: { color: "success", text: "已完成" },
  failed: { color: "error", text: "失败" },
}

export function VideosPage() {
  const queryClient = useQueryClient()
  const [page] = [1]
  const [previewVideo, setPreviewVideo] = useState<any>(null)

  const { data, isLoading } = useQuery({
    queryKey: ["videos", page],
    queryFn: () => videosApi.list({ page, page_size: 20 }),
  })

  const renderMutation = useMutation({
    mutationFn: videosApi.render,
    onSuccess: () => {
      message.destroy()
      message.success("渲染任务已提交")
      queryClient.invalidateQueries({ queryKey: ["videos"] })
    },
    onError: () => {
      message.destroy()
      message.error("渲染失败")
    },
  })

  const videos = data?.data?.items || []

  return (
    <div className="space-y-4">
      <h1 className="text-lg font-semibold">视频剪辑</h1>

      {isLoading ? (
        <Card>加载中...</Card>
      ) : videos.length === 0 ? (
        <Empty description="暂无视频，请先生成脚本再创建视频" />
      ) : (
        <List
          dataSource={videos}
          renderItem={(video: any) => (
            <List.Item>
              <List.Item.Meta
                avatar={
                  <div className="w-20 h-28 bg-gray-100 rounded flex items-center justify-center">
                    {video.thumbnail_path ? (
                      <img src={video.thumbnail_path} className="w-full h-full object-cover rounded" />
                    ) : (
                      <PlayCircleOutlined className="text-2xl text-gray-400" />
                    )}
                  </div>
                }
                title={
                  <div className="flex justify-between items-center">
                    <span className="text-sm">{video.title}</span>
                    <Tag color={statusMap[video.status]?.color}>{statusMap[video.status]?.text}</Tag>
                  </div>
                }
                description={
                  <div className="space-y-2">
                    {video.status === "rendering" && (
                      <Progress percent={video.progress || 0} size="small" />
                    )}
                    <div className="text-xs text-gray-500">
                      时长: {video.duration}s | 尺寸: {video.width}x{video.height}
                    </div>
                    {video.status === "completed" && (
                      <Button size="small" type="primary" onClick={() => setPreviewVideo(video)}>
                        预览
                      </Button>
                    )}
                    {video.status === "pending" && (
                      <Button
                        size="small"
                        type="primary"
                        onClick={() => renderMutation.mutate(video.id)}
                        loading={renderMutation.isPending}
                        disabled={renderMutation.isPending}
                      >
                        开始渲染
                      </Button>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      )}

      <Modal
        open={!!previewVideo}
        title="视频预览"
        onCancel={() => setPreviewVideo(null)}
        footer={null}
        width={800}
      >
        {previewVideo?.video_path && (
          <video
            src={previewVideo.video_path}
            controls
            autoPlay
            className="w-full"
            style={{ maxHeight: "60vh" }}
          />
        )}
        {!previewVideo?.video_path && <p>视频文件不存在</p>}
      </Modal>
    </div>
  )
}
