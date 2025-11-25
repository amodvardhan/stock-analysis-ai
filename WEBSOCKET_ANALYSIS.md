# WebSocket Real-Time Stock Price Updates - Architecture Analysis

## Executive Summary

✅ **WebSocket infrastructure is FULLY IMPLEMENTED** in your codebase  
⚠️ **WebSocket is only PARTIALLY USED** - Currently active in 1 out of ~11 pages that display stock prices

---

## 1. Backend WebSocket Implementation ✅

### Location: `/backend/api/routes/websocket.py`

**Status**: ✅ **FULLY IMPLEMENTED**

**Key Features**:
- WebSocket endpoint at `/ws` (registered in `main.py`)
- JWT token authentication via query parameter
- Connection management with `ConnectionManager` class
- Subscribe/unsubscribe to stock symbols
- Background task that updates prices every 5 seconds
- Broadcasts price updates to all subscribed connections
- Handles disconnections gracefully

**Architecture**:
```python
ConnectionManager:
  - active_connections: Dict[user_id -> Set[WebSocket]]
  - subscriptions: Dict[WebSocket -> Set[symbol:market]]
  - start_price_updates(): Background task (5-second interval)
```

**WebSocket Message Protocol**:
- **Client → Server**:
  - Subscribe: `{"action": "subscribe", "symbol": "RELIANCE", "market": "india_nse"}`
  - Unsubscribe: `{"action": "unsubscribe", "symbol": "RELIANCE", "market": "india_nse"}`
  - Ping: `{"action": "ping"}`

- **Server → Client**:
  - Price Update: `{"type": "price_update", "symbol": "...", "current_price": ..., "change": ..., "change_percent": ..., "timestamp": "..."}`
  - Subscription Confirmed: `{"type": "subscription_confirmed", "symbol": "...", "market": "..."}`
  - Pong: `{"type": "pong"}`

**Connection URL**: `ws://host/ws?token=JWT_TOKEN`

---

## 2. Frontend WebSocket Implementation ✅

### Location: `/frontend/src/hooks/useWebSocket.ts`

**Status**: ✅ **FULLY IMPLEMENTED**

**Features**:
- React hook `useWebSocket(symbols[], market)`
- Automatic connection management
- Auto-reconnect on disconnect (3-second delay)
- Subscribes to all provided symbols on connect
- Returns `priceUpdates` Map with real-time data
- Connection status indicator (`isConnected`)

**Usage Pattern**:
```typescript
const { isConnected, priceUpdates, subscribe, unsubscribe } = useWebSocket(
  ['RELIANCE', 'TCS'], 
  'india_nse'
);

// Access real-time price
const liveUpdate = priceUpdates.get('RELIANCE');
const currentPrice = liveUpdate?.current_price;
```

---

## 3. Current WebSocket Usage in Frontend

### ✅ **ACTIVELY USING WebSocket**:

1. **RecommendationsPage.tsx** ✅
   - **Location**: `/frontend/src/pages/RecommendationsPage.tsx`
   - **Usage**: Lines 8, 24, 31-32, 160, 166, 242-244
   - **Features**:
     - Subscribes to all recommendation symbols
     - Shows live price updates with animations
     - Displays connection status (Wifi/WifiOff icon)
     - Updates heat map with real-time data
     - Price change animations (up/down indicators)

### ❌ **NOT USING WebSocket (But Should)**:

1. **WatchlistPage.tsx** ❌
   - **Location**: `/frontend/src/pages/WatchlistPage.tsx`
   - **Current**: Shows static `current_price` from API (line 223-226)
   - **Should**: Use WebSocket to show real-time prices for all watchlist items
   - **Impact**: HIGH - Watchlist is specifically for monitoring stocks

2. **MarketMoversPage.tsx** ❌
   - **Location**: `/frontend/src/pages/MarketMoversPage.tsx`
   - **Current**: Shows static prices from API (line 161)
   - **Should**: Use WebSocket to show real-time prices for top movers
   - **Impact**: HIGH - Market movers need live updates

