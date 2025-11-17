import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { LoginForm } from '@/components/auth/LoginForm'
import { SignupForm } from '@/components/auth/SignupForm'
import { Layout } from '@/components/layout/Layout'
import { DashboardPage } from '@/pages/DashboardPage'
import { AnalysisPage } from '@/pages/AnalysisPage'
import { useAuthStore } from '@/stores/authStore'

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
                    <Route
                        path="portfolio"
                        element={
                            <div className="card">
                                <h1 className="text-2xl font-bold">Portfolio</h1>
                                <p className="text-gray-600 mt-2">Coming soon...</p>
                            </div>
                        }
                    />
                    <Route
                        path="watchlist"
                        element={
                            <div className="card">
                                <h1 className="text-2xl font-bold">Watchlist</h1>
                                <p className="text-gray-600 mt-2">Coming soon...</p>
                            </div>
                        }
                    />
                </Route>
            </Routes>
        </BrowserRouter>
    )
}

export default App
