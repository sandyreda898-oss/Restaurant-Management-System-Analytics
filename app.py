import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import pyodbc

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Restaurant Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Coffee / Beige Palette ────────────────────────────────────────────────────
BG      = "#F5EDD6"
PANEL   = "#EDE0C4"
CREAM   = "#F0D9B5"
DARK    = "#2C1810"
MED     = "#7B4A2D"
CARAMEL = "#C17F3E"
LATTE   = "#D4A96A"
RED     = "#8B3A2A"
GREEN   = "#4A6741"
NAVY    = "#2E4060"
SUBTEXT = "#7B4A2D"
COLORS  = [CARAMEL, MED, RED, GREEN, NAVY, LATTE, "#A0522D", "#556B2F"]

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
    .stApp, [data-testid="stAppViewContainer"] {{ background-color: {BG}; }}
    [data-testid="stHeader"]  {{ background-color: {BG}; }}
    [data-testid="stSidebar"] {{ background-color: {PANEL}; }}
    .block-container {{ padding-top: 1.5rem; padding-bottom: 2rem; }}
    [data-testid="metric-container"] {{
        background-color: {CREAM};
        border: 1.5px solid {CARAMEL};
        border-radius: 12px;
        padding: 16px 20px;
    }}
    [data-testid="metric-container"] label {{ color:{SUBTEXT}!important; font-size:13px!important; font-weight:600!important; }}
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{ color:{DARK}!important; font-size:28px!important; font-weight:700!important; }}
    [data-testid="stMetricDelta"] {{ color:{GREEN}!important; }}
    h1 {{ color:{DARK}!important; font-family:Georgia,serif!important; }}
    h2,h3 {{ color:{MED}!important; font-family:Georgia,serif!important; }}
    hr {{ border-color:{CARAMEL}; opacity:0.3; }}
    .stTabs [data-baseweb="tab-list"] {{ background-color:{PANEL}; border-radius:10px; padding:4px; }}
    .stTabs [data-baseweb="tab"]      {{ color:{MED}; font-weight:600; }}
    .stTabs [aria-selected="true"]    {{ background-color:{CARAMEL}!important; color:white!important; border-radius:8px; }}
