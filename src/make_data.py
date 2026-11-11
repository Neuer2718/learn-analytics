"""Generate a fake parcel-shipment dataset for Pareto practice.

Each row is one parcel. Most parcels are billed exactly what was expected.
SKUs with bad dimensional data in the item master get "dim corrections":
the carrier re-measures the box and bills more. A small group of SKUs
with badly wrong dimensions causes most of the correction cost.

Run from the project folder:  python src/make_data.py
"""

from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42          # fixed seed -> same data every run
N_SKUS = 500
N_PARCELS = 20_000
OUT_PATH = Path(__file__).resolve().parent.parent / "data" / "shipments.csv"


def make_skus(rng):
    """Build one row per SKU with its shipping profile."""
    skus = pd.DataFrame({"sku": [f"SKU-{i:05d}" for i in range(10001, 10001 + N_SKUS)]})

    # Popularity is skewed: a few SKUs ship far more often than others.
    skus["popularity"] = rng.lognormal(mean=0, sigma=1.0, size=N_SKUS)

    # Normal parcel cost per SKU, roughly $6 to $40.
    skus["base_charge"] = rng.uniform(6, 40, size=N_SKUS).round(2)

    # Item-master data quality: most good, some slightly off, a few badly off.
    quality = rng.choice(["good", "minor", "bad"], size=N_SKUS, p=[0.75, 0.18, 0.07])
    skus["error_rate"] = np.select(
        [quality == "good", quality == "minor", quality == "bad"],
        [0.01, rng.uniform(0.15, 0.40, N_SKUS), rng.uniform(0.70, 0.95, N_SKUS)],
    )
    skus["error_size"] = np.select(  # typical overcharge as a fraction of base cost
        [quality == "good", quality == "minor", quality == "bad"],
        [0.10, rng.uniform(0.10, 0.30, N_SKUS), rng.uniform(0.60, 1.50, N_SKUS)],
    )
    return skus


def make_parcels(rng, skus):
    """Sample parcels from the SKU list and compute billed vs. expected charges."""
    weights = skus["popularity"] / skus["popularity"].sum()
    idx = rng.choice(len(skus), size=N_PARCELS, p=weights)
    p = skus.iloc[idx].reset_index(drop=True)

    carriers = rng.choice(["Carrier A", "Carrier B", "Carrier C"], size=N_PARCELS, p=[0.5, 0.35, 0.15])
    carrier_mult = pd.Series(carriers).map({"Carrier A": 1.00, "Carrier B": 0.95, "Carrier C": 1.10})

    start = np.datetime64("2026-01-05")
    ship_date = start + rng.integers(0, 182, size=N_PARCELS).astype("timedelta64[D]")

    # Small per-parcel variation around the SKU's base charge.
    expected = (p["base_charge"] * carrier_mult * rng.normal(1.0, 0.05, N_PARCELS)).round(2)

    corrected = rng.random(N_PARCELS) < p["error_rate"]
    overcharge = expected * p["error_size"] * rng.uniform(0.5, 1.5, N_PARCELS)
    billed = (expected + np.where(corrected, overcharge, 0.0)).round(2)

    return pd.DataFrame({
        "sku": p["sku"],
        "carrier": carriers,
        "ship_date": ship_date,
        "billed_charge": billed,
        "expected_charge": expected,
    }).sort_values("ship_date", ignore_index=True)


def main():
    rng = np.random.default_rng(SEED)
    parcels = make_parcels(rng, make_skus(rng))
    OUT_PATH.parent.mkdir(exist_ok=True)
    parcels.to_csv(OUT_PATH, index=False)
    print(f"Wrote {len(parcels):,} parcels for {parcels['sku'].nunique()} SKUs to {OUT_PATH}")


if __name__ == "__main__":
    main()
