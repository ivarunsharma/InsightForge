"""
Generates JPEG business chart images for InsightForge data directory.
Mix of:
  - Charts based on Superstore dataset values (matching)
  - Charts with fictional/external data (non-matching)
  - Some images with visual noise: low DPI, scan artifacts, overlapping text
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import warnings
warnings.filterwarnings("ignore")

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
os.makedirs(OUT, exist_ok=True)

# ── colour palette ──────────────────────────────────────────────────────────
BLUE   = "#2E86AB"
ORANGE = "#F4A261"
GREEN  = "#2A9D8F"
RED    = "#E76F51"
PURPLE = "#6A4C93"
GREY   = "#AAAAAA"


def save(fig, name, dpi=120):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=dpi, bbox_inches="tight", format="jpeg")
    plt.close(fig)
    print(f"  Created: {name}")
    return path


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 1 — Sales by Region (matches Superstore)
# ────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 5))
regions  = ["West", "East", "Central", "South"]
sales    = [725457, 678781, 501239, 391723]
profits  = [108418,  91523,  39706,  46749]
x = np.arange(len(regions))
w = 0.4

bars1 = ax.bar(x - w/2, sales,   width=w, color=BLUE,   label="Sales ($)")
bars2 = ax.bar(x + w/2, profits, width=w, color=GREEN,  label="Profit ($)")

ax.set_title("Sales & Profit by Region — FY2017", fontsize=14, fontweight="bold", pad=12)
ax.set_xticks(x); ax.set_xticklabels(regions, fontsize=11)
ax.set_ylabel("Amount (USD)", fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v:,.0f}"))
ax.legend(fontsize=9)
ax.set_ylim(0, 850000)

for bar in bars1:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8000,
            f"${bar.get_height()/1000:.0f}K", ha="center", va="bottom", fontsize=8)
for bar in bars2:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8000,
            f"${bar.get_height()/1000:.0f}K", ha="center", va="bottom", fontsize=8, color=GREEN)

ax.text(0.99, 0.01, "Source: Superstore FY2017 | INTERNAL ONLY",
        transform=ax.transAxes, fontsize=7, color=GREY, ha="right", va="bottom")
fig.tight_layout()
save(fig, "sales_by_region_2017.jpg")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 2 — Monthly Sales Trend (matches Superstore, 2016+2017 dual year)
# ────────────────────────────────────────────────────────────────────────────
months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
sales_2016 = [94200,82100,121300,108400,115600,102300,112700,131400,148200,162400,155800,135100]
sales_2017 = [102300,89400,138200,121600,131200,118400,124800,152100,167300,181200,174600,146800]

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(months, sales_2016, marker="o", color=ORANGE, linewidth=2, markersize=6, label="2016")
ax.plot(months, sales_2017, marker="s", color=BLUE,   linewidth=2, markersize=6, label="2017")
ax.fill_between(months, sales_2016, sales_2017, alpha=0.08, color=BLUE)

ax.set_title("Monthly Sales Trend — 2016 vs 2017", fontsize=14, fontweight="bold", pad=12)
ax.set_ylabel("Monthly Sales (USD)", fontsize=10)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))
ax.legend(fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.4)

# inject a noisy annotation to simulate a handwritten sticky note
ax.annotate("?? check Sep\nspike source",
            xy=(8, 167300), xytext=(9.2, 175000),
            arrowprops=dict(arrowstyle="->", color="red", lw=1.2),
            fontsize=8, color="red", style="italic")
ax.text(0.01, 0.97, "DRAFT — not for distribution", transform=ax.transAxes,
        fontsize=8, color="red", alpha=0.6, va="top")
fig.tight_layout()
save(fig, "monthly_sales_trend_2016_2017.jpg")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 3 — Category & Sub-Category Profit Heatmap (matches Superstore)
# ────────────────────────────────────────────────────────────────────────────
subcats = ["Phones","Chairs","Storage","Binders","Machines",
           "Accessories","Copiers","Bookcases","Appliances","Tables"]
categories = ["Technology","Furniture","Office Supplies"]
# profit values ($) per sub-cat (some negative for Tables — intentional)
profit_vals = np.array([
    [44515,     0,      0,      0,      41935, 22638, 55618,     0,      0,      0    ],
    [0,      26590,     0,      0,      0,      0,      0,     21002,  6781, -17725   ],
    [0,          0,  21899,  30221,     0,      0,      0,      0,      0,      0    ],
])

fig, ax = plt.subplots(figsize=(12, 4))
# mask zeros
masked = np.ma.masked_where(profit_vals == 0, profit_vals)
im = ax.imshow(masked, cmap="RdYlGn", aspect="auto", vmin=-20000, vmax=60000)
ax.set_xticks(range(len(subcats))); ax.set_xticklabels(subcats, rotation=35, ha="right", fontsize=9)
ax.set_yticks(range(len(categories))); ax.set_yticklabels(categories, fontsize=10)
plt.colorbar(im, ax=ax, label="Gross Profit (USD)", shrink=0.8)
ax.set_title("Profit Heatmap by Category & Sub-Category — FY2017", fontsize=13, fontweight="bold", pad=10)

for i in range(len(categories)):
    for j in range(len(subcats)):
        v = profit_vals[i, j]
        if v != 0:
            ax.text(j, i, f"${v/1000:.1f}K", ha="center", va="center",
                    fontsize=8, color="black" if abs(v) < 40000 else "white")
fig.tight_layout()
save(fig, "profit_heatmap_by_category.jpg")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 4 — Customer Segment Pie + Donut (matches Superstore)
# ────────────────────────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

seg_labels  = ["Consumer", "Corporate", "Home Office"]
seg_orders  = [5191, 3020, 1783]
seg_revenue = [1148061, 706146, 430993]
seg_colors  = [BLUE, ORANGE, GREEN]

wedges, texts, autotexts = ax1.pie(
    seg_orders, labels=seg_labels, colors=seg_colors,
    autopct="%1.1f%%", startangle=140,
    wedgeprops=dict(edgecolor="white", linewidth=2))
for at in autotexts: at.set_fontsize(10)
ax1.set_title("Order Volume by Segment", fontsize=11, fontweight="bold")

wedges2, _, autotexts2 = ax2.pie(
    seg_revenue, colors=seg_colors,
    autopct="%1.1f%%", startangle=140,
    wedgeprops=dict(width=0.5, edgecolor="white", linewidth=2))
for at in autotexts2: at.set_fontsize(10)
ax2.legend(wedges2, [f"{l}\n${v/1000:.0f}K" for l, v in zip(seg_labels, seg_revenue)],
           loc="lower left", fontsize=8)
ax2.set_title("Revenue Share by Segment", fontsize=11, fontweight="bold")

fig.suptitle("Customer Segment Analysis — FY2017", fontsize=13, fontweight="bold", y=1.02)
fig.tight_layout()
save(fig, "customer_segment_analysis.jpg")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 5 — Top 10 Sub-Categories by Sales (matches Superstore)
# ────────────────────────────────────────────────────────────────────────────
top_subs   = ["Phones","Chairs","Storage","Tables","Binders",
              "Machines","Accessories","Copiers","Bookcases","Paper"]
top_sales  = [330007, 328449, 223844, 206966, 203413,
              189239, 167380, 149528, 114880, 78479]
top_profit = [44515,  26590,  21899, -17725,  30221,
               3385,  22638,  55618,  21002,  34054]
colors_bar = [GREEN if p >= 0 else RED for p in top_profit]

fig, ax = plt.subplots(figsize=(9, 6))
y_pos = range(len(top_subs))
bars = ax.barh(list(reversed(top_subs)), list(reversed(top_sales)),
               color=list(reversed(colors_bar)), edgecolor="white")

for bar, profit in zip(bars, reversed(top_profit)):
    label = f"  ${profit/1000:+.1f}K profit"
    color = "green" if profit >= 0 else "red"
    ax.text(bar.get_width() + 3000, bar.get_y() + bar.get_height()/2,
            label, va="center", fontsize=8, color=color)

ax.set_xlabel("Total Sales (USD)", fontsize=10)
ax.set_title("Top 10 Sub-Categories by Sales — FY2017\n(bar colour = profit: green positive, red negative)",
             fontsize=12, fontweight="bold")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))
ax.set_xlim(0, 430000)
ax.grid(axis="x", linestyle="--", alpha=0.3)
fig.tight_layout()
save(fig, "top10_subcategories_sales.jpg")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 6 — Discount vs Profit Scatter (matches Superstore — shows abuse)
# ────────────────────────────────────────────────────────────────────────────
np.random.seed(42)
n = 400
discount = np.concatenate([
    np.random.uniform(0, 0.2, 200),
    np.random.uniform(0.3, 0.8, 200)
])
profit = (0.25 - discount) * np.random.uniform(200, 1200, n) + np.random.normal(0, 30, n)
cats = np.random.choice(["Technology","Furniture","Office Supplies"], n, p=[0.36,0.32,0.32])
cat_colors_map = {"Technology": BLUE, "Furniture": ORANGE, "Office Supplies": GREEN}
point_colors = [cat_colors_map[c] for c in cats]

fig, ax = plt.subplots(figsize=(9, 5))
sc = ax.scatter(discount * 100, profit, c=point_colors, alpha=0.45, s=25, edgecolors="none")
ax.axhline(0, color="red", linewidth=1.2, linestyle="--", label="Break-even")
ax.axvline(20, color="grey", linewidth=1, linestyle=":", label="20% discount target")
ax.set_xlabel("Discount (%)", fontsize=10)
ax.set_ylabel("Profit per Order (USD)", fontsize=10)
ax.set_title("Discount Rate vs Profit — All Orders FY2017\n(Note: high discount → negative profit pattern)",
             fontsize=12, fontweight="bold")
legend_handles = [mpatches.Patch(color=v, label=k) for k, v in cat_colors_map.items()]
legend_handles += [plt.Line2D([0],[0], color="red", linestyle="--", label="Break-even"),
                   plt.Line2D([0],[0], color="grey", linestyle=":", label="20% target")]
ax.legend(handles=legend_handles, fontsize=8, loc="upper right")

# noise: a messy stamp
ax.text(0.5, 0.5, "PRELIMINARY\nDO NOT CITE",
        transform=ax.transAxes, fontsize=28, color="red",
        alpha=0.12, ha="center", va="center", rotation=30, fontweight="bold")
fig.tight_layout()
save(fig, "discount_vs_profit_scatter.jpg")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 7 — Shipping Mode Dashboard (matches + some noise labels)
# ────────────────────────────────────────────────────────────────────────────
ship_modes   = ["Standard\nClass", "Second\nClass", "First\nClass", "Same Day"]
ship_orders  = [5968, 1945, 1538, 543]
ship_avdays  = [5.0,  3.1,  2.0,  0.9]
ship_cost    = [6.12, 9.44, 14.77, 23.18]
ship_revenue = [5.80, 9.10, 14.20, 17.90]   # avg revenue per shipment (same-day LOSS)

fig = plt.figure(figsize=(12, 7))
gs = GridSpec(2, 2, figure=fig, hspace=0.45, wspace=0.35)

# top-left: order volume
ax1 = fig.add_subplot(gs[0, 0])
ax1.bar(ship_modes, ship_orders, color=[BLUE, GREEN, ORANGE, RED])
ax1.set_title("Order Volume by Ship Mode", fontsize=10, fontweight="bold")
ax1.set_ylabel("# Orders")
for i, v in enumerate(ship_orders):
    ax1.text(i, v + 40, str(v), ha="center", fontsize=9)

# top-right: avg delivery days
ax2 = fig.add_subplot(gs[0, 1])
ax2.bar(ship_modes, ship_avdays, color=[BLUE, GREEN, ORANGE, RED])
ax2.set_title("Avg Delivery Days", fontsize=10, fontweight="bold")
ax2.set_ylabel("Days")
for i, v in enumerate(ship_avdays):
    ax2.text(i, v + 0.05, f"{v}", ha="center", fontsize=9)

# bottom-left: cost vs revenue per shipment
ax3 = fig.add_subplot(gs[1, 0])
x  = np.arange(len(ship_modes))
ax3.bar(x - 0.2, ship_cost,    0.4, color=RED,   label="Cost/order")
ax3.bar(x + 0.2, ship_revenue, 0.4, color=GREEN, label="Revenue/order")
ax3.set_title("Cost vs Revenue per Shipment", fontsize=10, fontweight="bold")
ax3.set_xticks(x); ax3.set_xticklabels(ship_modes)
ax3.set_ylabel("USD")
ax3.legend(fontsize=8)
ax3.annotate("LOSS!", xy=(3, 18), fontsize=9, color="red", fontweight="bold")

# bottom-right: pie of order split
ax4 = fig.add_subplot(gs[1, 1])
ax4.pie(ship_orders, labels=ship_modes, colors=[BLUE, GREEN, ORANGE, RED],
        autopct="%1.0f%%", startangle=90, textprops={"fontsize": 9})
ax4.set_title("Order Split %", fontsize=10, fontweight="bold")

# noise: messy header note
fig.text(0.5, 0.98, "Shipping Performance Dashboard — FY2017   [DRAFT — figures TBC with ops team]",
         ha="center", fontsize=11, fontweight="bold", color="navy")
fig.text(0.5, 0.01, "NOTE: Same-day avg cost $23.18 > avg revenue $17.90 — unprofitable",
         ha="center", fontsize=8, color="red")
save(fig, "shipping_performance_dashboard.jpg")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 8 — Competitor Market Share (NON-Superstore data — external)
# + low DPI / scan-quality noise applied via PIL
# ────────────────────────────────────────────────────────────────────────────
companies  = ["Amazon\nBusiness", "Office\nDepot", "Staples", "TechRetail\n(Us)", "Grainger", "Others"]
share_2017 = [28.4, 18.2, 16.9, 8.1, 7.3, 21.1]
share_2016 = [22.1, 20.4, 18.7, 8.4, 7.8, 22.6]

fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(companies))
ax.bar(x - 0.2, share_2016, 0.4, color=GREY,   label="2016 Share %", alpha=0.8)
ax.bar(x + 0.2, share_2017, 0.4, color=PURPLE, label="2017 Share %", alpha=0.9)
ax.set_xticks(x); ax.set_xticklabels(companies, fontsize=10)
ax.set_ylabel("Market Share (%)")
ax.set_title("US Office Products Market Share — Competitive Landscape\n"
             "(Source: IBISWorld est. 2017 — NOT internal Superstore data)",
             fontsize=11, fontweight="bold")
ax.legend(fontsize=9)
ax.set_ylim(0, 36)
for i, (s16, s17) in enumerate(zip(share_2016, share_2017)):
    ax.text(i - 0.2, s16 + 0.4, f"{s16}%", ha="center", fontsize=8, color="grey")
    ax.text(i + 0.2, s17 + 0.4, f"{s17}%", ha="center", fontsize=8)

ax.text(0, 30, "⚠ COMPETITOR DATA — estimates only. Do not mix with internal figures.",
        fontsize=8, color="red", style="italic")
fig.tight_layout()

# save at low DPI first, then degrade with PIL to simulate scanned/faxed doc
low_dpi_path = os.path.join(OUT, "_tmp_market_share.jpg")
fig.savefig(low_dpi_path, dpi=55, bbox_inches="tight", format="jpeg")
plt.close(fig)

img = Image.open(low_dpi_path)
img = img.filter(ImageFilter.GaussianBlur(radius=0.8))
img_arr = np.array(img, dtype=np.float32)
noise = np.random.normal(0, 12, img_arr.shape)
img_arr = np.clip(img_arr + noise, 0, 255).astype(np.uint8)
img_noisy = Image.fromarray(img_arr)

# add a "SCANNED" watermark text
draw = ImageDraw.Draw(img_noisy)
w, h = img_noisy.size
draw.text((w//2 - 60, h//2 - 15), "SCANNED COPY", fill=(200, 180, 180))

final_path = os.path.join(OUT, "competitor_market_share_scan.jpg")
img_noisy.save(final_path, "JPEG", quality=60)
os.remove(low_dpi_path)
print(f"  Created: competitor_market_share_scan.jpg  (low-quality scan simulation)")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 9 — Quarterly Revenue Waterfall Chart (matches Superstore)
# ────────────────────────────────────────────────────────────────────────────
quarters   = ["Q1 2017", "Q2 2017", "Q3 2017", "Q4 2017", "FY Total"]
values     = [480200, 531300, 637500, 648200, 2297200]
is_total   = [False,  False,  False,  False,  True]
running    = [0, 480200, 1011500, 1649000, 0]

fig, ax = plt.subplots(figsize=(9, 5))
bar_colors = [BLUE if not t else ORANGE for t in is_total]
bottoms    = [r if not t else 0 for r, t in zip(running, is_total)]

bars = ax.bar(quarters, values, bottom=bottoms, color=bar_colors,
              edgecolor="white", linewidth=1.5, width=0.55)

for bar, val, bot, tot in zip(bars, values, bottoms, is_total):
    ypos = bot + val/2
    ax.text(bar.get_x() + bar.get_width()/2, ypos,
            f"${val/1000:.0f}K", ha="center", va="center",
            fontsize=9, color="white", fontweight="bold")

for i in range(len(quarters) - 2):
    ax.plot([i + 0.275, i + 0.725],
            [running[i+1], running[i+1]],
            color="grey", linewidth=0.8, linestyle="--")

ax.set_title("Quarterly Revenue Waterfall — FY2017", fontsize=13, fontweight="bold", pad=10)
ax.set_ylabel("Revenue (USD)")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"${v/1000:.0f}K"))
ax.set_ylim(0, 2600000)
legend_els = [mpatches.Patch(color=BLUE, label="Quarterly Revenue"),
              mpatches.Patch(color=ORANGE, label="FY Total")]
ax.legend(handles=legend_els, fontsize=9)
ax.text(0.99, 0.01, "FY2017 Total: $2,297,200", transform=ax.transAxes,
        fontsize=9, color=ORANGE, ha="right", va="bottom", fontweight="bold")
fig.tight_layout()
save(fig, "quarterly_revenue_waterfall.jpg")


# ────────────────────────────────────────────────────────────────────────────
# IMAGE 10 — Mixed Dashboard with intentional label noise
# (some values don't match Superstore exactly — simulate manual data entry errors)
# ────────────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(12, 8))
fig.patch.set_facecolor("#F5F5F5")
gs2 = GridSpec(2, 3, figure=fig, hspace=0.5, wspace=0.4)

# KPI boxes
kpis = [
    ("Total Revenue",    "$2,297,200",  BLUE),
    ("Total Profit",     "$286,397",    GREEN),
    ("Total Orders",     "9,994",       ORANGE),
    ("Avg Order Value",  "$229.85",     PURPLE),
    ("Return Rate",      "3.3%",        RED),
    ("Retention Rate",   "68%  ← LOW",  RED),
]
for idx, (label, value, color) in enumerate(kpis):
    row, col = divmod(idx, 3)
    ax = fig.add_subplot(gs2[row, col])
    ax.set_facecolor(color)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.62, value,  ha="center", va="center", fontsize=18,
            fontweight="bold", color="white", transform=ax.transAxes)
    ax.text(0.5, 0.25, label,  ha="center", va="center", fontsize=10,
            color="white", alpha=0.9, transform=ax.transAxes)

fig.suptitle("InsightForge — Executive KPI Dashboard FY2017\n"
             "[DRAFT — some figures manually entered, verify against source]",
             fontsize=13, fontweight="bold", y=1.01)

# noise: misaligned note
fig.text(0.01, 0.01,
         "⚠ Retention 68% — source: CRM export Nov 2017 (may not include Dec closures)\n"
         "⚠ Return rate from ops report — cross-check with finance\n"
         "⚠ Avg Order Value: $229.85 [another source says $232.10 — discrepancy not resolved]",
         fontsize=7.5, color="darkred", va="bottom")

save(fig, "executive_kpi_dashboard.jpg", dpi=110)


print(f"\nAll JPEG images saved to: {OUT}")
print("\nFull data directory contents:")
for f in sorted(os.listdir(OUT)):
    if not f.startswith("."):
        size = os.path.getsize(os.path.join(OUT, f))
        print(f"  {f:55s}  {size/1024:7.1f} KB")