</style>
""", unsafe_allow_html=True)

LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor=PANEL,
    font=dict(family="Georgia, serif", color=DARK, size=11),
    margin=dict(t=40, b=30, l=30, r=20),
)

# helper: base axis style + any overrides merged cleanly
def xax(**kw): return dict(gridcolor=BG, zerolinecolor=BG, tickfont=dict(color=MED), **kw)
def yax(**kw): return dict(gridcolor=BG, zerolinecolor=BG, tickfont=dict(color=MED), **kw)

def apply_layout(fig, height=340, xaxis_kw=None, yaxis_kw=None, **extra):
    fig.update_layout(
        **LAYOUT,
        height=height,
        xaxis=xax(**(xaxis_kw or {})),
        yaxis=yax(**(yaxis_kw or {})),
        **extra
    )

# ══════════════════════════════════════════════════════════════════════════════
# ── DB Connection
# ══════════════════════════════════════════════════════════════════════════════
SERVER   = r"DESKTOP-JQL88L5\SQLEXPRESS"
DATABASE = "RestaurantManagementSystem"

@st.cache_resource(show_spinner="Connecting to SQL Server...")
def get_connection():
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={SERVER};"
        f"DATABASE={DATABASE};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)

@st.cache_data(ttl=60, show_spinner="Loading data...")
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    return pd.read_sql(sql, conn)

# Test connection
try:
    get_connection()
    connected = True
except Exception as e:
    connected = False
    conn_error = str(e)

# ══════════════════════════════════════════════════════════════════════════════
# ── Load Data
# ══════════════════════════════════════════════════════════════════════════════
if connected:

    df_kpi = run_query("""
        SELECT
            COUNT(*)                   AS TotalOrders,
            SUM(FinalAmount)           AS TotalRevenue,
            AVG(FinalAmount)           AS AvgOrderValue,
            COUNT(DISTINCT CustomerID) AS TotalCustomers
        FROM Orders
    """)

    df_status = run_query("""
        SELECT OrderStatus AS Status, COUNT(*) AS Count
        FROM Orders
        GROUP BY OrderStatus
    """)

    df_pay = run_query("""
        SELECT PaymentMethod AS Method, COUNT(*) AS Count, SUM(PaidAmount) AS Total
        FROM Payments
        GROUP BY PaymentMethod
    """)

    df_cat = run_query("""
        SELECT c.CategoryName AS Category, SUM(od.SubTotal) AS Revenue
        FROM OrderDetails od
        JOIN MenuItems  m ON od.ItemID    = m.ItemID
        JOIN Categories c ON m.CategoryID = c.CategoryID
        GROUP BY c.CategoryName
        ORDER BY Revenue DESC
    """)

    df_items = run_query("""
        SELECT TOP 8
            m.ItemName              AS Item,
            COUNT(od.OrderDetailID) AS Orders,
            SUM(od.Quantity)        AS TotalQty,
            SUM(od.SubTotal)        AS Revenue
        FROM OrderDetails od
        JOIN MenuItems m ON od.ItemID = m.ItemID
        GROUP BY m.ItemName
        ORDER BY Orders DESC
    """)
    df_items = df_items.sort_values("Orders")

    df_margin = run_query("""
        SELECT
            ItemName,
            Price     AS Sale,
            CostPrice AS Cost,
            Price - CostPrice                         AS Profit,
            ROUND((Price-CostPrice)*100.0/Price, 1)   AS Margin
        FROM MenuItems
        ORDER BY Margin DESC
    """)

    df_city = run_query("""
        SELECT City, COUNT(*) AS Count
        FROM Customers
        GROUP BY City
        ORDER BY Count DESC
    """)

    df_salary = run_query("""
        SELECT r.RoleName AS Role,
               COUNT(e.EmployeeID) AS Employees,
               SUM(e.Salary)       AS TotalSalary,
               AVG(e.Salary)       AS AvgSalary
        FROM Employees e
        JOIN Roles r ON e.RoleID = r.RoleID
        GROUP BY r.RoleName
        ORDER BY TotalSalary DESC
    """)

    df_emp = run_query("""
        SELECT e.FullName AS Name, r.RoleName AS Role, e.Phone, e.Salary
        FROM Employees e
        JOIN Roles r ON e.RoleID = r.RoleID
    """)

    df_stock = run_query("""
        SELECT
            i.IngredientName, i.QuantityAvailable, i.Unit,
            i.ReorderLevel,   s.SupplierName,
            CASE WHEN i.QuantityAvailable <= i.ReorderLevel
                 THEN 'Needs Reorder' ELSE 'In Stock' END AS Status,
            ROUND(i.QuantityAvailable * 100.0 / i.ReorderLevel, 0) AS Pct
        FROM Inventory i
        JOIN Suppliers s ON i.SupplierID = s.SupplierID
        ORDER BY Pct ASC
    """)

    df_reviews = run_query("""
        SELECT
            r.Rating,
            COUNT(r.ReviewID)  AS ReviewCount,
            AVG(o.FinalAmount) AS AvgOrderValue
        FROM Reviews r
        JOIN Orders o ON r.OrderID = o.OrderID
        GROUP BY r.Rating
        ORDER BY r.Rating
    """)

    df_delivery = run_query("""
        SELECT
            e.FullName                          AS Driver,
            COUNT(d.DeliveryID)                 AS TotalDeliveries,
            AVG(CAST(d.CustomerRating AS FLOAT)) AS AvgRating
        FROM Deliveries d
        JOIN Employees e ON d.DeliveryEmployeeID = e.EmployeeID
        GROUP BY e.FullName
    """)

    df_revenue = run_query("""
        SELECT
            SUM(TotalAmount) AS SubTotal,
            SUM(Tax)         AS TotalTax,
            SUM(DeliveryFee) AS DeliveryFees,
            SUM(Discount)    AS Discounts,
            SUM(FinalAmount) AS NetRevenue
        FROM Orders
    """)

    df_coupons = run_query("""
        SELECT Code, DiscountType, DiscountValue,
               MaxUsage, Status,
               CAST(StartDate AS DATE) AS StartDate,
               CAST(EndDate   AS DATE) AS EndDate
        FROM Coupons
    """)

# ══════════════════════════════════════════════════════════════════════════════
# ── UI
# ══════════════════════════════════════════════════════════════════════════════

if not connected:
    st.error(f"Cannot connect to SQL Server: `{conn_error}`", icon="❌")
    st.info("Make sure:\n- SQL Server is running\n- ODBC Driver 17 is installed\n- Windows Authentication is enabled")
    st.stop()

# Header
st.markdown(f"""
<div style="text-align:center; padding:10px 0 4px 0;">
    <h1 style="font-size:2.2rem; color:{DARK}; margin-bottom:2px;">
        Restaurant Management System
    </h1>

