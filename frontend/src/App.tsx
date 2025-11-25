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
// Advanced features - kept for API compatibility but not in main navigation
// These can be accessed directly via URL if needed, but not shown to beginners

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
                    {/* Core Investment Features - Simple & Focused */}
                    <Route index element={<Navigate to="/dashboard" />} />
                    <Route path="dashboard" element={<DashboardPage />} />
                    <Route path="analysis" element={<AnalysisPage />} />
                    <Route path="recommendations" element={<RecommendationsPage />} />
                    <Route path="portfolio" element={<Portfolio />} />
                    <Route path="watchlist" element={<WatchlistPage />} />

                    {/* Advanced features - Hidden from main navigation but accessible via direct URL */}
                    {/* These are kept for API compatibility but not shown to beginners */}

                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
