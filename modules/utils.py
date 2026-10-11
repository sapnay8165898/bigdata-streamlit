import os

def ensure_dirs():
    for d in ['data', 'models']:
        os.makedirs(d, exist_ok=True)

def human(n):
    for unit in ['', 'K', 'M', 'B', 'T']:
        if abs(n) < 1000:
            return f"{n:.1f}{unit}"
        n /= 1000
    return f"{n:.1f}P"

def rows_label(n):
    if n < 1_000: return f"{n} rows"
    if n < 1_000_000: return f"{n/1000:.1f}K rows"
    if n < 1_000_000_000: return f"{n/1_000_000:.1f}M rows"
    return f"{n/1_000_000_000:.1f}B rows"