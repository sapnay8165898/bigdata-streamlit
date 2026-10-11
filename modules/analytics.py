from modules.ingest import run_query

def kpis(table):
    return run_query(f"""
        SELECT
            COUNT(*)               AS total_rows,
            COUNT(DISTINCT customer_id) AS customers,
            COUNT(DISTINCT product_id)  AS products,
            SUM(total)             AS revenue,
            AVG(total)             AS avg_order,
            MAX(total)             AS max_order
        FROM {table}
    """)

def revenue_by_region(table):
    return run_query(f"""
        SELECT region,
               COUNT(*)          AS orders,
               SUM(total)        AS revenue,
               AVG(total)        AS avg_order
        FROM {table}
        WHERE region IS NOT NULL
        GROUP BY region
        ORDER BY revenue DESC
    """)

def revenue_by_category(table):
    return run_query(f"""
        SELECT category,
               COUNT(*)     AS orders,
               SUM(total)   AS revenue
        FROM {table}
        GROUP BY category
        ORDER BY revenue DESC
    """)

def monthly_trend(table):
    return run_query(f"""
        SELECT DATE_TRUNC('month', timestamp) AS month,
               COUNT(*)  AS orders,
               SUM(total) AS revenue
        FROM {table}
        GROUP BY month
        ORDER BY month
    """)

def top_products(table, limit=10):
    return run_query(f"""
        SELECT product_id,
               SUM(quantity) AS units_sold,
               SUM(total)    AS revenue
        FROM {table}
        GROUP BY product_id
        ORDER BY revenue DESC
        LIMIT {limit}
    """)

def channel_breakdown(table):
    return run_query(f"""
        SELECT channel,
               COUNT(*)   AS orders,
               SUM(total) AS revenue
        FROM {table}
        GROUP BY channel
        ORDER BY revenue DESC
    """)

def hourly_heatmap(table):
    return run_query(f"""
        SELECT EXTRACT(hour FROM timestamp)   AS hour,
               EXTRACT(dow  FROM timestamp)   AS dow,
               COUNT(*)                        AS orders
        FROM {table}
        GROUP BY hour, dow
        ORDER BY dow, hour
    """)

def top_customers(table, limit=10):
    return run_query(f"""
        SELECT customer_id,
               COUNT(*)   AS orders,
               SUM(total) AS lifetime_value
        FROM {table}
        GROUP BY customer_id
        ORDER BY lifetime_value DESC
        LIMIT {limit}
    """)