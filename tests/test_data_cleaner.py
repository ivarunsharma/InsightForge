import pytest
import pandas as pd
from src.data_cleaner import load_and_clean

@pytest.fixture(scope="module")
def clean_df():
    return load_and_clean()


# ── Row count ─────────────────────────────────────────────────────────────────

def test_row_count(clean_df):
    # ~7,010 rows after cleaning — allow ±200 for minor source data variation
    assert 6800 <= len(clean_df) <= 7200, f"Unexpected row count: {len(clean_df)}"


# ── Column dtypes ─────────────────────────────────────────────────────────────

def test_sales_is_numeric(clean_df):
    assert pd.api.types.is_float_dtype(clean_df["Sales"]) or \
           pd.api.types.is_integer_dtype(clean_df["Sales"])

def test_profit_is_numeric(clean_df):
    assert pd.api.types.is_float_dtype(clean_df["Profit"]) or \
           pd.api.types.is_integer_dtype(clean_df["Profit"])

def test_order_date_is_datetime(clean_df):
    assert pd.api.types.is_datetime64_any_dtype(clean_df["Order Date"])

def test_ship_date_is_datetime(clean_df):
    assert pd.api.types.is_datetime64_any_dtype(clean_df["Ship Date"])


# ── No nulls in critical columns ──────────────────────────────────────────────

def test_no_nulls_in_critical_columns(clean_df):
    for col in ["Sales", "Profit", "Region", "Segment", "Order Date"]:
        assert clean_df[col].isna().sum() == 0, f"Nulls found in {col}"


# ── Region values ─────────────────────────────────────────────────────────────

def test_region_values(clean_df):
    assert set(clean_df["Region"].unique()) == {"South", "West", "East", "Central"}

def test_no_dirty_region_variants(clean_df):
    dirty = {"south", "SOUTH", "Sth", "S.", "west", "WEST", "east", "EAST",
             "central", "CENTRAL"}
    found = set(clean_df["Region"].unique()) & dirty
    assert not found, f"Dirty region values still present: {found}"


# ── Segment values ────────────────────────────────────────────────────────────

def test_segment_values(clean_df):
    assert set(clean_df["Segment"].unique()) == {"Consumer", "Corporate", "Home Office"}


# ── Ship Mode values ──────────────────────────────────────────────────────────

def test_ship_mode_values(clean_df):
    assert set(clean_df["Ship Mode"].unique()).issubset(
        {"Standard Class", "Second Class", "First Class", "Same Day"}
    )


# ── Business logic guards ─────────────────────────────────────────────────────

def test_no_sales_outliers(clean_df):
    assert clean_df["Sales"].max() <= 50000, \
        f"Sales outlier above $50,000: {clean_df['Sales'].max()}"

def test_quantity_non_negative(clean_df):
    assert (clean_df["Quantity"] >= 0).all(), "Negative Quantity values found"

def test_no_duplicate_rows(clean_df):
    assert clean_df.duplicated().sum() == 0, "Duplicate rows found after cleaning"

def test_customer_name_no_leading_trailing_whitespace(clean_df):
    assert (clean_df["Customer Name"] == clean_df["Customer Name"].str.strip()).all()
