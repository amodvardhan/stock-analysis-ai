import React from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { LoginForm } from '@/components/auth/LoginForm'
import { SignupForm } from '@/components/auth/SignupForm'
import { Layout } from '@/components/layout/Layout'
import { DashboardPage } from '@/pages/DashboardPage'
import { AnalysisPage } from '@/pages/AnalysisPage'
import { Portfolio } from '@/pages/Portfolio'
import { useAuthStore } from '@/stores/authStore'
import WatchlistPage from '@/pages/WatchlistPage'
import RecommendationsPage from '@/pages/RecommendationsPage'
import { BacktestingPage } from '@/pages/BacktestingPage'
import { OrdersPage } from '@/pages/OrdersPage'
import { RiskDashboardPage } from '@/pages/RiskDashboardPage'

// Protected Route wrapper
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated)
    return isAuthenticated ? <>{children}</> : <Navigate to="/login" />
}

function App() {
    return (
        <BrowserRouter>
            <Toaster position="top-right" />
            <Routes>
                {/* Public routes */}
                <Route path="/login" element={<LoginForm />} />
                <Route path="/signup" element={<SignupForm />} />

                {/* Protected routes */}
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <Layout />
                        </ProtectedRoute>
                    }
                >
                    <Route index element={<Navigate to="/dashboard" />} />
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="analysis" element={<AnalysisPage />} />
                    <Route path="recommendations" element={<RecommendationsPage />} />
                    <Route path="portfolio" element={<Portfolio />} />
                    <Route path="watchlist" element={<WatchlistPage />} />
                    <Route path="backtesting" element={<BacktestingPage />} />
                    <Route path="orders" element={<OrdersPage />} />
                    <Route path="risk" element={<RiskDashboardPage />} />

                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
