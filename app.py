"""
Afficionado Coffee Roasters — Sales Trend & Time-Based Performance Dashboard
Run:  streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

_FC = "#0d3b5e"
pio.templates["ob"] = pio.templates["plotly_white"]
pio.templates["ob"].layout.font        = dict(color=_FC, family="Arial, sans-serif")
pio.templates["ob"].layout.title.font  = dict(color=_FC, size=15)
pio.templates.default = "ob"

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Afficionado Coffee Roasters – Analytics",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Main background ── */
    .main { background-color: #f0f6fb; }

    /* ── Metric cards ── */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
        border-left: 4px solid #1a6fa8;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1a6fa8; }
    .metric-label { font-size: 0.85rem; color: #888; margin-top: 4px; }
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #0d3b5e;
        border-bottom: 2px solid #5ab4d6;
        padding-bottom: 6px;
        margin-top: 10px;
    }

    /* ── Sidebar shell ── */
    [data-testid="stSidebar"] {
        background-color: #0d3b5e;
    }
    [data-testid="stSidebar"] * {
        color: #d6eef8 !important;
    }

    /* ── Sidebar section label ("Filters") — fix red color ── */
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] .stSubheader,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {
        color: #5ab4d6 !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.08em !important;
        text-transform: uppercase !important;
    }

    /* ── Multiselect container background ── */
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] [data-baseweb="popover"] {
        background-color: #0a2f4e !important;
        border: 1px solid #1a6fa8 !important;
        border-radius: 8px !important;
    }

    /* ── Multiselect tags — fix red to brand blue ── */
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #1a6fa8 !important;
        border-radius: 6px !important;
        border: none !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] span,
    [data-testid="stSidebar"] [data-baseweb="tag"] [data-testid="stMarkdownContainer"] {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
    }
    /* Tag × close button */
    [data-testid="stSidebar"] [data-baseweb="tag"] [role="presentation"] svg {
        fill: #d6eef8 !important;
    }

    /* ── Slider track & thumb — fix red to brand blue ── */
    [data-testid="stSidebar"] [data-testid="stSlider"] [role="slider"] {
        background-color: #5ab4d6 !important;
        border-color: #5ab4d6 !important;
    }
    [data-testid="stSidebar"] [data-testid="stSlider"] > div > div > div > div {
        background: linear-gradient(90deg, #1a6fa8, #5ab4d6) !important;
    }

    /* ── Radio buttons — fix red dot to brand teal ── */
    [data-testid="stSidebar"] [data-testid="stRadio"] label [data-testid="stMarkdownContainer"] p {
        color: #d6eef8 !important;
    }
    [data-testid="stSidebar"] input[type="radio"]:checked + div {
        border-color: #5ab4d6 !important;
        background-color: #5ab4d6 !important;
    }

    /* ── Divider ── */
    [data-testid="stSidebar"] hr {
        border-color: rgba(90,180,214,0.25) !important;
        margin: 16px 0 !important;
    }

    /* ── Caption / footer text ── */
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #7eb8d4 !important;
        font-size: 0.75rem !important;
    }

    /* ── Main content headings ── */
    .main h1,.main h2,.main h3 { color: #0d3b5e !important; }
    [data-testid="stMarkdownContainer"] h1 { color: #0d3b5e !important; font-weight: 800; }
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3 { color: #1a6fa8 !important; font-weight: 700; }
    [data-testid="stMarkdownContainer"] p { color: #1a1a2e !important; }

    /* ── Tabs ── */
    button[data-baseweb="tab"] { color: #0d3b5e !important; font-weight: 600; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #1a6fa8 !important; }
</style>
""", unsafe_allow_html=True)

# ── Color palette ─────────────────────────────────────────────────────────────
COLORS = {
    "primary":   "#1a6fa8",
    "secondary": "#5ab4d6",
    "accent":    "#0d3b5e",
    "light":     "#d6eef8",
    "stores":    ["#1a6fa8", "#5ab4d6", "#0d3b5e"],
}
STORE_COLOR_MAP = {
    "Hell's Kitchen":  "#1a6fa8",
    "Astoria":         "#5ab4d6",
    "Lower Manhattan": "#0d3b5e",
}

