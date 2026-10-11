import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os

from modules.generator import generate_ecommerce, generate_iot
from modules.ingest import (
    load_dataframe, list_tables, table_info,
    run_query, drop_table, load_csv,
)
from modules.analytics import (
    kpis, revenue_by_region, revenue_by_category,
    monthly_trend, top_products, channel_breakdown,
    hourly_heatmap, top_customers,
)
from modules.ml_models import (
    customer_segmentation, detect_anomalies, forecast_revenue,
)
from modules.utils import ensure_dirs, human, rows_label

# ------------------------------------------------------------------
st.set_page_config(
    page_title="Big Data Analytics System",
    page_icon="📊",
    layout="wide",
)
ensure_dirs()

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------
with st.sidebar:
    st.title("📊 Big Data Analytics")

    page = st.radio(
        "Navigation",
        ["🏠 Home", "📥 Data Ingestion", "📈 Analytics",
         "🤖 ML Insights", "🔍 SQL Explorer"],
    )

    st.divider()
    st.subheader("📦 Data Store")
    tables = list_tables()
    if tables:
        for t in tables:
            try:
                cnt, _ = table_info(t)
                st.caption(f"• `{t}` — {rows_label(cnt)}")
            except Exception:
                st.caption(f"• `{t}`")
    else:
        st.caption("No tables yet")

    if tables and st.button("🗑️ Drop all tables", use_container_width=True):
        for t in tables:
            drop_table(t)
        st.success("All tables dropped")
        st.rerun()

# ------------------------------------------------------------------
# HOME
# ------------------------------------------------------------------
if page == "🏠 Home":
    st.title("📊 Big Data Analytics System")
    st.markdown("""
    A **Streamlit-based big data analytics platform** built on **DuckDB** — a real
    in-process OLAP engine that handles **millions of rows** on a single machine.

    ### 🚀 Capabilities
    - **Ingestion** — Load CSVs, JSONs, or generate synthetic big data (100K–5M rows)
    - **Analytics** — SQL-based aggregations, KPIs, time-series, heatmaps
    - **ML** — Customer segmentation, anomaly detection, revenue forecasting
    - **Visualization** — Fully interactive Plotly charts
    - **SQL Explorer** — Run ad-hoc DuckDB queries directly

    ### 🧭 Get Started
    1. Go to **📥 Data Ingestion** in the sidebar
    2. Click **Generate E-commerce Data** (or upload your own CSV)
    3. Click **Load to DuckDB**
    4. Explore the **📈 Analytics** and **🤖 ML Insights** tabs
    """)

    if tables:
        st.divider()
        st.subheader("Current Data Store")
        for t in tables:
            cnt, cols = table_info(t)
            with st.expander(f"📋 {t} — {rows_label(cnt)}"):
                st.dataframe(cols, use_container_width=True)

