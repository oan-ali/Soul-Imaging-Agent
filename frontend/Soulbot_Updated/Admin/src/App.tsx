import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes, Navigate } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { DashboardLayout } from "./components/DashboardLayout";
import DashboardOverview from "./pages/DashboardOverview";
import CallHistory from "./pages/CallHistory";
import AgentConfig from "./pages/AgentConfig";
import KnowledgeBase from "./pages/KnowledgeBase";
import EmbedCodes from "./pages/EmbedCodes";
import Integrations from "./pages/Integrations";
import Analytics from "./pages/Analytics";
import TeamManagement from "./pages/TeamManagement";
import SettingsPage from "./pages/SettingsPage";
import NotFound from "./pages/NotFound";
import Login from "./pages/Login";

const queryClient = new QueryClient();

// Protected Route Component
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const isAuthenticated = localStorage.getItem("soulbot_auth") === "true";
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <>{children}</>;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <BrowserRouter basename={window.location.pathname.startsWith('/admin') ? '/admin' : '/'}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<ProtectedRoute><DashboardLayout /></ProtectedRoute>}>
            <Route path="/" element={<DashboardOverview />} />
            <Route path="/calls" element={<CallHistory />} />
            <Route path="/agent" element={<AgentConfig />} />
            <Route path="/knowledge" element={<KnowledgeBase />} />
            <Route path="/embed" element={<EmbedCodes />} />
            <Route path="/integrations" element={<Integrations />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/team" element={<TeamManagement />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
      <Sonner position="top-center" richColors />
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