# ── Load & cache data ─────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/Transactions.csv")
    df["revenue"]      = df["transaction_qty"] * df["unit_price"]
    df["hour"]         = df["transaction_time"].str.split(":").str[0].astype(int)
    df["minute"]       = df["transaction_time"].str.split(":").str[1].astype(int)
    df["hour_decimal"] = df["hour"] + df["minute"] / 60
    df = df.sort_values("transaction_id").reset_index(drop=True)
    total_days = 182
    df["day_num"] = (df["transaction_id"] / df["transaction_id"].max() * total_days).astype(int) + 1
    df["day_num"] = df["day_num"].clip(1, total_days)

    def bucket(h):
        if   6  <= h <= 11: return "Morning (6–11)"
        elif 12 <= h <= 16: return "Afternoon (12–16)"
        elif 17 <= h <= 21: return "Evening (17–21)"
        else:               return "Late/Early (22–5)"

    BUCKET_ORDER = ["Morning (6–11)", "Afternoon (12–16)", "Evening (17–21)", "Late/Early (22–5)"]
    df["time_bucket"] = pd.Categorical(df["hour"].apply(bucket), categories=BUCKET_ORDER, ordered=True)
    return df

df_full = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/A_small_cup_of_coffee.JPG/240px-A_small_cup_of_coffee.JPG",
        width=80,
    )
    st.title("☕ Afficionado")
    st.caption("Sales Analytics Dashboard")
    st.markdown("---")
    st.subheader("🔍 Filters")
    all_stores    = sorted(df_full["store_location"].unique().tolist())
    sel_stores    = st.multiselect("Store Location", all_stores, default=all_stores)
    hour_range    = st.slider("Hour Range", min_value=6, max_value=20, value=(6, 20), step=1)
    metric_toggle = st.radio("Primary Metric", ["Revenue ($)", "Transaction Count"])
    st.markdown("---")
    st.caption("Data: 149,116 transactions · 3 stores · 2025")

# ── Filter ────────────────────────────────────────────────────────────────────
df = df_full[
    df_full["store_location"].isin(sel_stores) &
    df_full["hour"].between(hour_range[0], hour_range[1])
].copy()

metric_name = "Revenue ($)" if metric_toggle == "Revenue ($)" else "Transactions"
y_col       = "revenue"     if metric_toggle == "Revenue ($)" else "transactions"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# ☕ Afficionado Coffee Roasters")
st.markdown("### Sales Trend & Time-Based Performance Analytics — 2025")
st.markdown("---")

# ── KPI Cards ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
total_rev = df["revenue"].sum()
total_txn = len(df)
avg_rev   = df["revenue"].mean()
peak_hour = df.groupby("hour")["transaction_id"].count().idxmax()
top_store = df.groupby("store_location")["revenue"].sum().idxmax()

for col, val, lbl in [
    (k1, f"${total_rev:,.0f}", "Total Revenue"),
    (k2, f"{total_txn:,}",     "Total Transactions"),
    (k3, f"${avg_rev:.2f}",    "Avg Transaction Value"),
    (k4, f"{peak_hour}:00",    "Peak Hour"),
    (k5, top_store.split()[0], "Top Store"),
]:
    with col:
        st.markdown(
            f'<div class="metric-card"><div class="metric-value">{val}</div>'
            f'<div class="metric-label">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Sales Trend", "🕐 Hourly Demand", "🗓️ Time Buckets",
    "🏪 Store Comparison", "🛍️ Product Analysis",
])

