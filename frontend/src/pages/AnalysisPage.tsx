import { useState } from 'react'
import { StockAnalysisForm } from '@/components/analysis/StockAnalysisForm'
import { AnalysisResult } from '@/components/analysis/AnalysisResult'
import type { StockAnalysis } from '@/types'
import { Sparkles } from 'lucide-react'

export const AnalysisPage = () => {
    const [analysis, setAnalysis] = useState<StockAnalysis | null>(null)

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

            {analysis && (
                <div className="animate-slide-up">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="w-1 h-8 bg-gradient-to-b from-primary-600 to-primary-700 rounded-full"></div>
                        <h2 className="text-2xl lg:text-3xl font-bold text-gray-900">
                            Analysis: <span className="text-gradient">{analysis.symbol}</span>
                        </h2>
                    </div>
                    <AnalysisResult analysis={analysis} />
                </div>
            )}
        </div>
    )
}
