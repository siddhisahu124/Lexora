import re

def extract_financial_metrics(text: str):
    revenue = re.findall(r"revenue[^0-9]*([\$€£]?\d[\d,\.]+)", text, re.I)
    profit = re.findall(r"net income[^0-9]*([\$€£]?\d[\d,\.]+)", text, re.I)

    return {
        "revenue_mentions": revenue[:5],
        "profit_mentions": profit[:5]
    }