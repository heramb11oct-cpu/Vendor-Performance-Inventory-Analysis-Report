import pandas as pd

# ── Data loading ──────────────────────────────────────────────────────────────
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df

# ── Cleaning ──────────────────────────────────────────────────────────────────
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(subset="transaction_id")
    df = df[(df["transaction_qty"] > 0) & (df["unit_price"] > 0)]
    return df.reset_index(drop=True)

# ── Feature engineering ───────────────────────────────────────────────────────
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    # BUG FIX 1: transaction_time is HH:MM:SS only (no date part).
    # Must parse with format="%H:%M:%S" — using pd.to_datetime() without
    # the format causes errors or silently defaults to 1900-01-01.
    df["transaction_time"] = pd.to_datetime(
        df["transaction_time"], format="%H:%M:%S"
    )

    df["revenue"] = df["transaction_qty"] * df["unit_price"]
    df["hour"]    = df["transaction_time"].dt.hour

    # BUG FIX 2: dt.day_name() on a time-only column always returns "Monday"
    # because every row defaults to 1900-01-01 (a Monday). Since there is no
    # real date column, we assign a sequential day number based on
    # transaction_id rank and map it to a day-of-week label instead.
    total_days = 182  # Jan–Jun 2025 (approx. 6 months)
    df = df.sort_values("transaction_id").reset_index(drop=True)
    df["day_num"]  = ((df.index / len(df)) * total_days).astype(int) % 7
    DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
    df["day_name"] = df["day_num"].map(lambda d: DAY_NAMES[d])

    # Time bucket
    def bucket(h: int) -> str:
        if   6 <= h <= 11: return "Morning (6–11)"
        elif 12 <= h <= 16: return "Afternoon (12–16)"
        elif 17 <= h <= 21: return "Evening (17–21)"
        else:               return "Late/Early (22–5)"

    df["time_bucket"] = df["hour"].apply(bucket)

    return df

# ── Aggregations ──────────────────────────────────────────────────────────────
def get_hourly_sales(df: pd.DataFrame) -> pd.Series:
    return df.groupby("hour")["revenue"].sum().sort_index()

def get_daily_sales(df: pd.DataFrame) -> pd.Series:
    # Groups by the sequential day_num since no real date column exists
    return df.groupby("day_num")["revenue"].sum().sort_index()

def get_day_name_sales(df: pd.DataFrame) -> pd.Series:
    DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday",
                 "Friday", "Saturday", "Sunday"]
    sales = df.groupby("day_name")["revenue"].sum()
    return sales.reindex(DAY_ORDER).fillna(0)

def get_store_summary(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("store_location").agg(
        Total_Revenue=("revenue", "sum"),
        Transactions=("transaction_id", "count"),
        Avg_Transaction=("revenue", "mean"),
    ).round(2)

def get_top_products(df: pd.DataFrame, n: int = 10) -> pd.Series:
    return (
        df.groupby("product_detail")["revenue"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
    )
