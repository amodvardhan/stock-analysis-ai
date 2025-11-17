import { useState } from 'react'
import { StockAnalysisForm } from '@/components/analysis/StockAnalysisForm'
import { AnalysisResult } from '@/components/analysis/AnalysisResult'
import type { StockAnalysis } from '@/types'

export const AnalysisPage = () => {
    const [analysis, setAnalysis] = useState<StockAnalysis | null>(null)

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-gray-900">Stock Analysis</h1>
                <p className="text-gray-600 mt-1">
                    Get AI-powered technical and fundamental analysis
                </p>
            </div>

            <StockAnalysisForm onAnalysisComplete={setAnalysis} />

            {analysis && (
                <div>
                    <h2 className="text-2xl font-bold mb-4">
                        Analysis: {analysis.symbol}
                    </h2>
                    <AnalysisResult analysis={analysis} />
                </div>
            )}
        </div>
    )
}
