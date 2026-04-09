import { Routes, Route, Navigate } from "react-router-dom"
import { Layout } from "./components/Layout"
import { HomePage } from "./pages/HomePage"
import { ScriptsPage } from "./pages/ScriptsPage"
import { VideosPage } from "./pages/VideosPage"
import { MaterialsPage } from "./pages/MaterialsPage"
import { PublishingPage } from "./pages/PublishingPage"
import { AnalyticsPage } from "./pages/AnalyticsPage"
import { ComfyUIPage } from "./pages/ComfyUIPage"
import { LoginPage } from "./pages/LoginPage"

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="scripts" element={<ScriptsPage />} />
        <Route path="videos" element={<VideosPage />} />
        <Route path="materials" element={<MaterialsPage />} />
        <Route path="publishing" element={<PublishingPage />} />
        <Route path="analytics" element={<AnalyticsPage />} />
        <Route path="ai-video" element={<ComfyUIPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
