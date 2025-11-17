import { useEffect, useState } from 'react'
import { TrendingUp, Briefcase, Eye, Clock } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'

export const DashboardPage = () => {
    const user = useAuthStore((state) => state.user)

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">
                    Welcome back, {user?.full_name}!
                </h1>
                <p className="text-gray-600 mt-1">
                    Here's your stock market intelligence dashboard
                </p>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="card bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-blue-600 font-medium">Total Analyses</p>
                            <p className="text-3xl font-bold text-blue-700 mt-1">0</p>
                        </div>
                        <TrendingUp className="w-10 h-10 text-blue-600 opacity-50" />
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-green-50 to-green-100 border border-green-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-green-600 font-medium">Portfolio Value</p>
                            <p className="text-3xl font-bold text-green-700 mt-1">₹0</p>
                        </div>
                        <Briefcase className="w-10 h-10 text-green-600 opacity-50" />
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-purple-600 font-medium">Watchlist</p>
                            <p className="text-3xl font-bold text-purple-700 mt-1">0</p>
                        </div>
                        <Eye className="w-10 h-10 text-purple-600 opacity-50" />
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-orange-50 to-orange-100 border border-orange-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm text-orange-600 font-medium">Last Analysis</p>
                            <p className="text-sm font-bold text-orange-700 mt-1">Never</p>
                        </div>
                        <Clock className="w-10 h-10 text-orange-600 opacity-50" />
                    </div>
                </div>
            </div>

            {/* Getting Started */}
            <div className="card">
                <h2 className="text-xl font-bold mb-4">Getting Started</h2>
                <div className="space-y-3">
                    <div className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
                        <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center flex-shrink-0 font-bold">
                            1
                        </div>
                        <div>
                            <h3 className="font-semibold">Analyze Your First Stock</h3>
                            <p className="text-sm text-gray-600">
                                Use our AI-powered analysis to get insights on any stock
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
                        <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center flex-shrink-0 font-bold">
                            2
                        </div>
                        <div>
                            <h3 className="font-semibold">Add Stocks to Watchlist</h3>
                            <p className="text-sm text-gray-600">
                                Monitor stocks you're interested in and get price alerts
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start gap-3 p-4 bg-gray-50 rounded-lg">
                        <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center flex-shrink-0 font-bold">
                            3
                        </div>
                        <div>
                            <h3 className="font-semibold">Track Your Portfolio</h3>
                            <p className="text-sm text-gray-600">
                                Add your holdings and track performance in real-time
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
