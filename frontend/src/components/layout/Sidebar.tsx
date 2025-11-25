import { NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, TrendingUp, Briefcase, Eye, Sparkles, BarChart3, ShoppingCart, Shield } from 'lucide-react'

const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/analysis', icon: TrendingUp, label: 'Stock Analysis' },
    { to: '/recommendations', icon: Sparkles, label: 'AI Recommendations' },
    { to: '/portfolio', icon: Briefcase, label: 'Portfolio' },
    { to: '/watchlist', icon: Eye, label: 'Watchlist' },
    { to: '/backtesting', icon: BarChart3, label: 'Backtesting' },
    { to: '/orders', icon: ShoppingCart, label: 'Orders' },
    { to: '/risk', icon: Shield, label: 'Risk Dashboard' },
]

export const Sidebar = () => {
    const location = useLocation()
    
    return (
        <aside className="w-64 lg:w-72 backdrop-blur-lg border-r min-h-[calc(100vh-4rem)] lg:min-h-[calc(100vh-5rem)] sticky top-16 lg:top-20 bg-white/80 dark:bg-slate-900/80 border-gray-200/50 dark:border-slate-700/50">
            <nav className="p-4 lg:p-6 space-y-2">
                {navItems.map((item) => {
                    const Icon = item.icon
                    const isActive = location.pathname === item.to
                    return (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            className={`group flex items-center gap-3 px-4 py-3.5 rounded-xl transition-all duration-200 ${
                                isActive
                                    ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-md shadow-primary-500/30 font-semibold'
                                    : 'text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-primary-50 hover:to-blue-50 dark:hover:from-primary-900/30 dark:hover:to-blue-900/30 hover:text-primary-700 dark:hover:text-primary-300 font-medium'
                            }`}
                        >
                            <Icon className={`w-5 h-5 transition-transform duration-200 ${isActive ? 'scale-110' : 'group-hover:scale-110'}`} />
                            <span className="text-sm lg:text-base">{item.label}</span>
                        </NavLink>
                    )
                })}
            </nav>
        </aside>
    )
}