3. **DashboardPage.tsx** ❌
   - **Location**: `/frontend/src/pages/DashboardPage.tsx`
   - **Current**: Shows static market overview data (lines 115-127, 151-156, 179-184)
   - **Should**: Use WebSocket for market indices and top movers
   - **Impact**: MEDIUM - Dashboard should show live data

4. **Portfolio.tsx** ❌
   - **Location**: `/frontend/src/pages/Portfolio.tsx`
   - **Current**: Likely shows static portfolio values
   - **Should**: Use WebSocket to update portfolio values in real-time
   - **Impact**: HIGH - Portfolio tracking needs live P&L

5. **AnalysisPage.tsx** ❌
   - **Location**: `/frontend/src/pages/AnalysisPage.tsx`
   - **Current**: Shows analysis results with static prices
   - **Should**: Use WebSocket to show live price while viewing analysis
   - **Impact**: MEDIUM - Nice to have live price during analysis

6. **Other Pages** (Lower Priority):
   - `PeerComparisonPage.tsx` - Could show live prices for comparison
   - `OptionsChainPage.tsx` - Could show live underlying stock price
   - `SectorAnalysisPage.tsx` - Could show live sector prices

---

## 4. WebSocket Architecture Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  RecommendationsPage.tsx                           │   │
│  │  ✅ Uses useWebSocket(['RELIANCE', 'TCS'])         │   │
│  └───────────────────┬────────────────────────────────┘   │
│                      │                                       │
│  ┌───────────────────▼────────────────────────────────┐   │
│  │  useWebSocket Hook                                 │   │
│  │  - Connects to ws://host/ws?token=JWT            │   │
│  │  - Subscribes to symbols                          │   │
│  │  - Receives price updates                         │   │
│  │  - Auto-reconnects on disconnect                  │   │
│  └───────────────────┬────────────────────────────────┘   │
└──────────────────────┼──────────────────────────────────────┘
                       │ WebSocket Connection
                       │ (ws:// or wss://)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐   │
│  │  /ws endpoint (main.py:419-422)                    │   │
│  │  - Authenticates via JWT token                      │   │
│  │  - Accepts WebSocket connection                    │   │
│  └───────────────────┬────────────────────────────────┘   │
│                      │                                       │
│  ┌───────────────────▼────────────────────────────────┐   │
│  │  ConnectionManager (websocket.py)                   │   │
│  │  - Manages active connections                       │   │
│  │  - Tracks subscriptions per connection             │   │
│  │  - Background task: start_price_updates()          │   │
│  │    └─ Updates every 5 seconds                      │   │
│  └───────────────────┬────────────────────────────────┘   │
│                      │                                       │
│  ┌───────────────────▼────────────────────────────────┐   │
│  │  get_stock_price() (stock_price_tool.py)          │   │
│  │  - Fetches latest price from API                   │   │
│  │  - Returns: current_price, change, change_percent  │   │
│  └────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 5. Implementation Status Summary

| Component | Status | Notes |
|-----------|--------|-------|
| **Backend WebSocket Server** | ✅ Complete | Fully functional with connection management |
| **Frontend WebSocket Hook** | ✅ Complete | `useWebSocket.ts` ready to use |
| **RecommendationsPage** | ✅ Using | Real-time prices working |
| **WatchlistPage** | ❌ Missing | **MUST HAVE** - Core feature for monitoring |
| **MarketMoversPage** | ❌ Missing | **MUST HAVE** - Shows active stocks |
| **DashboardPage** | ❌ Missing | Should show live market data |
| **Portfolio** | ❌ Missing | **MUST HAVE** - Real-time P&L |
| **AnalysisPage** | ❌ Missing | Nice to have live price |

---

## 6. Recommendations

### Priority 1: **MUST IMPLEMENT** (Critical for real-time features)

1. **WatchlistPage.tsx**
   - Extract symbols from watchlist items
   - Use `useWebSocket` hook
   - Update price column with live data
   - Show connection status

2. **MarketMoversPage.tsx**
   - Extract symbols from movers (gainers/losers/active)
   - Use `useWebSocket` hook
   - Update price and change columns
   - Highlight real-time updates

3. **Portfolio.tsx**
   - Extract symbols from portfolio holdings
   - Use `useWebSocket` hook
   - Calculate real-time portfolio value
   - Show live P&L

### Priority 2: **SHOULD IMPLEMENT** (Enhances UX)

4. **DashboardPage.tsx**
   - Subscribe to market indices (if available)
   - Subscribe to top movers shown on dashboard
   - Update market overview cards

### Priority 3: **NICE TO HAVE** (Optional)

5. **AnalysisPage.tsx**
   - Show live price while viewing analysis
   - Update price if user stays on page

---

## 7. Implementation Example

### Adding WebSocket to WatchlistPage.tsx:

```typescript
// Add import
import { useWebSocket } from '../hooks/useWebSocket';

// Inside component
const WatchlistPage: React.FC = () => {
    const [items, setItems] = useState<WatchlistItem[]>([]);
    // ... existing code ...
    
    // Extract symbols for WebSocket
    const symbols = useMemo(() => 
        items.map(item => item.stock.symbol),
        [items]
    );
    const market = items[0]?.stock.market || 'india_nse';
    
    // Connect to WebSocket
    const { isConnected, priceUpdates } = useWebSocket(symbols, market);
    
    // In WatchlistRow component, use live price:
    const liveUpdate = priceUpdates.get(item.stock.symbol);
    const current_price = liveUpdate?.current_price ?? item.stock.current_price;
    const priceChange = liveUpdate?.change ?? 0;
    const priceChangePercent = liveUpdate?.change_percent ?? 0;
    
    // Display with live indicator
    <td>
        <div className="flex items-center gap-2">
            <span>₹{current_price.toFixed(2)}</span>
            {liveUpdate && (
                <span className="text-xs text-primary-600">
                    <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                    Live
                </span>
            )}
        </div>
    </td>
```

---

## 8. Backend WebSocket Performance

**Current Implementation**:
- Updates every **5 seconds** (configurable via `interval` parameter)
- Fetches price for each unique subscription
- Broadcasts to all connections subscribed to that symbol

**Optimization Opportunities**:
1. **Caching**: Cache prices for 1-2 seconds to avoid duplicate API calls
2. **Batching**: Batch API calls for multiple symbols
3. **Rate Limiting**: Respect API rate limits
4. **Connection Pooling**: Optimize for many concurrent connections

**Scalability**:
- Current implementation works well for < 100 concurrent connections
- For larger scale, consider:
  - Redis pub/sub for distributed updates
  - Message queue for price updates
  - Separate WebSocket server instance

---

## 9. Testing WebSocket

### Manual Testing:

1. **Connect to WebSocket**:
   ```bash
   # Using wscat (npm install -g wscat)
   wscat -c "ws://localhost:8000/ws?token=YOUR_JWT_TOKEN"
   ```

2. **Subscribe to symbol**:
   ```json
   {"action": "subscribe", "symbol": "RELIANCE", "market": "india_nse"}
   ```

3. **Receive updates**:
   - Should receive price updates every 5 seconds
   - Format: `{"type": "price_update", "symbol": "RELIANCE", ...}`

### Frontend Testing:
- Open browser DevTools → Network → WS tab
- Verify WebSocket connection established
- Check messages being sent/received
- Verify reconnection on disconnect

---

## 10. Conclusion

✅ **WebSocket infrastructure is production-ready**  
⚠️ **Only 1 out of ~11 pages using it** - Significant opportunity to enhance UX

**Next Steps**:
1. Implement WebSocket in WatchlistPage (Priority 1)
2. Implement WebSocket in MarketMoversPage (Priority 1)
3. Implement WebSocket in Portfolio (Priority 1)
4. Add WebSocket to DashboardPage (Priority 2)
5. Consider adding to other pages (Priority 3)

**Estimated Implementation Time**:
- Priority 1 (3 pages): ~2-3 hours
- Priority 2 (1 page): ~1 hour
- Priority 3 (optional): ~1-2 hours

---

**Document Created**: $(date)  
**Last Updated**: $(date)  
**Status**: Ready for Implementation

