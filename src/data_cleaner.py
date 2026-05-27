import pandas as pd


def load_and_clean(input_path="data/superstore_messy.csv",
                   output_path="data/superstore_clean.csv"):

    df = pd.read_csv(input_path, encoding="latin1")
    before = len(df)
    print(f"Loaded: {before} rows")

    # 1. Remove duplicate rows
    df = df.drop_duplicates()

    # 2. Standardize Region values
    region_map = {
        "south": "South", "SOUTH": "South", "Sth": "South", "S.": "South",
        "west": "West",   "WEST": "West",
        "east": "East",   "EAST": "East",
        "central": "Central", "CENTRAL": "Central"
    }
    df["Region"] = df["Region"].replace(region_map)

    # 3. Parse mixed date formats: original data is MM/DD/YYYY, corruption script injected
    #    DD/MM/YY for 20% of rows. Two-pass approach handles both without dropping rows.
    def _parse_dates(col):
        parsed = pd.to_datetime(col, dayfirst=False, errors="coerce")
        nat_mask = parsed.isna()
        if nat_mask.any():
            parsed[nat_mask] = pd.to_datetime(col[nat_mask], dayfirst=True, errors="coerce")
        return parsed

    df["Order Date"] = _parse_dates(df["Order Date"])
    df["Ship Date"]  = _parse_dates(df["Ship Date"])

    # 4. Fix Profit column — strip " USD" string suffix, convert to float
    df["Profit"] = df["Profit"].astype(str).str.replace(" USD", "", regex=False).str.strip()
    df["Profit"] = pd.to_numeric(df["Profit"], errors="coerce")

    # 5. Ensure Sales is numeric
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")

    # 6. Drop rows missing critical fields
    df = df.dropna(subset=["Sales", "Profit", "Region", "Segment", "Order Date"])

    # 7. Remove injected Sales outliers (anything above $50,000)
    df = df[df["Sales"] <= 50000]

    # 8. Fix negative Quantity (physically impossible)
    df["Quantity"] = df["Quantity"].abs()

    # 9. Remove invalid Segment values
    df = df[df["Segment"].isin(["Consumer", "Corporate", "Home Office"])]

    # 10. Remove invalid Ship Mode values
    df = df[df["Ship Mode"].isin(["Standard Class", "Second Class", "First Class", "Same Day"])]

    # 11. Strip whitespace from Customer Name
    df["Customer Name"] = df["Customer Name"].str.strip()

    after = len(df)
    print(f"Cleaned: {after} rows (removed {before - after})")
    print(f"\nRegion distribution:\n{df['Region'].value_counts()}")
    print(f"\nSales max: ${df['Sales'].max():,.2f}")
    print(f"Profit dtype: {df['Profit'].dtype}")

    df.to_csv(output_path, index=False)
    print(f"\nSaved: {output_path}")
    return df


if __name__ == "__main__":
    df = load_and_clean()
    print(df.describe())
