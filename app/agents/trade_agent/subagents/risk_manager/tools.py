"""Risk Manager Tools"""

from typing import Dict
from app.services.zerodha_service import get_zerodha_service


def get_portfolio_state() -> Dict:
    """
    Get current portfolio state including positions, margins, and P&L.
    
    Returns:
        Dict with portfolio details
    """
    try:
        zerodha = get_zerodha_service()
        
        # Get margins
        margins = zerodha.get_margins()
        equity_margin = margins.get("equity", {})
        available = equity_margin.get("available", {})
        utilised = equity_margin.get("utilised", {})
        
        available_margin = available.get("live_balance", 0) + available.get("adhoc_margin", 0)
        used_margin = utilised.get("debits", 0)
        
        # Get positions
        positions = zerodha.get_positions()
        day_positions = positions.get("day", [])
        
        # Calculate P&L
        total_pnl = sum(p.get("pnl", 0) for p in day_positions)
        
        # Format positions
        formatted_positions = []
        for pos in day_positions:
            if pos.get("quantity", 0) != 0:
                formatted_positions.append({
                    "symbol": pos.get("tradingsymbol"),
                    "quantity": pos.get("quantity"),
                    "average_price": pos.get("average_price"),
                    "last_price": pos.get("last_price"),
                    "pnl": pos.get("pnl"),
                    "product": pos.get("product"),
                })
        
        return {
            "available_margin": available_margin,
            "used_margin": used_margin,
            "total_margin": available_margin + used_margin,
            "positions": formatted_positions,
            "position_count": len(formatted_positions),
            "total_unrealized_pnl": total_pnl,
        }
    except Exception as e:
        return {"error": str(e)}


def calculate_position_size(
    capital: float,
    risk_appetite: float,
    entry_price: float,
    stop_loss: float
) -> Dict:
    """
    Calculate position size based on risk parameters.
    
    Args:
        capital: Total available capital
        risk_appetite: Risk appetite (0.0 to 1.0)
        entry_price: Planned entry price
        stop_loss: Stop loss price
        
    Returns:
        Dict with position sizing details
    """
    # Calculate risk per trade based on risk_appetite
    risk_per_trade_pct = 0.5 + (risk_appetite * 1.5)  # 0.5% to 2%
    risk_amount = capital * (risk_per_trade_pct / 100)
    
    # Calculate SL distance
    sl_distance = abs(entry_price - stop_loss)
    
    if sl_distance == 0:
        return {"error": "Stop loss cannot be equal to entry price"}
    
    # Calculate position size
    position_size = int(risk_amount / sl_distance)
    position_value = position_size * entry_price
    
    # Max per instrument check
    max_per_instrument_pct = 10 + (risk_appetite * 15)  # 10% to 25%
    max_position_value = capital * (max_per_instrument_pct / 100)
    
    if position_value > max_position_value:
        position_size = int(max_position_value / entry_price)
        position_value = position_size * entry_price
    
    # Confidence threshold
    min_confidence = 0.8 - (risk_appetite * 0.2)  # 0.8 to 0.6
    
    return {
        "position_size": position_size,
        "position_value": position_value,
        "risk_amount": risk_amount,
        "risk_per_trade_pct": risk_per_trade_pct,
        "sl_distance": sl_distance,
        "capital_used_pct": (position_value / capital) * 100,
        "max_per_instrument_pct": max_per_instrument_pct,
        "min_confidence_threshold": min_confidence,
    }
