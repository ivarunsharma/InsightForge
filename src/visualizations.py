import matplotlib.pyplot as plt
import pandas as pd


def plot_sales_by_region(df):
    fig, ax = plt.subplots()
    df.groupby("Region")["Sales"].sum().sort_values().plot(
        kind="barh", ax=ax, color="steelblue")
    ax.set_title("Total Sales by Region")
    ax.set_xlabel("Sales ($)")
    return fig


def plot_profit_by_category(df):
    fig, ax = plt.subplots()
    df.groupby("Category")["Profit"].sum().plot(
        kind="bar", ax=ax, color="steelblue")
    ax.set_title("Total Profit by Category")
    ax.set_ylabel("Profit ($)")
    plt.xticks(rotation=0)
    return fig


def plot_monthly_trend(df):
    df = df.copy()
    df["Month"] = pd.to_datetime(df["Order Date"]).dt.to_period("M")
    monthly = df.groupby("Month")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(10, 4))
    monthly.plot(ax=ax, marker="o", color="steelblue")
    ax.set_title("Monthly Sales Trend")
    ax.set_ylabel("Sales ($)")
    return fig


def plot_discount_vs_profit(df):
    fig, ax = plt.subplots()
    ax.scatter(df["Discount"], df["Profit"], alpha=0.4, color="steelblue")
    ax.set_title("Discount vs Profit")
    ax.set_xlabel("Discount")
    ax.set_ylabel("Profit ($)")
    return fig


def plot_top_subcategories(df, n=10):
    fig, ax = plt.subplots()
    df.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False).head(n).plot(
        kind="barh", ax=ax, color="steelblue")
    ax.set_title(f"Top {n} Sub-Categories by Sales")
    ax.set_xlabel("Sales ($)")
    return fig


def generate_auto_insights(df, llm):
    top_region    = df.groupby("Region")["Sales"].sum().idxmax()
    worst_cat     = df.groupby("Category")["Profit"].sum().idxmin()
    best_segment  = df.groupby("Segment")["Profit"].sum().idxmax()
    avg_discount  = df["Discount"].mean()
    total_revenue = df["Sales"].sum()
    total_profit  = df["Profit"].sum()
    margin        = total_profit / total_revenue

    summary = f"""
    TechRetail Corporation FY Summary:
    - Top region by sales: {top_region}
    - Worst category by profit: {worst_cat}
    - Best performing segment: {best_segment}
    - Average discount given: {avg_discount:.1%}
    - Total revenue: ${total_revenue:,.0f}
    - Total profit: ${total_profit:,.0f}
    - Profit margin: {margin:.1%}
    """
    prompt = (
        "You are a business analyst. Based on this data summary, "
        "write exactly 3 concise, actionable business recommendations. "
        "Be specific. Use bullet points.\n\n" + summary
    )
    return llm.invoke(prompt).content