</div>
""", unsafe_allow_html=True)
st.markdown("---")

# KPIs
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Orders",    f"{int(df_kpi['TotalOrders'][0]):,}")
k2.metric("Total Revenue",   f"{float(df_kpi['TotalRevenue'][0]):,.0f} EGP")
k3.metric("Avg Order Value", f"{float(df_kpi['AvgOrderValue'][0]):,.0f} EGP")
k4.metric("Total Customers", f"{int(df_kpi['TotalCustomers'][0]):,}")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Orders & Payments",
    "Menu & Revenue",
    "Customers & Staff",
    "Inventory",
    "Reviews & Delivery"
])

# ── TAB 1: Orders & Payments ─────────────────────────────────────────────────
with tab1:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Order Status Distribution")
        fig = go.Figure(go.Pie(
            labels=df_status["Status"], values=df_status["Count"],
            hole=0.55,
            marker=dict(colors=COLORS, line=dict(color=BG, width=3)),
            textinfo="label+percent"
        ))
        apply_layout(fig, height=320)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Payment Methods")
        fig2 = go.Figure(go.Pie(
            labels=df_pay["Method"], values=df_pay["Count"],
            hole=0.55,
            marker=dict(colors=[CARAMEL, MED, LATTE], line=dict(color=BG, width=3)),
            textinfo="label+percent"
        ))
        apply_layout(fig2, height=320)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Revenue Breakdown (EGP)")
    rev = df_revenue.iloc[0]
    fig3 = go.Figure(go.Bar(
        x=["Sub-Total","Tax 14%","Delivery Fees","Discounts","Net Revenue"],
        y=[rev.SubTotal, rev.TotalTax, rev.DeliveryFees, rev.Discounts, rev.NetRevenue],
        marker_color=[MED, RED, NAVY, CARAMEL, GREEN],
        marker_line_width=0,
        text=[f"{v:,.0f}" for v in [rev.SubTotal, rev.TotalTax,
              rev.DeliveryFees, rev.Discounts, rev.NetRevenue]],
        textposition="outside",
    ))
    apply_layout(fig3, height=360, yaxis_kw=dict(tickformat=","))
    st.plotly_chart(fig3, use_container_width=True)

# ── TAB 2: Menu & Revenue ────────────────────────────────────────────────────
with tab2:
    st.subheader("Top 8 Menu Items — Orders Count")
    fig4 = go.Figure(go.Bar(
        x=df_items["Orders"], y=df_items["Item"],
        orientation="h",
        marker=dict(color=df_items["Orders"],
                    colorscale=[[0,MED],[0.5,CARAMEL],[1,CREAM]]),
        text=df_items["Orders"], textposition="outside",
    ))
    apply_layout(fig4, height=360)
    st.plotly_chart(fig4, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Revenue by Category")
        fig5 = go.Figure(go.Bar(
            x=df_cat["Category"], y=df_cat["Revenue"],
            marker_color=COLORS[:len(df_cat)], marker_line_width=0,
            text=[f"{v:,.0f}" for v in df_cat["Revenue"]],
            textposition="outside",
        ))
        apply_layout(fig5, height=340, yaxis_kw=dict(tickformat=","))
        st.plotly_chart(fig5, use_container_width=True)

    with c4:
        st.subheader("Profit Margin % per Item")
        m_colors = [GREEN if m >= 55 else CARAMEL if m >= 48 else RED
                    for m in df_margin["Margin"]]
        fig6 = go.Figure(go.Bar(
            x=df_margin["ItemName"], y=df_margin["Margin"],
            marker_color=m_colors, marker_line_width=0,
            text=[f"{m}%" for m in df_margin["Margin"]],
            textposition="outside",
        ))
        apply_layout(fig6, height=340,
                     xaxis_kw=dict(tickangle=35),
                     yaxis_kw=dict(range=[0,82]))
        st.plotly_chart(fig6, use_container_width=True)

    st.subheader("Sale Price vs Cost Price")
    fig7 = go.Figure()
    fig7.add_trace(go.Bar(name="Sale Price", x=df_margin["ItemName"],
                          y=df_margin["Sale"], marker_color=CARAMEL))
    fig7.add_trace(go.Bar(name="Cost Price", x=df_margin["ItemName"],
                          y=df_margin["Cost"], marker_color=RED))
    apply_layout(fig7, height=340,
                 barmode="group",
                 legend=dict(bgcolor=CREAM, bordercolor=CARAMEL,
                             borderwidth=1, font=dict(color=DARK)))
    st.plotly_chart(fig7, use_container_width=True)

# ── TAB 3: Customers & Staff ─────────────────────────────────────────────────
with tab3:
    c5, c6 = st.columns(2)

    with c5:
        st.subheader("Customers by City")
        fig8 = go.Figure(go.Bar(
            x=df_city["City"], y=df_city["Count"],
            marker_color=COLORS[:len(df_city)], marker_line_width=0,
            text=df_city["Count"], textposition="outside",
        ))
        apply_layout(fig8, height=320)
        st.plotly_chart(fig8, use_container_width=True)

    with c6:
        st.subheader("Total Salary by Role (EGP)")
        fig9 = go.Figure(go.Bar(
            x=df_salary["Role"], y=df_salary["TotalSalary"],
            marker_color=COLORS[:len(df_salary)], marker_line_width=0,
            text=[f"{v:,}" for v in df_salary["TotalSalary"]],
            textposition="outside",
        ))
        apply_layout(fig9, height=320)
        st.plotly_chart(fig9, use_container_width=True)

    st.subheader("Employee Directory")
    st.dataframe(df_emp, use_container_width=True, hide_index=True)

    st.subheader("Active Coupons")
    st.dataframe(df_coupons, use_container_width=True, hide_index=True)

# ── TAB 4: Inventory ─────────────────────────────────────────────────────────
with tab4:
    st.subheader("Stock Level vs Reorder Point (%)")
    s_colors = [GREEN if p >= 500 else CARAMEL if p >= 200 else RED
                for p in df_stock["Pct"]]
    fig10 = go.Figure()
    fig10.add_trace(go.Bar(
        x=df_stock["Pct"], y=df_stock["IngredientName"],
        orientation="h",
        marker_color=s_colors, marker_line_width=0,
        text=[f"{int(p)}%" for p in df_stock["Pct"]],
        textposition="outside",
    ))
    fig10.add_vline(x=100, line_color=RED, line_dash="dash", line_width=2,
                   annotation_text="Reorder Level",
                   annotation_font_color=RED)
    apply_layout(fig10, height=380)
    st.plotly_chart(fig10, use_container_width=True)

    st.subheader("Inventory Details")
    st.dataframe(
        df_stock[["IngredientName","QuantityAvailable","Unit",
                  "ReorderLevel","Status","SupplierName"]],
        use_container_width=True, hide_index=True
    )

# ── TAB 5: Reviews & Delivery ─────────────────────────────────────────────────
with tab5:
    c7, c8 = st.columns(2)

    with c7:
        st.subheader("Review Rating Distribution")
        fig11 = go.Figure(go.Bar(
            x=df_reviews["Rating"].astype(str) + " Stars",
            y=df_reviews["ReviewCount"],
            marker_color=[RED, CARAMEL, GREEN],
            marker_line_width=0,
            text=df_reviews["ReviewCount"], textposition="outside",
        ))
        apply_layout(fig11, height=320)
        st.plotly_chart(fig11, use_container_width=True)

    with c8:
        st.subheader("Avg Order Value by Rating")
        fig12 = go.Figure(go.Scatter(
            x=df_reviews["Rating"].astype(str) + " Stars",
            y=df_reviews["AvgOrderValue"],
            mode="lines+markers+text",
            line=dict(color=CARAMEL, width=3),
            marker=dict(size=14, color=CARAMEL,
                        line=dict(color=CREAM, width=2)),
            text=[f"{v:.0f} EGP" for v in df_reviews["AvgOrderValue"]],
            textposition="top center",
        ))
        apply_layout(fig12, height=320)
        st.plotly_chart(fig12, use_container_width=True)

    st.subheader("Delivery Performance")
    cols = st.columns(len(df_delivery))
    for i, (_, row) in enumerate(df_delivery.iterrows()):
        cols[i].metric(
            f"{row['Driver']}",
            f"{int(row['TotalDeliveries'])} deliveries",
            f"Avg Rating: {row['AvgRating']:.1f}"
        )


