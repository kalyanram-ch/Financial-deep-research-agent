import yfinance as yf
import pandas as pd

def get_stock_data(ticker: str) -> dict:
    """Get key financial metrics — never rely on LLM for numbers."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        hist = stock.history(period="1y")
        
        return {
            "ticker": ticker,
            "current_price": info.get("currentPrice"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "revenue": info.get("totalRevenue"),
            "revenue_growth": info.get("revenueGrowth"),
            "profit_margin": info.get("profitMargins"),
            "debt_to_equity": info.get("debtToEquity"),
            "roe": info.get("returnOnEquity"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "price_1y_ago": float(hist["Close"].iloc[0]) if not hist.empty else None,
            "price_change_1y_pct": round(
                ((info.get("currentPrice", 0) - float(hist["Close"].iloc[0])) 
                 / float(hist["Close"].iloc[0]) * 100), 2
            ) if not hist.empty else None
        }
    except Exception as e:
        return {"error": str(e), "ticker": ticker}

def get_sector_overview(tickers: list[str]) -> pd.DataFrame:
    """Comparative data across multiple companies."""
    rows = []
    for t in tickers:
        data = get_stock_data(t)
        if "error" not in data:
            rows.append(data)
    return pd.DataFrame(rows)