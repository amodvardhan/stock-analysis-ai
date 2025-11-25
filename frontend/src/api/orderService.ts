import { apiClient } from './client';

export interface OrderCreateRequest {
    symbol: string;
    market: string;
    order_type: 'market' | 'limit' | 'stop_loss' | 'stop_limit';
    side: 'BUY' | 'SELL';
    quantity: number;
    limit_price?: number;
    stop_price?: number;
    expires_at?: string;
    notes?: string;
}

export interface Order {
    id: number;
    symbol: string;
    order_type: string;
    side: string;
    quantity: number;
    filled_quantity: number;
    limit_price: number | null;
    status: string;
    created_at: string;
    filled_at: string | null;
}

export const orderService = {
    async createOrder(request: OrderCreateRequest): Promise<Order> {
        const response = await apiClient.post('api/v1/orders/', request);
        return response.data;
    },

    async getOrders(status?: string): Promise<Order[]> {
        const params = status ? { status_filter: status } : {};
        const response = await apiClient.get('api/v1/orders/', { params });
        return response.data;
    },

    async cancelOrder(orderId: number): Promise<{ id: number; status: string; cancelled_at: string }> {
        const response = await apiClient.delete(`api/v1/orders/${orderId}`);
        return response.data;
    }
};

