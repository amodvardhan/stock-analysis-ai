import React, { useState } from 'react';
import { portfolioService } from '../api/portfolioService';
import { AddHoldingRequest } from '../types';
import { toast } from 'react-hot-toast';

interface AddHoldingModalProps {
    onClose: () => void;
    onSuccess: () => void;
}

const AddHoldingModal: React.FC<AddHoldingModalProps> = ({ onClose, onSuccess }) => {
    const [formData, setFormData] = useState<AddHoldingRequest>({
        symbol: '',
        market: 'india_nse',
        quantity: 0,
        purchase_price: 0,
        purchase_date: new Date().toISOString().split('T')[0],
        brokerage_fee: 0,
        tax: 0,
        notes: '',
    });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!formData.symbol || formData.quantity <= 0 || formData.purchase_price <= 0) {
            toast.error('Please fill all required fields');
            return;
        }

        try {
            setLoading(true);
            await portfolioService.addHolding({
                ...formData,
                symbol: formData.symbol.toUpperCase(),
            });
            onSuccess();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to add stock');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setFormData((prev) => ({
            ...prev,
            [name]: name === 'quantity' || name === 'purchase_price' || name === 'brokerage_fee' || name === 'tax'
                ? parseFloat(value) || 0
                : value,
        }));
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
            <div className="bg-white dark:bg-slate-800 rounded-2xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto animate-scale-in">
                <div className="px-6 lg:px-8 py-5 border-b border-gray-200 dark:border-slate-700 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 flex justify-between items-center sticky top-0 bg-white dark:bg-slate-800 rounded-t-2xl">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-primary-700 rounded-xl flex items-center justify-center">
                            <span className="text-white text-xl font-bold">+</span>
                        </div>
                        <h2 className="text-xl lg:text-2xl font-bold text-gray-900 dark:text-gray-100">Add Stock to Portfolio</h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="w-8 h-8 flex items-center justify-center text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-lg transition-all"
                    >
                        ✕
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 lg:p-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Stock Symbol */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Stock Symbol *
                            </label>
                            <input
                                type="text"
                                name="symbol"
                                value={formData.symbol}
                                onChange={handleChange}
                                placeholder="e.g., RELIANCE"
                                className="input-field"
                                required
                            />
                        </div>

                        {/* Market */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Market *
                            </label>
                            <select
                                name="market"
                                value={formData.market}
                                onChange={handleChange}
                                className="input-field"
                            >
                                <option value="india_nse">India NSE</option>
                                <option value="india_bse">India BSE</option>
                                <option value="us_nyse">US NYSE</option>
                                <option value="us_nasdaq">US NASDAQ</option>
                            </select>
                        </div>

                        {/* Quantity */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Quantity *
                            </label>
                            <input
                                type="number"
                                name="quantity"
                                value={formData.quantity || ''}
                                onChange={handleChange}
                                placeholder="Number of shares"
                                min="1"
                                className="input-field"
                                required
                            />
                        </div>

                        {/* Purchase Price */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Purchase Price (₹) *
                            </label>
                            <input
                                type="number"
                                name="purchase_price"
                                value={formData.purchase_price || ''}
                                onChange={handleChange}
                                placeholder="Price per share"
                                step="0.01"
                                min="0.01"
                                className="input-field"
                                required
                            />
                        </div>

                        {/* Purchase Date */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Purchase Date
                            </label>
                            <input
                                type="date"
                                name="purchase_date"
                                value={formData.purchase_date}
                                onChange={handleChange}
                                className="input-field"
                            />
                        </div>

                        {/* Brokerage Fee */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Brokerage Fee (₹)
                            </label>
                            <input
                                type="number"
                                name="brokerage_fee"
                                value={formData.brokerage_fee || ''}
                                onChange={handleChange}
                                placeholder="Optional"
                                step="0.01"
                                min="0"
                                className="input-field"
                            />
                        </div>

                        {/* Tax */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Tax (₹)
                            </label>
                            <input
                                type="number"
                                name="tax"
                                value={formData.tax || ''}
                                onChange={handleChange}
                                placeholder="Optional"
                                step="0.01"
                                min="0"
                                className="input-field"
                            />
                        </div>

                        {/* Total Cost Display */}
                        <div className="md:col-span-2 bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/30 dark:to-blue-900/30 p-5 rounded-xl border border-primary-200 dark:border-primary-800">
                            <p className="text-sm text-gray-600 dark:text-gray-300 mb-1 font-medium">Total Investment</p>
                            <p className="text-2xl font-bold text-primary-700 dark:text-primary-400">
                                ₹{(
                                    (formData.quantity || 0) * (formData.purchase_price || 0) +
                                    (formData.brokerage_fee || 0) +
                                    (formData.tax || 0)
                                ).toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                            </p>
                        </div>

                        {/* Notes */}
                        <div className="md:col-span-2">
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Notes (Optional)
                            </label>
                            <textarea
                                name="notes"
                                value={formData.notes}
                                onChange={handleChange}
                                rows={3}
                                placeholder="Any additional notes..."
                                className="input-field"
                            />
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex justify-end gap-3 mt-8 pt-6 border-t border-gray-200 dark:border-slate-700">
                        <button
                            type="button"
                            onClick={onClose}
                            className="btn-secondary"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="btn-primary"
                        >
                            {loading ? 'Adding...' : 'Add to Portfolio'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AddHoldingModal;
