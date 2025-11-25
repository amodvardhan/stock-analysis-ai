import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuthStore } from '@/stores/authStore';

interface PriceUpdate {
    type: 'price_update';
    symbol: string;
    market: string;
    current_price: number;
    previous_close: number;
    change: number;
    change_percent: number;
    timestamp: string;
}

interface WebSocketMessage {
    type: string;
    [key: string]: any;
}

export const useWebSocket = (symbols: string[] = [], market: string = 'india_nse') => {
    const { token } = useAuthStore();
    const [isConnected, setIsConnected] = useState(false);
    const [priceUpdates, setPriceUpdates] = useState<Map<string, PriceUpdate>>(new Map());
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

    const connect = useCallback(() => {
        if (!token) {
            console.warn('No token available for WebSocket connection');
            return;
        }

        const wsUrl = `${import.meta.env.VITE_API_URL?.replace('http', 'ws') || 'ws://localhost:8000'}/ws?token=${token}`;
        const ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            console.log('WebSocket connected');
            setIsConnected(true);
            
            // Subscribe to all symbols
            symbols.forEach(symbol => {
                ws.send(JSON.stringify({
                    action: 'subscribe',
                    symbol: symbol,
                    market: market
                }));
            });
        };

        ws.onmessage = (event) => {
            try {
                const message: WebSocketMessage = JSON.parse(event.data);
                
                if (message.type === 'price_update') {
                    const update = message as PriceUpdate;
                    setPriceUpdates(prev => {
                        const newMap = new Map(prev);
                        newMap.set(update.symbol, update);
                        return newMap;
                    });
                } else if (message.type === 'subscription_confirmed') {
                    console.log(`Subscribed to ${message.symbol}`);
                } else if (message.type === 'pong') {
                    // Heartbeat response
                }
            } catch (error) {
                console.error('Error parsing WebSocket message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setIsConnected(false);
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            setIsConnected(false);
            
            // Attempt to reconnect after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
                connect();
            }, 3000);
        };

        wsRef.current = ws;
    }, [token, symbols, market]);

    const disconnect = useCallback(() => {
        if (reconnectTimeoutRef.current) {
            clearTimeout(reconnectTimeoutRef.current);
        }
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        setIsConnected(false);
    }, []);

    const subscribe = useCallback((symbol: string, market: string) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                action: 'subscribe',
                symbol: symbol,
                market: market
            }));
        }
    }, []);

    const unsubscribe = useCallback((symbol: string, market: string) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({
                action: 'unsubscribe',
                symbol: symbol,
                market: market
            }));
        }
    }, []);

    useEffect(() => {
        if (symbols.length > 0 && token) {
            connect();
        }

        return () => {
            disconnect();
        };
    }, [symbols.join(','), market, token, connect, disconnect]);

    return {
        isConnected,
        priceUpdates,
        subscribe,
        unsubscribe,
        connect,
        disconnect
    };
};

