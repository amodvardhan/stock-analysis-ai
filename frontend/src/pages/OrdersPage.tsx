import React, { useState, useEffect } from 'react';
import { Plus, X, TrendingUp, TrendingDown, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { orderService, Order, OrderCreateRequest } from '../api/orderService';
import { useTheme } from '@/contexts/ThemeContext';

export const OrdersPage = () => {
    const { theme } = useTheme();
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [selectedStatus, setSelectedStatus] = useState<string>('');

    const [formData, setFormData] = useState<OrderCreateRequest>({
        symbol: '',
        market: 'india_nse',
        order_type: 'market',
        side: 'BUY',
        quantity: 0,
        limit_price: undefined,
        stop_price: undefined,
        notes: ''
    });

    useEffect(() => {
        loadOrders();
    }, [selectedStatus]);

    const loadOrders = async () => {
        try {
            setLoading(true);
            const data = await orderService.getOrders(selectedStatus || undefined);
            setOrders(data);
        } catch (error: any) {
            toast.error('Failed to load orders');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateOrder = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await orderService.createOrder(formData);
            toast.success('Order created successfully');
            setShowCreateModal(false);
            setFormData({
                symbol: '',
                market: 'india_nse',
                order_type: 'market',
                side: 'BUY',
                quantity: 0,
                limit_price: undefined,
                stop_price: undefined,
                notes: ''
            });
            loadOrders();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to create order');
        }
    };

    const handleCancelOrder = async (orderId: number) => {
        if (!confirm('Are you sure you want to cancel this order?')) return;

        try {
            await orderService.cancelOrder(orderId);
            toast.success('Order cancelled');
            loadOrders();
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Failed to cancel order');
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'filled':
                return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300';
            case 'pending':
            case 'submitted':
                return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300';
            case 'cancelled':
            case 'rejected':
                return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300';
            default:
                return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'filled':
                return <CheckCircle className="w-4 h-4" />;
            case 'cancelled':
            case 'rejected':
                return <XCircle className="w-4 h-4" />;
            default:
                return <Clock className="w-4 h-4" />;
        }
    };

    const isDark = theme === 'dark';

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl lg:text-4xl font-bold mb-2 text-gray-900 dark:text-gray-100">Order Management</h1>
                    <p className="text-gray-600 dark:text-gray-400 text-lg">
                        Create and manage your trading orders
                    </p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="btn-primary flex items-center gap-2"
                >
                    <Plus className="w-5 h-5" />
                    New Order
                </button>
            </div>

            {/* Status Filter */}
            <div className="flex gap-2">
                <button
                    onClick={() => setSelectedStatus('')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${selectedStatus === ''
                            ? 'bg-primary-600 text-white'
                            : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                        }`}
                >
                    All
                </button>
                {['pending', 'submitted', 'filled', 'cancelled'].map(status => (
                    <button
                        key={status}
                        onClick={() => setSelectedStatus(status)}
                        className={`px-4 py-2 rounded-lg font-medium capitalize transition-colors ${selectedStatus === status
                                ? 'bg-primary-600 text-white'
                                : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                            }`}
                    >
                        {status}
                    </button>
                ))}
            </div>

            {/* Orders Table */}
            {loading ? (
                <div className="card text-center py-16">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400 mx-auto"></div>
                </div>
            ) : orders.length === 0 ? (
                <div className="card text-center py-16">
                    <AlertCircle className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400 font-medium">No orders found</p>
                    <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
                        Create your first order to get started
                    </p>
                </div>
            ) : (
                <div className="card overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className={`${isDark ? 'bg-gray-800' : 'bg-gray-50'}`}>
                                <tr>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Symbol</th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Type</th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Side</th>
                                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Quantity</th>
                                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Filled</th>
                                    <th className="text-right py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Price</th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Status</th>
                                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Date</th>
                                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700 dark:text-gray-300">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {orders.map((order) => (
                                    <tr key={order.id} className={`border-b ${isDark ? 'border-gray-700 hover:bg-gray-800/50' : 'border-gray-100 hover:bg-gray-50'}`}>
                                        <td className="py-3 px-4">
                                            <span className="font-semibold text-gray-900 dark:text-gray-100">{order.symbol}</span>
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className="text-sm capitalize text-gray-700 dark:text-gray-300">{order.order_type}</span>
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-bold ${order.side === 'BUY'
                                                    ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                                                    : 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                                                }`}>
                                                {order.side === 'BUY' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                                {order.side}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-right text-gray-900 dark:text-gray-100">{order.quantity}</td>
                                        <td className="py-3 px-4 text-right text-gray-900 dark:text-gray-100">{order.filled_quantity}</td>
                                        <td className="py-3 px-4 text-right text-gray-900 dark:text-gray-100">
                                            {order.limit_price ? `$${order.limit_price.toFixed(2)}` : 'Market'}
                                        </td>
                                        <td className="py-3 px-4">
                                            <span className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-bold ${getStatusColor(order.status)}`}>
                                                {getStatusIcon(order.status)}
                                                {order.status}
                                            </span>
                                        </td>
                                        <td className="py-3 px-4 text-sm text-gray-700 dark:text-gray-300">
                                            {new Date(order.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="py-3 px-4 text-center">
                                            {order.status === 'pending' || order.status === 'submitted' ? (
                                                <button
                                                    onClick={() => handleCancelOrder(order.id)}
                                                    className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                                                >
                                                    <X className="w-4 h-4" />
                                                </button>
                                            ) : (
                                                <span className="text-gray-400">-</span>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Create Order Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
                    <div className={`card max-w-2xl w-full max-h-[90vh] overflow-y-auto ${isDark ? 'bg-slate-800' : 'bg-white'}`}>
                        <div className="flex items-center justify-between mb-6">
                            <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100">Create New Order</h2>
                            <button
                                onClick={() => setShowCreateModal(false)}
                                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        <form onSubmit={handleCreateOrder} className="space-y-4">
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Symbol</label>
                                    <input
                                        type="text"
                                        value={formData.symbol}
                                        onChange={(e) => setFormData({ ...formData, symbol: e.target.value.toUpperCase() })}
                                        className="input-field"
                                        placeholder="RELIANCE"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Market</label>
                                    <select
                                        value={formData.market}
                                        onChange={(e) => setFormData({ ...formData, market: e.target.value })}
                                        className="input-field"
                                    >
                                        <option value="india_nse">India NSE</option>
                                        <option value="india_bse">India BSE</option>
                                        <option value="us_nyse">US NYSE</option>
                                        <option value="us_nasdaq">US NASDAQ</option>
                                    </select>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Order Type</label>
                                    <select
                                        value={formData.order_type}
                                        onChange={(e) => setFormData({ ...formData, order_type: e.target.value as any })}
                                        className="input-field"
                                    >
                                        <option value="market">Market</option>
                                        <option value="limit">Limit</option>
                                        <option value="stop_loss">Stop Loss</option>
                                        <option value="stop_limit">Stop Limit</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Side</label>
                                    <select
                                        value={formData.side}
                                        onChange={(e) => setFormData({ ...formData, side: e.target.value as any })}
                                        className="input-field"
                                    >
                                        <option value="BUY">Buy</option>
                                        <option value="SELL">Sell</option>
                                    </select>
                                </div>
                            </div>

                            <div>
                                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Quantity</label>
                                <input
                                    type="number"
                                    value={formData.quantity}
                                    onChange={(e) => setFormData({ ...formData, quantity: parseInt(e.target.value) })}
                                    className="input-field"
                                    min="1"
                                    required
                                />
                            </div>

                            {(formData.order_type === 'limit' || formData.order_type === 'stop_limit') && (
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Limit Price</label>
                                    <input
                                        type="number"
                                        value={formData.limit_price || ''}
                                        onChange={(e) => setFormData({ ...formData, limit_price: parseFloat(e.target.value) || undefined })}
                                        className="input-field"
                                        min="0"
                                        step="0.01"
                                        required={formData.order_type === 'limit' || formData.order_type === 'stop_limit'}
                                    />
                                </div>
                            )}

                            {(formData.order_type === 'stop_loss' || formData.order_type === 'stop_limit') && (
                                <div>
                                    <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Stop Price</label>
                                    <input
                                        type="number"
                                        value={formData.stop_price || ''}
                                        onChange={(e) => setFormData({ ...formData, stop_price: parseFloat(e.target.value) || undefined })}
                                        className="input-field"
                                        min="0"
                                        step="0.01"
                                        required={formData.order_type === 'stop_loss' || formData.order_type === 'stop_limit'}
                                    />
                                </div>
                            )}

                            <div>
                                <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">Notes (Optional)</label>
                                <textarea
                                    value={formData.notes}
                                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                                    className="input-field"
                                    rows={3}
                                />
                            </div>

                            <div className="flex gap-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowCreateModal(false)}
                                    className="btn-secondary flex-1"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="btn-primary flex-1"
                                >
                                    Create Order
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

