import yfinance as yf


def get_stock_price(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d")

        if data.empty:
            return None

        price = float(data["Close"].iloc[-1])

        return {
            "symbol": symbol,
            "price": round(price, 2)
        }

    except Exception:
        return None


def analyze_portfolio(symbols: list):
    results = []

    for sym in symbols:
        stock = get_stock_price(sym)
        if stock:
            results.append(stock)

    if not results:
        return {"error": "No valid stocks"}

    total = sum(s["price"] for s in results)

    return {
        "portfolio_value": round(total, 2),
        "stocks": results
    }