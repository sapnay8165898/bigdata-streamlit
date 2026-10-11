import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

def customer_segmentation(df: pd.DataFrame, n_clusters=4):
    """RFM-style clustering on customers."""
    agg = df.groupby('customer_id').agg(
        orders=('order_id', 'count'),
        revenue=('total', 'sum'),
        avg_order=('total', 'mean'),
    ).reset_index()

    X = agg[['orders', 'revenue', 'avg_order']].fillna(0)
    X_scaled = StandardScaler().fit_transform(X)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    agg['segment'] = km.fit_predict(X_scaled)

    # Label segments by revenue
    order = agg.groupby('segment')['revenue'].mean().sort_values().index.tolist()
    labels = ['Low-value', 'Mid-value', 'High-value', 'VIP'][:n_clusters]
    agg['segment_label'] = agg['segment'].map(
        {seg: labels[i] for i, seg in enumerate(order)})

    return agg, km

def detect_anomalies(df: pd.DataFrame, contamination=0.02):
    """Isolation Forest on transaction features."""
    X = df[['quantity', 'unit_price', 'total']].fillna(0)
    iso = IsolationForest(contamination=contamination, random_state=42)
    df = df.copy()
    df['anomaly'] = iso.fit_predict(X)  # -1 = anomaly, 1 = normal
    df['anomaly_score'] = iso.decision_function(X)
    return df, iso

def forecast_revenue(monthly_df: pd.DataFrame, periods=6):
    """Simple linear trend forecast on monthly revenue."""
    monthly_df = monthly_df.copy()
    monthly_df['month_num'] = range(len(monthly_df))
    X = monthly_df[['month_num']].values
    y = monthly_df['revenue'].values

    model = LinearRegression().fit(X, y)
    future_x = np.arange(len(monthly_df), len(monthly_df) + periods).reshape(-1, 1)
    future_y = model.predict(future_x)

    last_month = pd.to_datetime(monthly_df['month'].iloc[-1])
    future_months = pd.date_range(last_month + pd.offsets.MonthBegin(),
                                  periods=periods, freq='MS')

    forecast = pd.DataFrame({'month': future_months, 'revenue': future_y})
    return forecast, model