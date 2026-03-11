FINANCIAL_KEYWORDS = [
    "revenue",
    "net income",
    "balance sheet",
    "cash flow",
    "operating income",
    "earnings",
    "financial statements",
    "total assets",
    "liabilities",
    "shareholder"
]

def detect_financial_document(text: str) -> bool:
    text_lower = text.lower()
    score = sum(1 for k in FINANCIAL_KEYWORDS if k in text_lower)
    return score >= 3