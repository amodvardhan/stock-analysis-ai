import { useEffect, useState } from 'react'
import { marketService } from '../api/marketService'
import { toast } from 'react-hot-toast'
import { Calendar, TrendingUp, Building2 } from 'lucide-react'

export const EarningsCalendarPage = () => {
    const [earnings, setEarnings] = useState<any>(null)
    const [ipos, setIpos] = useState<any>(null)
    const [loading, setLoading] = useState(true)
    const [market, setMarket] = useState('india_nse')
    const [activeTab, setActiveTab] = useState<'earnings' | 'ipos'>('earnings')

    useEffect(() => {
        loadData()
    }, [market, activeTab])

    const loadData = async () => {
        try {
            setLoading(true)
            if (activeTab === 'earnings') {
                const data = await marketService.getEarningsCalendar(market, 30)
                setEarnings(data)
            } else {
                const data = await marketService.getIPOCalendar(market, 90)
                setIpos(data)
            }
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to load calendar')
        } finally {
            setLoading(false)
        }
    }

    if (loading && !earnings && !ipos) {
        return (
            <div className="flex justify-center items-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        )
    }

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <Calendar className="w-6 h-6 text-primary-600 dark:text-primary-400" />
                        <h1 className="text-3xl lg:text-4xl font-bold text-gray-900 dark:text-gray-100">
                            Earnings & IPO Calendar
                        </h1>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                        Track upcoming earnings and IPO announcements
                    </p>
                </div>
                <select
                    value={market}
                    onChange={(e) => setMarket(e.target.value)}
                    className="input-field"
                >
                    <option value="india_nse">India NSE</option>
                    <option value="india_bse">India BSE</option>
                    <option value="us_nyse">US NYSE</option>
                    <option value="us_nasdaq">US NASDAQ</option>
                </select>
            </div>

            {/* Tabs */}
            <div className="flex gap-3">
                <button
                    onClick={() => setActiveTab('earnings')}
                    className={`px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2 ${
                        activeTab === 'earnings'
                            ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                            : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                    }`}
                >
                    <TrendingUp className="w-4 h-4" />
                    Earnings Calendar
                </button>
                <button
                    onClick={() => setActiveTab('ipos')}
                    className={`px-6 py-3 rounded-xl font-semibold transition-all flex items-center gap-2 ${
                        activeTab === 'ipos'
                            ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
                            : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-700'
                    }`}
                >
                    <Building2 className="w-4 h-4" />
                    IPO Calendar
                </button>
            </div>

            {/* Earnings Calendar */}
            {activeTab === 'earnings' && earnings && (
                <div className="card">
                    <h2 className="text-2xl font-bold mb-6">Upcoming Earnings</h2>
                    {earnings.earnings_events && earnings.earnings_events.length > 0 ? (
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead className="bg-gray-50 dark:bg-slate-800">
                                    <tr>
                                        <th className="px-4 py-3 text-left">Symbol</th>
                                        <th className="px-4 py-3 text-left">Company</th>
                                        <th className="px-4 py-3 text-left">Earnings Date</th>
                                        <th className="px-4 py-3 text-right">Est. EPS</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-slate-700">
                                    {earnings.earnings_events.map((event: any, idx: number) => (
                                        <tr key={idx} className="hover:bg-gray-50 dark:hover:bg-slate-800">
                                            <td className="px-4 py-3 font-semibold text-gray-900 dark:text-gray-100">
                                                {event.symbol}
                                            </td>
                                            <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                                                {event.company_name}
                                            </td>
                                            <td className="px-4 py-3 text-gray-700 dark:text-gray-300">
                                                {event.earnings_date}
                                            </td>
                                            <td className="px-4 py-3 text-right text-gray-700 dark:text-gray-300">
                                                {event.estimated_eps ? event.estimated_eps.toFixed(2) : 'N/A'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    ) : (
                        <div className="text-center py-16">
                            <Calendar className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400 font-medium">
                                No upcoming earnings found
                            </p>
                        </div>
                    )}
                </div>
            )}

            {/* IPO Calendar */}
            {activeTab === 'ipos' && ipos && (
                <div className="card">
                    <h2 className="text-2xl font-bold mb-6">IPO Calendar</h2>
                    {ipos.note ? (
                        <div className="text-center py-16">
                            <Building2 className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400 font-medium mb-2">
                                {ipos.note}
                            </p>
                            <p className="text-sm text-gray-400 dark:text-gray-500">
                                IPO data requires specialized data source integration
                            </p>
                        </div>
                    ) : (
                        <div className="text-center py-16">
                            <Building2 className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                            <p className="text-gray-500 dark:text-gray-400 font-medium">
                                No upcoming IPOs found
                            </p>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}

