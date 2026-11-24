WITH corrections AS (
    SELECT sku, SUM(billed_charge - expected_charge) AS correction
    FROM read_csv_auto('data/shipments.csv')
    GROUP BY sku
),
ranked AS (
    SELECT
        sku,
        correction,
        SUM(correction) OVER (ORDER BY correction DESC, sku
                              ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
            / SUM(correction) OVER () AS cum_pct
    FROM corrections
)
SELECT
    (SELECT COUNT(*) FROM ranked WHERE cum_pct < 0.5) + 1 AS n_50,
    (SELECT COUNT(*) FROM ranked WHERE cum_pct < 0.8) + 1 AS n_80,
    (SELECT COUNT(*) FROM ranked) AS total_skus;