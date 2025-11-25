import { useState } from 'react'
import { Search, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { analysisAPI } from '@/api/analysis'
import type { StockAnalysis } from '@/types'

interface Props {
    onAnalysisComplete: (analysis: StockAnalysis) => void
}

export const StockAnalysisForm = ({ onAnalysisComplete }: Props) => {
    const [loading, setLoading] = useState(false)
    const [formData, setFormData] = useState({
        symbol: '',
        market: 'india_nse',
        company_name: '',
        user_risk_tolerance: 'moderate',
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)

        try {
            const analysis = await analysisAPI.analyzeStock(formData)
            onAnalysisComplete(analysis)
            toast.success('Analysis completed!')
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Analysis failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <form onSubmit={handleSubmit} className="card">
            <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl flex items-center justify-center">
                    <Search className="w-5 h-5 text-white" />
                </div>
                <h2 className="text-xl lg:text-2xl font-bold text-gray-900">Analyze Stock</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 lg:gap-6">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Stock Symbol
                    </label>
                    <input
                        type="text"
                        value={formData.symbol}
                        onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                        placeholder="e.g., RELIANCE, AAPL"
                        className="input-field"
                        required
                        disabled={loading}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Market
                    </label>
                    <select
                        value={formData.market}
                        onChange={(e) => setFormData({ ...formData, market: e.target.value })}
                        className="input-field"
                        disabled={loading}
                    >
                        <option value="india_nse">India NSE</option>
                        <option value="india_bse">India BSE</option>
                        <option value="us_nyse">US NYSE</option>
                        <option value="us_nasdaq">US NASDAQ</option>
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Company Name (Optional)
                    </label>
                    <input
                        type="text"
                        value={formData.company_name}
                        onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
                        placeholder="e.g., Reliance Industries"
                        className="input-field"
                        disabled={loading}
                    />
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        Risk Tolerance
                    </label>
                    <select
                        value={formData.user_risk_tolerance}
                        onChange={(e) => setFormData({ ...formData, user_risk_tolerance: e.target.value })}
                        className="input-field"
                        disabled={loading}
                    >
                        <option value="conservative">Conservative</option>
                        <option value="moderate">Moderate</option>
                        <option value="aggressive">Aggressive</option>
                    </select>
                </div>
            </div>

            <button
                type="submit"
                disabled={loading}
                className="btn-primary mt-6 w-full md:w-auto flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
            >
                {loading ? (
                    <>
                        <Loader2 className="w-5 h-5 animate-spin" />
                        Analyzing...
                    </>
                ) : (
                    <>
                        <Search className="w-5 h-5" />
                        Analyze Stock
                    </>
                )}
            </button>
        </form>
    )
}
