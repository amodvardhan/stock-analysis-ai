import { NavLink, useLocation } from 'react-router-dom'
import { LayoutDashboard, TrendingUp, Briefcase, Eye, Sparkles } from 'lucide-react'

const navItems = [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { to: '/analysis', icon: TrendingUp, label: 'Stock Analysis' },
    { to: '/recommendations', icon: Sparkles, label: 'AI Recommendations' },
    { to: '/portfolio', icon: Briefcase, label: 'Portfolio' },
    { to: '/watchlist', icon: Eye, label: 'Watchlist' },
]

export const Sidebar = () => {
    const location = useLocation()
    
    return (
        <aside className="w-64 lg:w-72 bg-white/80 backdrop-blur-lg border-r border-gray-200/50 min-h-[calc(100vh-4rem)] lg:min-h-[calc(100vh-5rem)] sticky top-16 lg:top-20">
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
                                    : 'text-gray-700 hover:bg-gradient-to-r hover:from-primary-50 hover:to-blue-50 hover:text-primary-700 font-medium'
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
