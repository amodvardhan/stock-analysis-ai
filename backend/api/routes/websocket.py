"""
=============================================================================
WebSocket Routes for Real-Time Stock Price Updates
=============================================================================
Provides real-time stock price streaming via WebSocket connections.
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from typing import Dict, Set, List
import json
import asyncio
import structlog
from datetime import datetime

from core.database import get_db
from db.models import User
from utils.security import decode_access_token
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import AsyncSessionLocal
from agents.tools.stock_price_tool import get_stock_price

logger = structlog.get_logger()


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        # Map of user_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Map of connection -> subscribed symbols
        self.subscriptions: Dict[WebSocket, Set[str]] = {}
        # Background task for price updates
        self.update_task: asyncio.Task = None
        
    async def connect(self, websocket: WebSocket, user_id: str):
        """Register a new WebSocket connection."""
        # Note: websocket.accept() is called in websocket_endpoint before this
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        
        self.active_connections[user_id].add(websocket)
        self.subscriptions[websocket] = set()
        
        logger.info("websocket_connected", user_id=user_id)
        
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        
        logger.info("websocket_disconnected", user_id=user_id)
    
    async def subscribe(self, websocket: WebSocket, symbol: str, market: str = "india_nse"):
        """Subscribe to price updates for a symbol."""
        if websocket not in self.subscriptions:
            self.subscriptions[websocket] = set()
        
        subscription_key = f"{symbol}:{market}"
        self.subscriptions[websocket].add(subscription_key)
        
        logger.info("websocket_subscribed", symbol=symbol, market=market)
        
        # Send initial price
        await self.send_price_update(websocket, symbol, market)
    
    async def unsubscribe(self, websocket: WebSocket, symbol: str, market: str = "india_nse"):
        """Unsubscribe from price updates for a symbol."""
        if websocket in self.subscriptions:
            subscription_key = f"{symbol}:{market}"
            self.subscriptions[websocket].discard(subscription_key)
        
        logger.info("websocket_unsubscribed", symbol=symbol, market=market)
    
    async def send_price_update(self, websocket: WebSocket, symbol: str, market: str):
        """Send price update to a specific connection."""
        try:
            price_data = await get_stock_price.ainvoke({
                "symbol": symbol,
                "market": market,
                "period": "1d"
            })
            
            message = {
                "type": "price_update",
                "symbol": symbol,
                "market": market,
                "current_price": price_data.get("current_price"),
                "previous_close": price_data.get("previous_close"),
                "change": price_data.get("change"),
                "change_percent": price_data.get("change_percent"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            await websocket.send_json(message)
        except Exception as e:
            logger.error("websocket_send_error", symbol=symbol, error=str(e))
    
    async def broadcast_to_user(self, user_id: str, message: dict):
        """Send message to all connections of a user."""
        if user_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error("websocket_broadcast_error", user_id=user_id, error=str(e))
                    disconnected.append(websocket)
            
            # Clean up disconnected sockets
            for ws in disconnected:
                self.disconnect(ws, user_id)
    
    async def start_price_updates(self, interval: int = 5):
        """Background task to update prices for all subscriptions."""
        while True:
            try:
                await asyncio.sleep(interval)
                
                # Collect all unique subscriptions
                all_subscriptions: Dict[str, Set[WebSocket]] = {}
                for websocket, subscriptions in self.subscriptions.items():
                    for sub in subscriptions:
                        if sub not in all_subscriptions:
                            all_subscriptions[sub] = set()
                        all_subscriptions[sub].add(websocket)
                
                # Update prices for each subscription
                for subscription_key, websockets in all_subscriptions.items():
                    symbol, market = subscription_key.split(":", 1)
                    price_data = await get_stock_price.ainvoke({
                        "symbol": symbol,
                        "market": market,
                        "period": "1d"
                    })
                    
                    message = {
                        "type": "price_update",
                        "symbol": symbol,
                        "market": market,
                        "current_price": price_data.get("current_price"),
                        "previous_close": price_data.get("previous_close"),
                        "change": price_data.get("change"),
                        "change_percent": price_data.get("change_percent"),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    # Send to all subscribed connections
                    disconnected = []
                    for websocket in websockets:
                        try:
                            await websocket.send_json(message)
                        except Exception as e:
                            logger.error("websocket_update_error", symbol=symbol, error=str(e))
                            disconnected.append(websocket)
                    
                    # Clean up disconnected sockets
                    for ws in disconnected:
                        if ws in self.subscriptions:
                            del self.subscriptions[ws]
                            
            except Exception as e:
                logger.error("price_update_task_error", error=str(e))
                await asyncio.sleep(interval)


# Global connection manager
manager = ConnectionManager()


async def get_current_user_ws(token: str) -> User:
    """Get user from WebSocket token."""
    try:
        email = decode_access_token(token)
        if not email:
            return None
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()
            return user
    except Exception as e:
        logger.error("websocket_auth_error", error=str(e))
        return None


async def websocket_endpoint(websocket: WebSocket, token: str = None):
    """
    WebSocket endpoint for real-time stock price updates.
    
    Usage:
    1. Connect with JWT token in query parameter: ws://host/ws?token=JWT_TOKEN
    2. Subscribe: {"action": "subscribe", "symbol": "RELIANCE", "market": "india_nse"}
    3. Unsubscribe: {"action": "unsubscribe", "symbol": "RELIANCE", "market": "india_nse"}
    4. Receive updates: {"type": "price_update", "symbol": "...", "current_price": ...}
    """
    # Accept connection first (required before sending/reading)
    try:
        await websocket.accept()
        logger.info("websocket_connection_accepted", client=websocket.client.host if websocket.client else "unknown")
    except Exception as e:
        logger.error("websocket_accept_failed", error=str(e))
        return
    
    try:
        # Authenticate user
        if not token:
            logger.warning("websocket_auth_failed", reason="no_token_provided")
            try:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="No token provided")
            except:
                pass
            return
        
        user = await get_current_user_ws(token)
        if not user:
            logger.warning("websocket_auth_failed", reason="invalid_token_or_user_not_found", token_preview=token[:20] + "..." if len(token) > 20 else token)
            try:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token or user not found")
            except:
                pass
            return
        
        if not user.is_active:
            logger.warning("websocket_auth_failed", reason="user_inactive", user_id=str(user.id))
            try:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User account is inactive")
            except:
                pass
            return
        
        # Connect
        await manager.connect(websocket, str(user.id))
        
        # Start price update task if not already running
        if manager.update_task is None or manager.update_task.done():
            manager.update_task = asyncio.create_task(manager.start_price_updates())
        
        try:
            while True:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                action = message.get("action")
                symbol = message.get("symbol")
                market = message.get("market", "india_nse")
                
                if action == "subscribe":
                    await manager.subscribe(websocket, symbol, market)
                    await websocket.send_json({
                        "type": "subscription_confirmed",
                        "symbol": symbol,
                        "market": market
                    })
                elif action == "unsubscribe":
                    await manager.unsubscribe(websocket, symbol, market)
                    await websocket.send_json({
                        "type": "unsubscription_confirmed",
                        "symbol": symbol,
                        "market": market
                    })
                elif action == "ping":
                    await websocket.send_json({"type": "pong"})
                else:
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    })
                    
        except WebSocketDisconnect:
            manager.disconnect(websocket, str(user.id))
            logger.info("websocket_disconnected", user_id=str(user.id))
            
    except Exception as e:
        logger.error("websocket_error", error=str(e))
        try:
            await websocket.close()
        except:
            pass

