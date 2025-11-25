import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { LogIn } from 'lucide-react'
import toast from 'react-hot-toast'
import { authAPI } from '@/api/auth'
import { useAuthStore } from '@/stores/authStore'

export const LoginForm = () => {
    const navigate = useNavigate()
    const setAuth = useAuthStore((state) => state.setAuth)
    const [loading, setLoading] = useState(false)
    const [credentials, setCredentials] = useState({
        email: '',
        password: '',
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            // Get token
            const authResponse = await authAPI.login(credentials)

            // Store token in localStorage FIRST (so apiClient can use it)
            localStorage.setItem('access_token', authResponse.access_token)

            // Then get user data
            const user = await authAPI.getCurrentUser()

            // Update store
            setAuth(authResponse.access_token, user)

            toast.success(`Welcome back, ${user.full_name}!`)
            navigate('/dashboard')
        } catch (error: any) {
            console.error('Login error:', error)
            toast.error(error.response?.data?.detail || 'Login failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-blue-50 to-slate-50 dark:from-slate-900 dark:via-slate-900 dark:to-slate-800 p-4 relative overflow-hidden transition-colors duration-200">
            {/* Background decoration */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-300 dark:bg-primary-900/30 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow"></div>
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-300 dark:bg-purple-900/30 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-pulse-slow" style={{ animationDelay: '1s' }}></div>
            </div>
            
            <div className="card max-w-md w-full relative z-10 shadow-xl">
                <div className="text-center mb-8">
                    <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-primary-600 to-primary-700 rounded-2xl mb-4 shadow-lg">
                        <LogIn className="w-8 h-8 text-white" />
                    </div>
                    <h1 className="text-3xl lg:text-4xl font-bold text-gradient mb-2">AI Hub</h1>
                    <p className="text-gray-600 dark:text-gray-400 font-medium">Stock Market Intelligence</p>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Email
                        </label>
                        <input
                            type="email"
                            value={credentials.email}
                            onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                            className="input-field"
                            required
                            disabled={loading}
                            autoComplete="email"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Password
                        </label>
                        <input
                            type="password"
                            value={credentials.password}
                            onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                            className="input-field"
                            required
                            disabled={loading}
                            autoComplete="current-password"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full shadow-lg hover:shadow-xl"
                    >
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
                    Don't have an account?{' '}
                    <Link to="/signup" className="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-semibold hover:underline transition-all">
                        Sign up
                    </Link>
                </p>
            </div>
        </div>
    )
}
