import { useState, useMemo } from 'react'
import { StockAnalysisForm } from '@/components/analysis/StockAnalysisForm'
import { AnalysisResult } from '@/components/analysis/AnalysisResult'
import type { StockAnalysis } from '@/types'
import { Sparkles } from 'lucide-react'

export const AnalysisPage = () => {
    const [analysis, setAnalysis] = useState<StockAnalysis | null>(null)

    // Data transformation logic - prepare data for presentation component
    const preparedData = useMemo(() => {
        if (!analysis) return null

        const { final_recommendation, analyses } = analysis
        const technical = analyses?.technical?.indicators
        const fundamental = analyses?.fundamental?.fundamental_details
        const sentiment = analyses?.sentiment

        // Helper functions for UI logic
        const getActionColor = (action: string) => {
            switch (action) {
                case 'buy': return 'text-green-600 bg-green-50 border-green-200'
                case 'sell': return 'text-red-600 bg-red-50 border-red-200'
                default: return 'text-yellow-600 bg-yellow-50 border-yellow-200'
            }
        }

        const getActionIcon = (action: string) => {
            switch (action) {
                case 'buy': return 'buy'
                case 'sell': return 'sell'
                default: return 'hold'
            }
        }

        // Prepare chart data for indicators
        const indicatorChartData = technical ? (() => {
            const { ema } = technical
            return [{
                name: 'Current Price',
                value: ema?.current_price || 0,
                ema9: ema?.ema_9 || 0,
                ema21: ema?.ema_21 || 0,
                ema50: ema?.ema_50 || 0,
            }]
        })() : []

        return {
            analysis,
            technical,
            fundamental,
            sentiment,
            final_recommendation,
            getActionColor,
            getActionIcon,
            indicatorChartData
        }
    }, [analysis])

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-6 h-6 text-primary-600" />
                    <h1 className="text-3xl lg:text-4xl font-bold text-gray-900">Stock Analysis</h1>
                </div>
                <p className="text-gray-600 text-lg">
                    Get AI-powered technical and fundamental analysis for any stock
                </p>
            </div>

            <StockAnalysisForm onAnalysisComplete={setAnalysis} />

            {preparedData && (
                <div className="animate-slide-up">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-1 h-8 bg-gradient-to-b from-primary-600 to-primary-700 rounded-full"></div>
                        <h2 className="text-2xl lg:text-3xl font-bold text-gray-900">
                            Analysis: <span className="text-gradient">{analysis.symbol}</span>
                        </h2>
                    </div>
                    <AnalysisResult preparedData={preparedData} />
                </div>
            )}
        </div>
    )
}
