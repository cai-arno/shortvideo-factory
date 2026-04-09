import { Outlet, useNavigate, useLocation } from "react-router-dom"
import { Layout as AntLayout, Menu, Button } from "antd"
import {
  HomeOutlined,
  FileTextOutlined,
  VideoCameraOutlined,
  AppstoreOutlined,
  SendOutlined,
  DashboardOutlined,
} from "@ant-design/icons"
import clsx from "clsx"

const { Header, Content } = AntLayout

const menuItems = [
  { key: "/", icon: <HomeOutlined />, label: "首页" },
  { key: "/scripts", icon: <FileTextOutlined />, label: "脚本" },
  { key: "/videos", icon: <VideoCameraOutlined />, label: "视频" },
  { key: "/ai-video", icon: <VideoCameraOutlined />, label: "AI视频" },
  { key: "/analytics", icon: <DashboardOutlined />, label: "看板" },
  { key: "/materials", icon: <AppstoreOutlined />, label: "素材" },
  { key: "/publishing", icon: <SendOutlined />, label: "发布" },
]

export function Layout() {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <AntLayout className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <Header className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-4 bg-white shadow-sm">
        <div className="text-lg font-bold text-purple-600">🎬 短视频工厂</div>
        <Button type="primary" size="small" onClick={() => navigate("/scripts")}>
          生成脚本
        </Button>
      </Header>

      {/* 底部导航（移动端） */}
      <Content className="pt-16 pb-20 px-4">
        <Outlet />
      </Content>

      <nav className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 safe-area-inset-bottom">
        <div className="flex justify-around items-center h-14">
          {menuItems.map((item) => (
            <button
              key={item.key}
              onClick={() => navigate(item.key)}
              className={clsx(
                "flex flex-col items-center justify-center w-full h-full gap-0.5 transition-colors",
                location.pathname === item.key
                  ? "text-purple-600"
                  : "text-gray-400 hover:text-gray-600"
              )}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="text-xs">{item.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </AntLayout>
  )
}
