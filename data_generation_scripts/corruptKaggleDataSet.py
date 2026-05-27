import pandas as pd
import numpy as np
import random

df = pd.read_csv("data/Sample - Superstore.csv", encoding="latin1")
df_messy = df.copy()
np.random.seed(42)

# 1. inject missing values randomly across key columns
for col in ["Sales", "Profit", "Region", "Segment", "Discount"]:
    null_idx = df_messy.sample(frac=0.07).index
    df_messy.loc[null_idx, col] = np.nan

# 2. duplicate ~3% of rows
dupes = df_messy.sample(frac=0.03)
df_messy = pd.concat([df_messy, dupes]).reset_index(drop=True)

# 3. inconsistent region names
replacements = {"South": random.choice(["south", "SOUTH", "Sth", "S."]),
                "North": random.choice(["north", "NORTH", "Nth", "N."])}
mask = df_messy.sample(frac=0.15).index
df_messy.loc[mask, "Region"] = df_messy.loc[mask, "Region"].replace(replacements)

# 4. mixed date formats
mixed_idx = df_messy.sample(frac=0.2).index
df_messy.loc[mixed_idx, "Order Date"] = pd.to_datetime(
    df_messy.loc[mixed_idx, "Order Date"]).dt.strftime("%d/%m/%y")

# 5. outliers in sales
outlier_idx = df_messy.sample(n=15).index
df_messy.loc[outlier_idx, "Sales"] = np.random.uniform(50000, 200000, 15)

# 6. negative quantities
neg_idx = df_messy.sample(n=20).index
df_messy.loc[neg_idx, "Quantity"] = -df_messy.loc[neg_idx, "Quantity"]

# 7. placeholder garbage values
garbage = ["N/A", "none", "--", "unknown", "?"]
for col in ["Segment", "Ship Mode"]:
    g_idx = df_messy.sample(frac=0.04).index
    df_messy.loc[g_idx, col] = random.choice(garbage)

# 8. whitespace in text columns
ws_idx = df_messy.sample(frac=0.1).index
df_messy.loc[ws_idx, "Customer Name"] = " " + df_messy.loc[ws_idx, "Customer Name"] + " "

# 9. wrong data types — convert profit to string for some rows
str_idx = df_messy.sample(frac=0.05).index
df_messy["Profit"] = df_messy["Profit"].astype(object)
df_messy.loc[str_idx, "Profit"] = df_messy.loc[str_idx, "Profit"].astype(str) + " USD"

# 10. save
df_messy.to_csv("data/superstore_messy.csv", index=False)
print(f"Messy dataset: {df_messy.shape}")
print(f"Nulls per column:\n{df_messy.isnull().sum()}")