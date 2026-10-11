import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random

def generate_ecommerce(n_rows=100_000, seed=42):
    """Generate synthetic e-commerce transaction data."""
    rng = np.random.default_rng(seed)
    random.seed(seed)

    regions = ['North', 'South', 'East', 'West', 'Central']
    categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Beauty']
    channels = ['Web', 'Mobile', 'Store', 'Partner']
    payment = ['Card', 'UPI', 'Wallet', 'COD']

    # Time range: 1 year
    end = datetime.now()
    start = end - timedelta(days=365)
    timestamps = [
        start + timedelta(seconds=int(s))
        for s in rng.integers(0, 365 * 24 * 3600, size=n_rows)
    ]

    df = pd.DataFrame({
        'order_id':    np.arange(1, n_rows + 1),
        'timestamp':   timestamps,
        'customer_id': rng.integers(1, n_rows // 5 + 1, size=n_rows),
        'product_id':  rng.integers(1, 5000, size=n_rows),
        'category':    rng.choice(categories, size=n_rows),
        'region':      rng.choice(regions, size=n_rows),
        'channel':     rng.choice(channels, size=n_rows),
        'payment':     rng.choice(payment, size=n_rows),
        'quantity':    rng.integers(1, 10, size=n_rows),
        'unit_price':  np.round(rng.gamma(2.0, 25.0, size=n_rows), 2),
    })

    # Inject ~2% anomalies (huge orders — simulate fraud / errors)
    anomaly_idx = rng.choice(n_rows, size=int(n_rows * 0.02), replace=False)
    df.loc[anomaly_idx, 'quantity'] = rng.integers(100, 500, size=len(anomaly_idx))
    df.loc[anomaly_idx, 'unit_price'] = np.round(
        rng.uniform(500, 5000, size=len(anomaly_idx)), 2)

    df['total'] = df['quantity'] * df['unit_price']

    # Add some NULLs to simulate real-world dirty data
    null_idx = rng.choice(n_rows, size=int(n_rows * 0.01), replace=False)
    df.loc[null_idx, 'region'] = None

    return df


def generate_iot(n_rows=200_000, n_devices=500, seed=7):
    """Generate synthetic IoT sensor readings."""
    rng = np.random.default_rng(seed)

    end = datetime.now()
    start = end - timedelta(days=30)

    device_ids = [f"DEV-{i:04d}" for i in range(1, n_devices + 1)]

    df = pd.DataFrame({
        'device_id':  rng.choice(device_ids, size=n_rows),
        'timestamp':  [
            start + timedelta(seconds=int(s))
            for s in rng.integers(0, 30 * 24 * 3600, size=n_rows)
        ],
        'temperature': np.round(rng.normal(25, 5, size=n_rows), 2),
        'humidity':    np.round(rng.normal(60, 10, size=n_rows), 2),
        'pressure':    np.round(rng.normal(1013, 8, size=n_rows), 2),
        'battery':     np.round(rng.uniform(0, 100, size=n_rows), 2),
    })
    return df