# ─── TAB 1 — Sales Trend ─────────────────────────────────────────────────────
with tab1:
    try:
        st.markdown('<p class="section-header">📈 Overall Sales Trend</p>', unsafe_allow_html=True)
        st.caption("Transaction-ID-based sequential trend (proxy for chronological order, Jan–Jun 2025)")

        daily = df.groupby("day_num").agg(
            revenue=("revenue", "sum"),
            transactions=("transaction_id", "count"),
        ).reset_index()
        daily["rev_7d_ma"] = daily["revenue"].rolling(7, min_periods=1).mean()

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=daily["day_num"], y=daily[y_col],
            mode="lines", name=metric_name,
            line=dict(color=COLORS["secondary"], width=1.5),
            opacity=0.5, fill="tozeroy", fillcolor="rgba(90,180,214,0.15)",
        ))
        if metric_toggle == "Revenue ($)":
            fig_trend.add_trace(go.Scatter(
                x=daily["day_num"], y=daily["rev_7d_ma"],
                mode="lines", name="7-Day Moving Avg",
                line=dict(color=COLORS["primary"], width=2.5),
            ))
        fig_trend.update_layout(
            font=dict(color=_FC),
            title="Daily Sales Trend (Jan–Jun 2025)",
            xaxis=dict(title="Day Number (Sequential)", tickfont=dict(color=_FC), title_font=dict(color=_FC)),
            yaxis=dict(title=metric_name, tickfont=dict(color=_FC), title_font=dict(color=_FC)),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(orientation="h", y=1.1, font=dict(color=_FC)),
            height=380,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

        c1, c2 = st.columns(2)
        with c1:
            store_daily = df.groupby(["day_num", "store_location"]).agg(
                revenue=("revenue", "sum"),
                transactions=("transaction_id", "count"),
            ).reset_index()
            fig_store_trend = px.line(
                store_daily, x="day_num", y=y_col,
                color="store_location", color_discrete_map=STORE_COLOR_MAP,
                title="Daily Trend by Store",
                labels={"day_num": "Day", y_col: metric_name, "store_location": "Store"},
            )
            fig_store_trend.update_layout(
                font=dict(color=_FC), plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                yaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                legend=dict(orientation="h", y=-0.2, font=dict(color=_FC)), height=320,
            )
            st.plotly_chart(fig_store_trend, use_container_width=True)

        with c2:
            store_share = df.groupby("store_location")["revenue"].sum().reset_index()
            fig_pie = px.pie(
                store_share, values="revenue", names="store_location",
                color="store_location", color_discrete_map=STORE_COLOR_MAP,
                title="Revenue Share by Store", hole=0.45,
            )
            fig_pie.update_traces(textposition="outside", textinfo="percent+label",
                                  textfont=dict(color=_FC))
            fig_pie.update_layout(
                font=dict(color=_FC), showlegend=False,
                paper_bgcolor="white", height=320,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    except Exception as e:
        st.error(f"**Tab 1 error:** {e}")
        st.exception(e)

# ─── TAB 2 — Hourly Demand ───────────────────────────────────────────────────
with tab2:
    try:
        st.markdown('<p class="section-header">🕐 Hourly Demand Analysis</p>', unsafe_allow_html=True)

        hourly = df.groupby("hour").agg(
            revenue=("revenue", "sum"),
            transactions=("transaction_id", "count"),
            avg_rev=("revenue", "mean"),
        ).reset_index()

        c1, c2 = st.columns([3, 2])
        with c1:
            colors_bar = [
                COLORS["primary"]   if v == hourly[y_col].max()
                else COLORS["secondary"] if v >= hourly[y_col].quantile(0.75)
                else "#b8ddf0"
                for v in hourly[y_col]
            ]
            fig_hourly = go.Figure()
            fig_hourly.add_trace(go.Bar(
                x=hourly["hour"], y=hourly[y_col],
                marker_color=colors_bar,
                text=hourly[y_col].apply(
                    lambda v: f"${v:,.0f}" if metric_toggle == "Revenue ($)" else f"{v:,}"
                ),
                textposition="outside",
                textfont=dict(color=_FC),
                name=metric_name,
            ))
            fig_hourly.add_vline(
                x=10, line_dash="dash", line_color="#c0392b",
                annotation_text="Peak Hour (10 AM)", annotation_position="top right",
                annotation_font_color=_FC,
            )
            fig_hourly.update_layout(
                font=dict(color=_FC),
                title=f"Hourly {metric_name} Distribution",
                xaxis=dict(
                    title="Hour of Day", tickmode="array",
                    tickvals=list(range(6, 21)),
                    ticktext=[f"{h}:00" for h in range(6, 21)],
                    tickfont=dict(color=_FC), title_font=dict(color=_FC),
                ),
                yaxis=dict(title=metric_name, tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                plot_bgcolor="white", paper_bgcolor="white", height=380,
            )
            st.plotly_chart(fig_hourly, use_container_width=True)

        with c2:
            st.markdown("**📊 Hourly Breakdown Table**")
            display_df = hourly.copy()
            display_df["Hour"]    = display_df["hour"].apply(lambda h: f"{h}:00")
            display_df["Revenue"] = display_df["revenue"].apply(lambda v: f"${v:,.0f}")
            display_df["Avg/Txn"] = display_df["avg_rev"].apply(lambda v: f"${v:.2f}")
            st.dataframe(
                display_df[["Hour", "Revenue", "transactions", "Avg/Txn"]].rename(
                    columns={"transactions": "Txns"}
                ),
                use_container_width=True, hide_index=True, height=360,
            )

        st.markdown('<p class="section-header">🔥 Hourly Heatmap by Store</p>', unsafe_allow_html=True)
        heat_data = df.groupby(["store_location", "hour"]).agg(
            revenue=("revenue", "sum"),
            transactions=("transaction_id", "count"),
        ).reset_index()
        heat_pivot = heat_data.pivot(
            index="store_location", columns="hour", values=y_col
        ).fillna(0)

        fig_heat = px.imshow(
            heat_pivot,
            color_continuous_scale=["#f0f6fb", "#5ab4d6", "#1a6fa8", "#0d3b5e"],
            labels=dict(x="Hour of Day", y="Store Location", color=metric_name),
            title=f"Heatmap: {metric_name} by Store × Hour",
            aspect="auto",
            text_auto=".0f" if metric_toggle != "Revenue ($)" else False,
        )
        fig_heat.update_xaxes(
            tickvals=list(range(6, 21)),
            ticktext=[f"{h}:00" for h in range(6, 21)],
            tickfont=dict(color=_FC), title_font=dict(color=_FC),
        )
        fig_heat.update_layout(
            font=dict(color=_FC), paper_bgcolor="white", plot_bgcolor="white",
            yaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
            coloraxis_colorbar=dict(title=metric_name, tickfont=dict(color=_FC),
                                    title_font=dict(color=_FC)),
            height=280,
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    except Exception as e:
        st.error(f"**Tab 2 error:** {e}")
        st.exception(e)

# ─── TAB 3 — Time Buckets ────────────────────────────────────────────────────
with tab3:
    try:
        st.markdown('<p class="section-header">🗓️ Time Bucket Performance</p>', unsafe_allow_html=True)

        bucket_agg = df.groupby("time_bucket", observed=True).agg(
            revenue=("revenue", "sum"),
            transactions=("transaction_id", "count"),
            avg_txn=("revenue", "mean"),
        ).reset_index()

        c1, c2 = st.columns(2)
        with c1:
            fig_bucket_bar = px.bar(
                bucket_agg, x="time_bucket",
                y="revenue" if metric_toggle == "Revenue ($)" else "transactions",
                color="time_bucket",
                color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], "#0d3b5e", "#7ecae0"],
                title=f"{metric_name} by Time of Day",
                labels={"time_bucket": "Time Period", "revenue": "Revenue ($)", "transactions": "Transactions"},
                text_auto=True,
            )
            fig_bucket_bar.update_traces(texttemplate="%{y:,.0f}", textposition="outside",
                                         textfont=dict(color=_FC))
            fig_bucket_bar.update_layout(
                font=dict(color=_FC), showlegend=False,
                plot_bgcolor="white", paper_bgcolor="white", height=360,
                xaxis=dict(title="Time Period", tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                yaxis=dict(title=metric_name, tickfont=dict(color=_FC), title_font=dict(color=_FC)),
            )
            st.plotly_chart(fig_bucket_bar, use_container_width=True)

        with c2:
            fig_bucket_pie = px.pie(
                bucket_agg, values="revenue", names="time_bucket",
                color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], "#0d3b5e", "#7ecae0"],
                title="Revenue Share by Time Period", hole=0.4,
            )
            fig_bucket_pie.update_traces(textposition="outside", textinfo="percent+label",
                                         textfont=dict(color=_FC))
            fig_bucket_pie.update_layout(
                font=dict(color=_FC), showlegend=False,
                paper_bgcolor="white", height=360,
            )
            st.plotly_chart(fig_bucket_pie, use_container_width=True)

        st.markdown('<p class="section-header">🏪 Time Bucket Performance by Store</p>', unsafe_allow_html=True)
        bucket_store = df.groupby(["store_location", "time_bucket"], observed=True).agg(
            revenue=("revenue", "sum"),
            transactions=("transaction_id", "count"),
        ).reset_index()
        fig_stacked = px.bar(
            bucket_store,
            x="store_location",
            y="revenue" if metric_toggle == "Revenue ($)" else "transactions",
            color="time_bucket", barmode="group",
            color_discrete_sequence=[COLORS["primary"], COLORS["secondary"], "#0d3b5e", "#7ecae0"],
            title=f"{metric_name} by Store and Time Period",
            labels={"store_location": "Store", "revenue": "Revenue ($)",
                    "transactions": "Transactions", "time_bucket": "Period"},
        )
        fig_stacked.update_layout(
            font=dict(color=_FC), plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
            yaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
            legend=dict(orientation="h", y=-0.2, font=dict(color=_FC)), height=380,
        )
        st.plotly_chart(fig_stacked, use_container_width=True)

    except Exception as e:
        st.error(f"**Tab 3 error:** {e}")
        st.exception(e)

# ─── TAB 4 — Store Comparison ────────────────────────────────────────────────
with tab4:
    try:
        st.markdown('<p class="section-header">🏪 Cross-Location Performance Comparison</p>', unsafe_allow_html=True)

        store_summary = df.groupby("store_location").agg(
            total_revenue=("revenue", "sum"),
            total_txns=("transaction_id", "count"),
            avg_txn=("revenue", "mean"),
            avg_qty=("transaction_qty", "mean"),
        ).reset_index().sort_values("total_revenue", ascending=False)

        cols = st.columns(len(sel_stores))
        for i, row in store_summary.iterrows():
            with cols[list(store_summary.index).index(i)]:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-value">${row["total_revenue"]:,.0f}</div>'
                    f'<div class="metric-label">{row["store_location"]}<br>'
                    f'{row["total_txns"]:,} txns · Avg ${row["avg_txn"]:.2f}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)

        with c1:
            hourly_store = df.groupby(["store_location", "hour"]).agg(
                revenue=("revenue", "sum"),
                transactions=("transaction_id", "count"),
            ).reset_index()
            fig_compare = px.line(
                hourly_store,
                x="hour", y="revenue" if metric_toggle == "Revenue ($)" else "transactions",
                color="store_location", color_discrete_map=STORE_COLOR_MAP,
                markers=True,
                title=f"Hourly {metric_name} — Store Comparison",
                labels={"hour": "Hour of Day", "revenue": "Revenue ($)", "transactions": "Transactions"},
            )
            fig_compare.update_xaxes(
                tickvals=list(range(6, 21)),
                ticktext=[f"{h}:00" for h in range(6, 21)],
                tickfont=dict(color=_FC), title_font=dict(color=_FC),
            )
            fig_compare.update_layout(
                font=dict(color=_FC), plot_bgcolor="white", paper_bgcolor="white",
                yaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                legend=dict(orientation="h", y=-0.25, font=dict(color=_FC)), height=360,
            )
            st.plotly_chart(fig_compare, use_container_width=True)

        with c2:
            cat_store = df.groupby(["store_location", "product_category"])["revenue"].sum().reset_index()
            fig_cat = px.bar(
                cat_store, x="store_location", y="revenue",
                color="product_category",
                title="Revenue by Category per Store",
                labels={"store_location": "Store", "revenue": "Revenue ($)", "product_category": "Category"},
                color_discrete_sequence=px.colors.sequential.Blues_r,
            )
            fig_cat.update_layout(
                font=dict(color=_FC), plot_bgcolor="white", paper_bgcolor="white",
                xaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                yaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                legend=dict(orientation="h", y=-0.35, font=dict(color=_FC)), height=360,
            )
            st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown("**🎯 Peak Hour per Store**")
        peak_hours_df = df.groupby(["store_location", "hour"])["transaction_id"].count().reset_index()
        peak_per_store = peak_hours_df.loc[
            peak_hours_df.groupby("store_location")["transaction_id"].idxmax()
        ][["store_location", "hour", "transaction_id"]].rename(
            columns={"hour": "Peak Hour", "transaction_id": "Transactions at Peak"}
        )
        peak_per_store["Peak Hour"] = peak_per_store["Peak Hour"].apply(lambda h: f"{h}:00 – {h+1}:00")
        st.dataframe(peak_per_store, use_container_width=True, hide_index=True)

    except Exception as e:
        st.error(f"**Tab 4 error:** {e}")
        st.exception(e)

# ─── TAB 5 — Product Analysis ────────────────────────────────────────────────
with tab5:
    try:
        st.markdown('<p class="section-header">🛍️ Product Performance Analysis</p>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            cat_rev = df.groupby("product_category")["revenue"].sum().sort_values(ascending=True).reset_index()
            fig_cat_bar = px.bar(
                cat_rev, x="revenue", y="product_category",
                orientation="h",
                title="Revenue by Product Category",
                color="revenue",
                color_continuous_scale=["#d6eef8", "#1a6fa8"],
                labels={"revenue": "Revenue ($)", "product_category": "Category"},
            )
            fig_cat_bar.update_layout(
                font=dict(color=_FC), plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False, height=380,
                xaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                yaxis=dict(tickfont=dict(color=_FC), title=""),
            )
            st.plotly_chart(fig_cat_bar, use_container_width=True)

        with c2:
            top_products = (
                df.groupby("product_detail")["revenue"]
                .sum().sort_values(ascending=False).head(15).reset_index()
            )
            fig_top = px.bar(
                top_products, x="revenue", y="product_detail",
                orientation="h",
                title="Top 15 Products by Revenue",
                color="revenue",
                color_continuous_scale=["#5ab4d6", "#0d3b5e"],
                labels={"revenue": "Revenue ($)", "product_detail": "Product"},
            )
            fig_top.update_layout(
                font=dict(color=_FC), plot_bgcolor="white", paper_bgcolor="white",
                coloraxis_showscale=False, height=380,
                xaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
                yaxis=dict(autorange="reversed", tickfont=dict(color=_FC), title=""),
            )
            st.plotly_chart(fig_top, use_container_width=True)

        st.markdown('<p class="section-header">⏰ Category Demand by Hour</p>', unsafe_allow_html=True)
        cat_hour = df.groupby(["hour", "product_category"])["revenue"].sum().reset_index()
        top_cats = df.groupby("product_category")["revenue"].sum().nlargest(5).index.tolist()
        cat_hour_top = cat_hour[cat_hour["product_category"].isin(top_cats)]

        fig_cat_hour = px.line(
            cat_hour_top, x="hour", y="revenue",
            color="product_category", markers=True,
            title="Hourly Revenue for Top 5 Categories",
            labels={"hour": "Hour of Day", "revenue": "Revenue ($)", "product_category": "Category"},
            color_discrete_sequence=["#1a6fa8", "#5ab4d6", "#0d3b5e", "#7ecae0", "#083060"],
        )
        fig_cat_hour.update_xaxes(
            tickvals=list(range(6, 21)),
            ticktext=[f"{h}:00" for h in range(6, 21)],
            tickfont=dict(color=_FC), title_font=dict(color=_FC),
        )
        fig_cat_hour.update_layout(
            font=dict(color=_FC), plot_bgcolor="white", paper_bgcolor="white",
            yaxis=dict(tickfont=dict(color=_FC), title_font=dict(color=_FC)),
            legend=dict(orientation="h", y=-0.2, font=dict(color=_FC)), height=360,
        )
        st.plotly_chart(fig_cat_hour, use_container_width=True)

    except Exception as e:
        st.error(f"**Tab 5 error:** {e}")
        st.exception(e)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("☕ Afficionado Coffee Roasters | Sales Analytics Dashboard | Data: 149,116 transactions across 3 locations, 2025")
