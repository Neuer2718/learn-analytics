"""Exercise 1: Pareto analysis of dimensional shipping corrections.

Work through one STEP at a time. After each step, save and run:
    python src/pareto.py
and check that the output looks right before moving on.
"""

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Find the data relative to THIS file, so the script works no matter which
# folder the terminal is in.  __file__ = path of this script (src/pareto.py),
# .parent = src/, .parent.parent = the project folder.
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_DIR / "data" / "shipments.csv"

# ---------------------------------------------------------------------------
# STEP 1 (done for you): load the data and look at it.
# A pandas DataFrame is basically an Excel sheet in Python: rows and named columns.
# ---------------------------------------------------------------------------
df = pd.read_csv(DATA_PATH)

print(df.shape)            # (number of rows, number of columns)


# ---------------------------------------------------------------------------
# STEP 2: add a new column called "correction" = billed_charge - expected_charge
#
# In Excel you'd type =D2-E2 and drag it down. In pandas, one line does the
# whole column at once. Pattern:
#     df["new_column"] = df["column_a"] - df["column_b"]
#
# Then print df.head() again to check that the new column shows up.
# ---------------------------------------------------------------------------
df["correction"] = df["billed_charge"] - df["expected_charge"]
print(df.head())



# ---------------------------------------------------------------------------
# STEP 3: total the correction per SKU (like a PivotTable: Rows = sku,
# Values = Sum of correction).  Hint: look up  .groupby("sku")  and  .sum()
# Store the result in a variable called  by_sku.
# ---------------------------------------------------------------------------
# TODO
by_sku = df.groupby("sku")["correction"].sum()
print(by_sku)

# ---------------------------------------------------------------------------
# STEP 4: sort by_sku from largest to smallest, then add a cumulative % column.
# Hints: .sort_values(ascending=False)   .cumsum()   divide by the total
# ---------------------------------------------------------------------------
# TODO
by_sku = by_sku.sort_values(ascending=False)
cum_pct = by_sku.cumsum() / by_sku.sum()
print(cum_pct.head(10))


# ---------------------------------------------------------------------------
# STEP 5: print the total correction $, and how many SKUs it takes to reach
# 50% and 80% of it.
# ---------------------------------------------------------------------------
# TODO
n_50 = (cum_pct < 0.5).sum() + 1
n_80 = (cum_pct < 0.8).sum() + 1

print(f"Total correction: ${by_sku.sum():,.2f}")
print(f"SKUs to reach 50% of cost: {n_50}")
print(f"SKUs to reach 80% of cost: {n_80}")

# ---------------------------------------------------------------------------
# STEP 6 (later): Pareto chart saved to pareto.png. We'll do this together.
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))

top = by_sku.head(50)
ax.bar(range(1, len(top) + 1), top.values)
ax.set_xlabel("Top 50 SKUs")
ax.set_ylabel("Correction cost ($)")

top_cum = cum_pct.head(50)
ax2 = ax.twinx()
ax2.plot(range(len(top_cum)), top_cum.values * 100, color="red")
ax2.set_ylabel("Cumulative % of cost")
ax2.set_ylim(0, 105)

ax2.axhline(y=80, color="gray", linestyle="--")

ax.set_title(f"{n_80} of {len(by_sku)} SKUs drive 80% of correction cost")
fig.tight_layout()
fig.savefig(PROJECT_DIR / "pareto.png", dpi=150)