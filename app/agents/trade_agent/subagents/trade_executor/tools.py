"""Trade Executor Tools"""

from typing import Dict, Optional
from app.services.zerodha_service import get_zerodha_service


def place_trade_order(
    symbol: str,
    transaction_type: str,
    quantity: int,
    order_type: str = "MARKET",
    price: Optional[float] = None,
    exchange: str = "NSE",
    product: str = "MIS",
    tag: str = "TRADE_AGENT"
) -> Dict:
    """
    Place a trade order via Zerodha.
    
    Args:
        symbol: Stock symbol
        transaction_type: 'BUY' or 'SELL'
        quantity: Number of shares
        order_type: 'MARKET', 'LIMIT', 'SL', 'SL-M'
        price: Limit price (required for LIMIT orders)
        exchange: Exchange
        product: 'MIS' (intraday), 'CNC' (delivery)
        tag: Order tag for identification
        
    Returns:
        Dict with order_id and status
    """
    try:
        zerodha = get_zerodha_service()
        
        order_id = zerodha.place_order(
            tradingsymbol=symbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            order_type=order_type,
            product=product,
            price=price,
            tag=tag
        )
        
        return {
            "order_id": order_id,
            "symbol": symbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "order_type": order_type,
            "status": "PLACED",
            "message": f"Order placed successfully. Order ID: {order_id}"
        }
    except Exception as e:
        return {"error": str(e), "status": "FAILED"}


def place_stop_loss_order(
    symbol: str,
    transaction_type: str,
    quantity: int,
    trigger_price: float,
    price: Optional[float] = None,
    exchange: str = "NSE",
    product: str = "MIS",
    tag: str = "TRADE_AGENT_SL"
) -> Dict:
    """
    Place a stop-loss order.
    
    Args:
        symbol: Stock symbol
        transaction_type: 'BUY' or 'SELL' (opposite of entry)
        quantity: Number of shares
        trigger_price: Price at which SL triggers
        price: Limit price after trigger (None for market)
        exchange: Exchange
        product: Product type
        tag: Order tag
        
    Returns:
        Dict with order_id and status
    """
    try:
        zerodha = get_zerodha_service()
        
        order_id = zerodha.place_sl_order(
            tradingsymbol=symbol,
            exchange=exchange,
            transaction_type=transaction_type,
            quantity=quantity,
            trigger_price=trigger_price,
            price=price,
            product=product,
            tag=tag
        )
        
        return {
            "order_id": order_id,
            "symbol": symbol,
            "transaction_type": transaction_type,
            "quantity": quantity,
            "trigger_price": trigger_price,
            "status": "PLACED",
            "message": f"Stop-loss order placed. Order ID: {order_id}"
        }
    except Exception as e:
        return {"error": str(e), "status": "FAILED"}


def get_order_status(order_id: str) -> Dict:
    """
    Get status of an order.
    
    Args:
        order_id: Order ID to check
        
    Returns:
        Dict with order status and details
    """
    try:
        zerodha = get_zerodha_service()
        history = zerodha.get_order_history(order_id)
        
        if not history:
            return {"error": "Order not found"}
        
        latest = history[-1]
        return {
            "order_id": order_id,
            "status": latest.get("status"),
            "filled_quantity": latest.get("filled_quantity"),
            "pending_quantity": latest.get("pending_quantity"),
            "average_price": latest.get("average_price"),
            "tradingsymbol": latest.get("tradingsymbol"),
            "transaction_type": latest.get("transaction_type"),
            "status_message": latest.get("status_message"),
        }
    except Exception as e:
        return {"error": str(e)}
