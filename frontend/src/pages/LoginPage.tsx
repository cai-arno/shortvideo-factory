import { useState, useEffect } from "react"
import { Form, Input, Button, Card, message } from "antd"
import { MobileOutlined, LockOutlined } from "@ant-design/icons"
import { useNavigate } from "react-router-dom"
import { authApi } from "../services/api"

export function LoginPage() {
  const [form] = Form.useForm()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [sending, setSending] = useState(false)
  const [countdown, setCountdown] = useState(0)

  const handleSendCode = async () => {
    try {
      const phone = await form.validateFields(["phone"])
      setSending(true)
      await authApi.sendCode(phone.phone)
      message.success("验证码已发送")
      setCountdown(60)
    } catch {
      // validation error shown inline
    } finally {
      setSending(false)
    }
  }

  const handleLogin = async (values: { phone: string; code: string }) => {
    setLoading(true)
    try {
      const { data } = await authApi.login(values.phone, values.code)
      localStorage.setItem("token", data.access_token)
      localStorage.setItem("user", JSON.stringify(data.user || {}))
      message.success("登录成功")
      navigate("/", { replace: true })
    } catch {
      message.error("验证码错误或已过期")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000)
      return () => clearTimeout(timer)
    }
  }, [countdown])

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <Card className="w-full max-w-sm shadow-lg">
        <div className="text-center mb-6">
          <div className="text-3xl mb-2">🎬</div>
          <h1 className="text-xl font-bold text-gray-800">短视频工厂</h1>
          <p className="text-sm text-gray-500 mt-1">登录后继续使用</p>
        </div>

        <Form
          form={form}
          layout="vertical"
          onFinish={handleLogin}
          size="large"
        >
          <Form.Item
            name="phone"
            rules={[
              { required: true, message: "请输入手机号" },
              { pattern: /^1[3-9]\d{9}$/, message: "手机号格式不正确" },
            ]}
          >
            <Input
              prefix={<MobileOutlined className="text-gray-400" />}
              placeholder="请输入手机号"
              maxLength={11}
            />
          </Form.Item>

          <Form.Item
            name="code"
            rules={[{ required: true, message: "请输入验证码" }]}
          >
            <div className="flex gap-2">
              <Input
                prefix={<LockOutlined className="text-gray-400" />}
                placeholder="请输入验证码"
                maxLength={6}
                className="flex-1"
              />
              <Button
                className="whitespace-nowrap"
                disabled={countdown > 0}
                loading={sending}
                onClick={handleSendCode}
              >
                {countdown > 0 ? `${countdown}s` : "获取验证码"}
              </Button>
            </div>
          </Form.Item>

          <Form.Item className="mb-0">
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={loading}
            >
              登录
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  )
}
