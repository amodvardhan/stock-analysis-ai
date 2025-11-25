# Backend Simplification Plan

## Recommendation: **Keep Code, Hide from Main API**

### Why Keep the Code?

1. **Already Built & Tested** - Removing means losing working code
2. **Future Flexibility** - Can re-enable if users request
3. **Internal Use** - Some features (like Financials, News) are used by core features
4. **No Breaking Changes** - Existing integrations won't break

### Why Hide from Main API?

1. **Cleaner API** - Only expose core features
2. **Focused Development** - Focus on core features
3. **Beginner-Friendly** - Don't expose advanced endpoints
4. **Can Re-enable** - Easy to add back if needed

## Implementation Plan

### Step 1: Separate Core vs Advanced Routes

**Core Routes** (Keep in main API):
- ✅ `/api/v1/auth/*` - Authentication
- ✅ `/api/v1/analysis/*` - Stock analysis
- ✅ `/api/v1/recommendations/*` - AI recommendations
- ✅ `/api/v1/portfolio/*` - Portfolio management
- ✅ `/api/v1/watchlist/*` - Watchlist
- ✅ `/api/v1/market/overview` - Market overview
- ✅ `/api/v1/market/movers` - Market movers
- ✅ `/api/v1/market/sectors` - Sector analysis
- ✅ `/api/v1/market/news` - News (used in Stock Analysis)
- ✅ `/api/v1/market/financials/{symbol}` - Financials (used in Stock Analysis)
- ✅ `/api/v1/market/compare` - Peer comparison (useful, but not essential)

**Advanced Routes** (Keep code, hide from main API):
- ⚠️ `/api/v1/market/options/{symbol}` - Options chain
- ⚠️ `/api/v1/market/corporate-actions/{symbol}` - Corporate actions
- ⚠️ `/api/v1/market/earnings` - Earnings calendar
- ⚠️ `/api/v1/backtesting/*` - Backtesting
- ⚠️ `/api/v1/orders/*` - Orders (if not actually trading)
- ⚠️ `/api/v1/risk/*` - Risk (integrate into portfolio instead)

**Keep but Internal**:
- ✅ `/api/v1/market/financials/{symbol}` - Used by Stock Analysis
- ✅ `/api/v1/market/news` - Used by Stock Analysis
- ✅ `/api/v1/explainability/*` - Used by Recommendations (XAI)

### Step 2: Create Advanced Features Router (Optional)

Create a separate router for advanced features that can be enabled/disabled:

```python
# backend/api/routes/advanced.py
# Advanced features - not in main navigation but accessible if needed
advanced_router = APIRouter()

# Only include if ENABLE_ADVANCED_FEATURES=true
if settings.ENABLE_ADVANCED_FEATURES:
    advanced_router.include_router(options_router, prefix="/options")
    advanced_router.include_router(backtesting_router, prefix="/backtesting")
    # etc.
```

### Step 3: Mark Services as "Advanced"

Add comments to services:
```python
# ADVANCED FEATURE - Not exposed in main API
# Can be enabled via advanced router if needed
```

## Recommended Approach

### Option A: **Keep All, Hide Advanced** (Recommended)
- ✅ Keep all backend code
- ✅ Remove advanced routes from main API router
- ✅ Keep services/agents (used internally)
- ✅ Can re-enable easily

**Pros:**
- No code loss
- Flexible
- Easy to re-enable
- Internal features still work

**Cons:**
- Some unused code
- Slightly larger codebase

### Option B: **Remove Advanced Completely**
- ❌ Delete advanced services/agents
- ❌ Delete advanced routes
- ❌ Cleaner codebase

**Pros:**
- Cleaner codebase
- Focused development

**Cons:**
- Lose working code
- Hard to add back
- Breaking changes

## My Recommendation: **Option A**

**Keep the code, but:**
1. Remove advanced routes from main API router
2. Keep services/agents (some are used internally)
3. Mark as "advanced" in comments
4. Can create separate advanced router if needed

**Why?**
- Financials service is used by Stock Analysis
- News service is used by Stock Analysis  
- Options/Backtesting can be re-enabled if users request
- No breaking changes
- Focused API for beginners

## Files to Modify

1. ✅ `backend/api/routes/__init__.py` - Remove advanced routes from main router
2. ✅ Keep all services (they're used internally)
3. ✅ Keep all agents (they're used internally)
4. ✅ Add comments marking advanced features

## Result

- **Main API**: Only core features exposed
- **Backend Code**: All kept, some hidden
- **Flexibility**: Can re-enable advanced features
- **Focus**: Beginner-friendly API

