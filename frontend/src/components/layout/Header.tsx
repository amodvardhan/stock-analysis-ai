import { LogOut, User, TrendingUp, Moon, Sun } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useTheme } from '@/contexts/ThemeContext'

export const Header = () => {
    const navigate = useNavigate()
    const { user, logout } = useAuthStore()
    const { theme, toggleTheme } = useTheme()

    const handleLogout = () => {
        logout()
        navigate('/login')
    }

    return (
        <header className="sticky top-0 z-50 backdrop-blur-lg shadow-sm border-b transition-colors duration-200 bg-white/80 dark:bg-slate-900/80 border-gray-200/50 dark:border-slate-700/50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between items-center h-16 lg:h-20">
                    <div className="flex items-center gap-3">
                        <div className="flex items-center justify-center w-10 h-10 lg:w-12 lg:h-12 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl shadow-md">
                            <TrendingUp className="w-6 h-6 lg:w-7 lg:h-7 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl lg:text-2xl font-bold text-gradient">AI Hub</h1>
                            <span className="text-xs lg:text-sm text-gray-500 dark:text-gray-400 font-medium">Stock Intelligence</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-3 lg:gap-4">
                        <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 rounded-xl border border-primary-100 dark:border-primary-800">
                            <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
                                <User className="w-4 h-4 text-white" />
                            </div>
                            <span className="text-sm font-medium text-gray-700 dark:text-gray-200">{user?.full_name}</span>
                        </div>
                        <button
                            onClick={toggleTheme}
                            className="flex items-center justify-center w-10 h-10 rounded-xl bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
                            aria-label="Toggle theme"
                        >
                            {theme === 'dark' ? (
                                <Sun className="w-5 h-5 text-yellow-500" />
                            ) : (
                                <Moon className="w-5 h-5 text-gray-700" />
                            )}
                        </button>
                        <button
                            onClick={handleLogout}
                            className="flex items-center gap-2 px-3 lg:px-4 py-2 text-sm font-medium text-danger-600 dark:text-danger-400 hover:bg-danger-50 dark:hover:bg-danger-900/20 rounded-xl transition-all duration-200 hover:shadow-sm active:scale-95"
                        >
                            <LogOut className="w-4 h-4" />
                            <span className="hidden sm:inline">Logout</span>
                        </button>
                    </div>
                </div>
            </div>
        </header>
    )
}
