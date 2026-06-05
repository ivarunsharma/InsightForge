import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd

# Pastel palette matching the app theme
BLUE_DARK   = "#1a4a7a"
BLUE_MID    = "#4fa8d6"
BLUE_LIGHT  = "#90c4e8"
GREEN_MID   = "#5daf80"
GREEN_LIGHT = "#a8d5b8"
BG          = "#ffffff"
GRID        = "#e8f1f8"
TEXT        = "#1a4a7a"
PALETTE     = [BLUE_MID, GREEN_MID, "#f4a261", "#e76f51", BLUE_LIGHT, GREEN_LIGHT]


def _apply_style(ax, fig):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)
    ax.title.set_fontsize(11)
    ax.title.set_fontweight("bold")
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def plot_sales_by_region(df):
    fig, ax = plt.subplots(figsize=(5, 3.2))
    data = df.groupby("Region")["Sales"].sum().sort_values()
    bars = data.plot(kind="barh", ax=ax, color=BLUE_MID, edgecolor="none")
    ax.set_title("Sales by Region")
    ax.set_xlabel("Sales ($)")
    _apply_style(ax, fig)
    fig.tight_layout()
    return fig


def plot_profit_by_category(df):
    fig, ax = plt.subplots(figsize=(5, 3.2))
    data = df.groupby("Category")["Profit"].sum()
    colors = [GREEN_MID if v >= 0 else "#e76f51" for v in data.values]
    data.plot(kind="bar", ax=ax, color=colors, edgecolor="none")
    ax.set_title("Profit by Category")
    ax.set_ylabel("Profit ($)")
    plt.xticks(rotation=0)
    _apply_style(ax, fig)
    fig.tight_layout()
    return fig


def plot_monthly_trend(df):
    df = df.copy()
    df["Month"] = pd.to_datetime(df["Order Date"]).dt.to_period("M")
    monthly = df.groupby("Month")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(10, 3.5))
    ax.plot(range(len(monthly)), monthly.values, marker="o", color=BLUE_MID,
            linewidth=2, markersize=4, markerfacecolor=BLUE_DARK)
    ax.fill_between(range(len(monthly)), monthly.values, alpha=0.12, color=BLUE_MID)
    ax.set_xticks(range(len(monthly)))
    ax.set_xticklabels([str(p) for p in monthly.index], rotation=45, ha="right", fontsize=7)
    ax.set_title("Monthly Sales Trend")
    ax.set_ylabel("Sales ($)")
    _apply_style(ax, fig)
    fig.tight_layout()
    return fig


def plot_discount_vs_profit(df):
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.scatter(df["Discount"], df["Profit"], alpha=0.35, color=BLUE_MID,
               edgecolors="none", s=18)
    ax.set_title("Discount vs Profit")
    ax.set_xlabel("Discount")
    ax.set_ylabel("Profit ($)")
    _apply_style(ax, fig)
    fig.tight_layout()
    return fig


def plot_top_subcategories(df, n=10):
    fig, ax = plt.subplots(figsize=(5, 3.8))
    data = df.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False).head(n)
    colors = [BLUE_MID if i % 2 == 0 else BLUE_LIGHT for i in range(len(data))]
    data.sort_values().plot(kind="barh", ax=ax, color=colors, edgecolor="none")
    ax.set_title(f"Top {n} Sub-Categories")
    ax.set_xlabel("Sales ($)")
    _apply_style(ax, fig)
    fig.tight_layout()
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