# ------------------------------------------------------------------
# INGESTION
# ------------------------------------------------------------------
elif page == "📥 Data Ingestion":
    st.title("📥 Data Ingestion")
    st.markdown("Generate synthetic data or upload your own file.")

    tab1, tab2 = st.tabs(["🧪 Generate Synthetic Data", "📂 Upload File"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("E-commerce")
            n_rows = st.slider("Rows", 10_000, 2_000_000, 200_000, 10_000)
            if st.button("Generate E-commerce Data", use_container_width=True):
                with st.spinner(f"Generating {n_rows:,} rows..."):
                    df = generate_ecommerce(n_rows)
                    st.session_state['gen_df'] = df
                    st.session_state['gen_name'] = 'ecommerce'
                st.success(f"Generated {n_rows:,} rows")

        with c2:
            st.subheader("IoT Sensors")
            n_iot = st.slider("IoT rows", 10_000, 1_000_000, 100_000, 10_000)
            if st.button("Generate IoT Data", use_container_width=True):
                with st.spinner(f"Generating {n_iot:,} rows..."):
                    df = generate_iot(n_iot)
                    st.session_state['gen_df'] = df
                    st.session_state['gen_name'] = 'iot'
                st.success(f"Generated {n_iot:,} rows")

        if 'gen_df' in st.session_state:
            df = st.session_state['gen_df']
            name = st.session_state['gen_name']
            st.divider()
            st.subheader("Preview")
            st.dataframe(df.head(50), use_container_width=True)

            tbl_name = st.text_input("Table name in DuckDB", value=name)
            if st.button(f"⬆️ Load into DuckDB as `{tbl_name}`",
                         use_container_width=True, type="primary"):
                with st.spinner("Loading..."):
                    load_dataframe(df, tbl_name)
                st.success(f"Loaded {len(df):,} rows into `{tbl_name}`")

    with tab2:
        st.subheader("Upload CSV")
        up = st.file_uploader("Choose a CSV file", type=['csv'])
        if up:
            df = pd.read_csv(up)
            st.dataframe(df.head(50), use_container_width=True)
            tbl_name = st.text_input("Table name", value="uploaded")
            if st.button("⬆️ Load uploaded CSV", type="primary"):
                load_dataframe(df, tbl_name)
                st.success(f"Loaded {len(df):,} rows into `{tbl_name}`")

# ------------------------------------------------------------------
# ANALYTICS
# ------------------------------------------------------------------
elif page == "📈 Analytics":
    st.title("📈 Analytics Dashboard")

    tables = list_tables()
    if not tables:
        st.warning("No tables found. Go to **📥 Data Ingestion** first.")
        st.stop()

    table = st.selectbox("Select table", tables)
    cnt, _ = table_info(table)

    st.caption(f"Analyzing `{table}` — {rows_label(cnt)}")

    # KPI row
    try:
        k = kpis(table).iloc[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows", f"{k['total_rows']:,}")
        c2.metric("Customers", f"{int(k['customers']):,}")
        c3.metric("Revenue", f"${k['revenue']:,.0f}")
        c4.metric("Avg Order", f"${k['avg_order']:.2f}")
    except Exception as e:
        st.info(f"KPIs need an e-commerce table: {e}")

    st.divider()

    try:
        # Revenue by region & category
        c1, c2 = st.columns(2)
        with c1:
            df = revenue_by_region(table)
            fig = px.bar(df, x='region', y='revenue',
                         title="Revenue by Region", color='region')
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df = revenue_by_category(table)
            fig = px.pie(df, names='category', values='revenue',
                         title="Revenue by Category", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)

        # Monthly trend
        df = monthly_trend(table)
        fig = px.line(df, x='month', y='revenue',
                      title="Monthly Revenue Trend", markers=True)
        st.plotly_chart(fig, use_container_width=True)

        # Top products & channels
        c1, c2 = st.columns(2)
        with c1:
            df = top_products(table, 10)
            fig = px.bar(df, x='revenue', y='product_id',
                         orientation='h', title="Top 10 Products by Revenue")
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            df = channel_breakdown(table)
            fig = px.pie(df, names='channel', values='orders',
                         title="Orders by Channel")
            st.plotly_chart(fig, use_container_width=True)

        # Hourly heatmap
        df = hourly_heatmap(table)
        pivot = df.pivot_table(index='dow', columns='hour',
                               values='orders', fill_value=0)
        fig = px.imshow(pivot, aspect='auto',
                        title="Orders by Day-of-Week × Hour",
                        color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)

        # Top customers
        df = top_customers(table)
        st.subheader("🏆 Top 10 Customers")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Some charts need e-commerce columns: {e}")

# ------------------------------------------------------------------
# ML INSIGHTS
# ------------------------------------------------------------------
elif page == "🤖 ML Insights":
    st.title("🤖 Machine Learning Insights")

    tables = list_tables()
    if not tables:
        st.warning("No data loaded yet.")
        st.stop()

    table = st.selectbox("Table", tables)
    cnt, _ = table_info(table)

    tab1, tab2, tab3 = st.tabs(
        ["👥 Customer Segmentation", "🚨 Anomaly Detection", "📈 Forecast"])

    with tab1:
        st.subheader("K-Means Customer Segmentation")
        k = st.slider("Number of clusters", 2, 8, 4)
        if st.button("Run Segmentation", type="primary"):
            with st.spinner(f"Clustering {cnt:,} rows..."):
                df = run_query(f"SELECT * FROM {table}")
                seg, model = customer_segmentation(df, n_clusters=k)
                st.session_state['seg'] = seg

        if 'seg' in st.session_state:
            seg = st.session_state['seg']
            c1, c2 = st.columns(2)
            with c1:
                fig = px.scatter(
                    seg, x='orders', y='revenue',
                    color='segment_label', size='avg_order',
                    title="Customer Segments", hover_data=['customer_id'])
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                counts = seg['segment_label'].value_counts().reset_index()
                counts.columns = ['Segment', 'Count']
                fig = px.bar(counts, x='Segment', y='Count',
                             title="Segment Distribution", color='Segment')
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Isolation Forest — Anomaly Detection")
        contam = st.slider("Expected anomaly rate", 0.005, 0.10, 0.02, 0.005)
        if st.button("Detect Anomalies", type="primary"):
            with st.spinner("Training Isolation Forest..."):
                df = run_query(f"SELECT * FROM {table}")
                res, model = detect_anomalies(df, contamination=contam)
                st.session_state['anom'] = res

        if 'anom' in st.session_state:
            res = st.session_state['anom']
            anomalies = res[res['anomaly'] == -1]
            st.metric("Anomalies Detected", f"{len(anomalies):,}",
                      delta=f"{len(anomalies)/len(res)*100:.2f}% of rows")

            fig = px.scatter(
                res.sample(min(5000, len(res))),
                x='quantity', y='total',
                color=res.sample(min(5000, len(res)))['anomaly'].map(
                    {1: 'Normal', -1: 'Anomaly'}),
                title="Anomalies (red)", opacity=0.6)
            st.plotly_chart(fig, use_container_width=True)

            st.subheader("Top Anomalies")
            st.dataframe(anomalies.nsmallest(50, 'anomaly_score'),
                         use_container_width=True)

    with tab3:
        st.subheader("Revenue Forecast (Linear Trend)")
        periods = st.slider("Forecast horizon (months)", 3, 24, 6)
        if st.button("Generate Forecast", type="primary"):
            with st.spinner("Fitting model..."):
                hist = monthly_trend(table)
                fc, model = forecast_revenue(hist, periods=periods)
                st.session_state['fc'] = (hist, fc)

        if 'fc' in st.session_state:
            hist, fc = st.session_state['fc']
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=hist['month'], y=hist['revenue'],
                                     mode='lines+markers', name='Historical'))
            fig.add_trace(go.Scatter(x=fc['month'], y=fc['revenue'],
                                     mode='lines+markers', name='Forecast',
                                     line=dict(dash='dash', color='orange')))
            fig.update_layout(title="Revenue Forecast", xaxis_title="Month",
                              yaxis_title="Revenue")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(fc, use_container_width=True)

# ------------------------------------------------------------------
# SQL EXPLORER
# ------------------------------------------------------------------
elif page == "🔍 SQL Explorer":
    st.title("🔍 SQL Explorer")
    st.markdown("Run **DuckDB SQL** queries directly on your tables.")

    tables = list_tables()
    if not tables:
        st.warning("No tables found. Load data first.")
        st.stop()

    st.caption(f"Available tables: `{'`, `'.join(tables)}`")

    default_sql = f"SELECT * FROM {tables[0]} LIMIT 100"
    sql = st.text_area("SQL Query", value=default_sql, height=150)

    if st.button("▶️ Run Query", type="primary"):
        try:
            with st.spinner("Executing..."):
                df = run_query(sql)
            st.success(f"Returned {len(df):,} rows")
            st.dataframe(df, use_container_width=True, height=400)

            st.download_button(
                "⬇️ Download CSV",
                df.to_csv(index=False).encode(),
                file_name=f"query_{datetime.now():%Y%m%d_%H%M%S}.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Query error: {e}")