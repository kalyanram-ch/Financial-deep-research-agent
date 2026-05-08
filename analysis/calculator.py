def compute_financial_summary(data: dict) -> dict:
    """
    Programmatic financial calculations — never rely on LLM for math.
    Takes raw financial data dict, returns computed metrics.
    """
    summary = {}

    try:
        # Revenue growth rate
        if data.get("revenue") and data.get("prev_revenue"):
            growth = ((data["revenue"] - data["prev_revenue"]) 
                      / data["prev_revenue"]) * 100
            summary["revenue_growth_pct"] = round(growth, 2)

        # Profit margin
        if data.get("net_income") and data.get("revenue"):
            margin = (data["net_income"] / data["revenue"]) * 100
            summary["profit_margin_pct"] = round(margin, 2)

        # Price change percentage
        if data.get("current_price") and data.get("prev_price"):
            change = ((data["current_price"] - data["prev_price"]) 
                      / data["prev_price"]) * 100
            summary["price_change_pct"] = round(change, 2)

        # Debt to equity ratio
        if data.get("total_debt") and data.get("total_equity"):
            de_ratio = data["total_debt"] / data["total_equity"]
            summary["debt_to_equity"] = round(de_ratio, 2)

        # Return on equity
        if data.get("net_income") and data.get("total_equity"):
            roe = (data["net_income"] / data["total_equity"]) * 100
            summary["roe_pct"] = round(roe, 2)

        # Price to earnings
        if data.get("current_price") and data.get("eps"):
            pe = data["current_price"] / data["eps"]
            summary["pe_ratio"] = round(pe, 2)

    except ZeroDivisionError:
        summary["error"] = "Division by zero in calculation"
    except Exception as e:
        summary["error"] = str(e)

    return summary


def format_large_number(value: float) -> str:
    """Convert raw numbers to readable format: 1500000000 → 1.50B"""
    if value is None:
        return "N/A"
    if abs(value) >= 1_000_000_000:
        return f"{value / 1_000_000_000:.2f}B"
    elif abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    elif abs(value) >= 1_000:
        return f"{value / 1_000:.2f}K"
    return str(round(value, 2))


def compare_companies(companies_data: list[dict]) -> list[dict]:
    """
    Takes list of company financial dicts.
    Returns ranked list with computed comparison metrics.
    """
    results = []
    for company in companies_data:
        metrics = compute_financial_summary(company)
        metrics["name"] = company.get("name", "Unknown")
        metrics["ticker"] = company.get("ticker", "")
        metrics["market_cap_fmt"] = format_large_number(company.get("market_cap"))
        metrics["revenue_fmt"] = format_large_number(company.get("revenue"))
        results.append(metrics)

    # Sort by revenue growth if available
    results.sort(
        key=lambda x: x.get("revenue_growth_pct", 0),
        reverse=True
    )
    return results