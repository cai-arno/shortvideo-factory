import { useState } from "react"
import { Card, List, Tag, Button, Modal, Form, Input, Select, message, Spin } from "antd"
import { PlusOutlined, DeleteOutlined } from "@ant-design/icons"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { scriptsApi } from "../services/api"

const { TextArea } = Input

const scriptTypeOptions = [
  { value: "product_showcase", label: "产品展示" },
  { value: "tutorial", label: "教程讲解" },
  { value: "story", label: "故事叙述" },
  { value: "review", label: "测评种草" },
  { value: "lifestyle", label: "生活场景" },
]

const statusMap: Record<string, { color: string; text: string }> = {
  draft: { color: "default", text: "草稿" },
  generating: { color: "processing", text: "生成中" },
  completed: { color: "success", text: "已完成" },
  failed: { color: "error", text: "失败" },
}

export function ScriptsPage() {
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()
  const queryClient = useQueryClient()
  const [page] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ["scripts", page],
    queryFn: () => scriptsApi.list({ page, page_size: 20 }),
  })

  const generateMutation = useMutation({
    mutationFn: scriptsApi.generate,
    onSuccess: () => {
      message.destroy()
      message.success("脚本生成中...")
      setModalOpen(false)
      form.resetFields()
      queryClient.invalidateQueries({ queryKey: ["scripts"] })
    },
    onError: () => {
      message.destroy()
      message.error("生成失败")
    },
  })

  const deleteMutation = useMutation({
    mutationFn: scriptsApi.delete,
    onSuccess: () => {
      message.destroy()
      message.success("已删除")
      queryClient.invalidateQueries({ queryKey: ["scripts"] })
    },
  })

  const scripts = data?.data?.items || []

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-lg font-semibold">脚本管理</h1>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)} disabled={generateMutation.isPending}>
          生成脚本
        </Button>
      </div>

      {isLoading ? (
        <div className="text-center py-10">
          <Spin />
        </div>
      ) : scripts.length === 0 ? (
        <Card>
          <div className="text-center text-gray-400 py-10">
            暂无脚本，点击上方按钮生成
          </div>
        </Card>
      ) : (
        <List
          dataSource={scripts}
          renderItem={(script: any) => (
            <List.Item
              actions={[
                <Button
                  key="delete"
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => deleteMutation.mutate(script.id)}
                />,
              ]}
            >
              <List.Item.Meta
                title={
                  <div className="flex justify-between items-center">
                    <span className="text-sm">{script.title}</span>
                    <Tag color={statusMap[script.status]?.color}>{statusMap[script.status]?.text}</Tag>
                  </div>
                }
                description={
                  <div className="text-xs text-gray-500">
                    <div>类型: {script.script_type}</div>
                    {script.hook && <div className="truncate mt-1">开场: {script.hook}</div>}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      )}

      {/* 生成脚本弹窗 */}
      <Modal
        title="生成脚本"
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={(values) => generateMutation.mutate(values)}
        >
          <Form.Item
            name="topic"
            label="主题"
            rules={[{ required: true, message: "请输入主题" }]}
          >
            <TextArea rows={3} placeholder="例如: 夏季护肤小技巧" />
          </Form.Item>

          <Form.Item name="script_type" label="视频类型" initialValue="product_showcase">
            <Select options={scriptTypeOptions} />
          </Form.Item>

          <Form.Item name="style" label="风格要求（可选）">
            <Input placeholder="例如: 轻松幽默、专业严谨" />
          </Form.Item>

          <Form.Item name="quantity" label="生成数量" initialValue={1}>
            <Select options={[{ value: 1, label: "1 条" }, { value: 3, label: "3 条" }, { value: 5, label: "5 条" }]} />
          </Form.Item>

          <Button type="primary" htmlType="submit" block loading={generateMutation.isPending} disabled={generateMutation.isPending}>
            开始生成
          </Button>
        </Form>
      </Modal>
    </div>
  )
}
