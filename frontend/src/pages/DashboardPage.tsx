import { useEffect, useState } from 'react'
import { TrendingUp, Briefcase, Eye, Clock, Sparkles, ArrowRight } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { useNavigate } from 'react-router-dom'

export const DashboardPage = () => {
    const user = useAuthStore((state) => state.user)
    const navigate = useNavigate()

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Welcome Section */}
            <div className="mb-8">
                <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-6 h-6 text-primary-600" />
                    <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">
                        Welcome back, <span className="text-gradient">{user?.full_name?.split(' ')[0]}</span>!
                    </h1>
                </div>
                <p className="text-gray-600 text-lg">
                    Here's your stock market intelligence dashboard
                </p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
                <div className="metric-card group bg-gradient-to-br from-blue-500 via-blue-600 to-blue-700 text-white animate-slide-up" style={{ animationDelay: '0ms' }}>
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-blue-100 text-sm font-medium mb-1">Total Analyses</p>
                            <p className="text-3xl lg:text-4xl font-bold">0</p>
                        </div>
                        <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <TrendingUp className="w-6 h-6 lg:w-7 lg:h-7" />
                        </div>
                    </div>
                </div>

                <div className="metric-card group bg-gradient-to-br from-success-500 via-success-600 to-success-700 text-white animate-slide-up" style={{ animationDelay: '100ms' }}>
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-success-100 text-sm font-medium mb-1">Portfolio Value</p>
                            <p className="text-3xl lg:text-4xl font-bold">₹0</p>
                        </div>
                        <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <Briefcase className="w-6 h-6 lg:w-7 lg:h-7" />
                        </div>
                    </div>
                </div>

                <div className="metric-card group bg-gradient-to-br from-purple-500 via-purple-600 to-purple-700 text-white animate-slide-up" style={{ animationDelay: '200ms' }}>
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-purple-100 text-sm font-medium mb-1">Watchlist</p>
                            <p className="text-3xl lg:text-4xl font-bold">0</p>
                        </div>
                        <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <Eye className="w-6 h-6 lg:w-7 lg:h-7" />
                        </div>
                    </div>
                </div>

                <div className="metric-card group bg-gradient-to-br from-orange-500 via-orange-600 to-orange-700 text-white animate-slide-up" style={{ animationDelay: '300ms' }}>
                    <div className="relative z-10 flex items-center justify-between">
                        <div>
                            <p className="text-orange-100 text-sm font-medium mb-1">Last Analysis</p>
                            <p className="text-lg lg:text-xl font-bold">Never</p>
                        </div>
                        <div className="w-12 h-12 lg:w-14 lg:h-14 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                            <Clock className="w-6 h-6 lg:w-7 lg:h-7" />
                        </div>
                    </div>
                </div>
            </div>

            {/* Getting Started */}
            <div className="card animate-slide-up" style={{ animationDelay: '400ms' }}>
                <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-900">Getting Started</h2>
                </div>
                <div className="space-y-4">
                    <div 
                        className="group flex items-start gap-4 p-5 bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl border border-primary-100 hover:shadow-md transition-all duration-200 cursor-pointer"
                        onClick={() => navigate('/analysis')}
                    >
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 text-white rounded-xl flex items-center justify-center flex-shrink-0 font-bold shadow-md group-hover:scale-110 transition-transform">
                            1
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold text-gray-900 mb-1">Analyze Your First Stock</h3>
                                <ArrowRight className="w-5 h-5 text-primary-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                            <p className="text-sm text-gray-600">
                                Use our AI-powered analysis to get comprehensive insights on any stock
                            </p>
                        </div>
                    </div>

                    <div 
                        className="group flex items-start gap-4 p-5 bg-gradient-to-r from-success-50 to-emerald-50 rounded-xl border border-success-100 hover:shadow-md transition-all duration-200 cursor-pointer"
                        onClick={() => navigate('/watchlist')}
                    >
                        <div className="w-10 h-10 bg-gradient-to-br from-success-600 to-success-700 text-white rounded-xl flex items-center justify-center flex-shrink-0 font-bold shadow-md group-hover:scale-110 transition-transform">
                            2
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold text-gray-900 mb-1">Add Stocks to Watchlist</h3>
                                <ArrowRight className="w-5 h-5 text-success-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                            <p className="text-sm text-gray-600">
                                Monitor stocks you're interested in and get real-time price alerts
                            </p>
                        </div>
                    </div>

                    <div 
                        className="group flex items-start gap-4 p-5 bg-gradient-to-r from-purple-50 to-violet-50 rounded-xl border border-purple-100 hover:shadow-md transition-all duration-200 cursor-pointer"
                        onClick={() => navigate('/portfolio')}
                    >
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-purple-700 text-white rounded-xl flex items-center justify-center flex-shrink-0 font-bold shadow-md group-hover:scale-110 transition-transform">
                            3
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center justify-between">
                                <h3 className="font-semibold text-gray-900 mb-1">Track Your Portfolio</h3>
                                <ArrowRight className="w-5 h-5 text-purple-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </div>
                            <p className="text-sm text-gray-600">
                                Add your holdings and track performance with real-time updates
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
