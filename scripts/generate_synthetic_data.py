from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample" / "training.csv"
UPLIFT_OUT = ROOT / "data" / "sample" / "uplift.csv"
START = pd.Timestamp("2025-01-01", tz="UTC")
DAYS = 638  # through late September 2026


def _sigmoid(value: float) -> float:
    return float(1 / (1 + np.exp(-value)))


def main(n: int = 12000, uplift_n: int = 8000) -> None:
    actions = ["promote_core_pack", "premium_bundle", "targeted_discount", "sales_visit"]
    action_types = {
        "promote_core_pack": "product_recommendation",
        "premium_bundle": "bundle",
        "targeted_discount": "promotion",
        "sales_visit": "human_followup",
    }
    economics = {
        "promote_core_pack": (9.0, 0.0, 0.25, 310.0, 0.00),
        "premium_bundle": (15.5, 1.5, 0.25, 385.0, 0.00),
        "targeted_discount": (7.5, 2.5, 0.20, 295.0, 0.05),
        "sales_visit": (18.0, 0.0, 4.50, 0.0, 0.00),
    }

    rows = []
    for i in range(n):
        day = int(RNG.integers(0, DAYS))
        event_ts = START + pd.Timedelta(days=day, hours=int(RNG.integers(0, 24)))
        progress = day / DAYS
        action_id = RNG.choice(actions)
        margin, discount, contact, price, risk = economics[action_id]
        affinity = float(np.clip(RNG.beta(4, 2) + 0.05 * progress, 0, 1))
        discount_response = float(np.clip(RNG.beta(2.5, 3) + 0.04 * progress, 0, 1))
        price_sensitivity = float(np.clip(RNG.beta(2, 3) + 0.03 * progress, 0, 1))
        freq = int(RNG.poisson(5 + 0.6 * progress))
        recency = int(RNG.integers(0, 31))
        avg_ticket = float(np.clip(RNG.normal(325 + 25 * progress, 85), 80, 700))
        contact_count = int(RNG.integers(0, 4))
        channel_probs = np.array([0.50 - 0.08 * progress, 0.35, 0.15 + 0.08 * progress])
        channel = RNG.choice(["traditional_trade", "modern_trade", "digital"], p=channel_probs)
        region = RNG.choice(["MX-CENTRAL", "MX-NORTH", "BR-SE", "CO-ANDES"])
        seasonality = 0.14 * np.sin(2 * np.pi * event_ts.dayofyear / 365.25)

        logit = (
            -1.1
            + 2.1 * affinity
            + 1.0 * discount_response * (action_id == "targeted_discount")
            + 0.08 * min(freq, 10)
            - 1.2 * price_sensitivity * (price > avg_ticket)
            - 0.02 * recency
            - 0.22 * contact_count
            + 0.25 * (action_id == "promote_core_pack")
            + seasonality
            - 0.18 * progress * (action_id == "targeted_discount")
        )
        p = _sigmoid(logit)
        response = int(RNG.random() < p)

        rows.append(
            {
                "event_timestamp": event_ts.isoformat(),
                "customer_id": f"C{int(RNG.integers(1, 2501)):05d}",
                "avg_ticket": avg_ticket,
                "purchase_frequency_30d": freq,
                "days_since_last_purchase": recency,
                "category_affinity": affinity,
                "historical_discount_response": discount_response,
                "price_sensitivity": price_sensitivity,
                "contact_count_7d": contact_count,
                "action_expected_margin": margin,
                "action_discount_cost": discount,
                "action_contact_cost": contact,
                "action_price": price,
                "action_risk_penalty": risk,
                "channel": channel,
                "region": region,
                "action_type": action_types[action_id],
                "action_id": action_id,
                "response": response,
            }
        )

    uplift_rows = []
    for i in range(uplift_n):
        day = int(RNG.integers(0, DAYS))
        event_ts = START + pd.Timedelta(days=day)
        affinity = float(RNG.beta(4, 2))
        discount_response = float(RNG.beta(2.5, 3))
        price_sensitivity = float(RNG.beta(2, 3))
        freq = int(RNG.poisson(5))
        avg_ticket = float(np.clip(RNG.normal(335, 90), 80, 700))
        treatment = int(RNG.random() < 0.5)  # randomized synthetic experiment
        base_logit = -1.15 + 1.55 * affinity + 0.06 * min(freq, 10) - 0.75 * price_sensitivity
        treatment_logit_effect = 1.15 * discount_response - 0.55 * price_sensitivity - 0.12
        p0 = _sigmoid(base_logit)
        p1 = _sigmoid(base_logit + treatment_logit_effect)
        response = int(RNG.random() < (p1 if treatment else p0))
        uplift_rows.append(
            {
                "event_timestamp": event_ts.isoformat(),
                "customer_id": f"U{int(RNG.integers(1, 3001)):05d}",
                "avg_ticket": avg_ticket,
                "purchase_frequency_30d": freq,
                "category_affinity": affinity,
                "historical_discount_response": discount_response,
                "price_sensitivity": price_sensitivity,
                "channel": RNG.choice(["traditional_trade", "modern_trade", "digital"]),
                "region": RNG.choice(["MX-CENTRAL", "MX-NORTH", "BR-SE", "CO-ANDES"]),
                "treatment": treatment,
                "response": response,
                "true_uplift": p1 - p0,
            }
        )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).sort_values("event_timestamp").to_csv(OUT, index=False)
    pd.DataFrame(uplift_rows).sort_values("event_timestamp").to_csv(UPLIFT_OUT, index=False)
    print(f"Wrote {n} propensity rows to {OUT}")
    print(f"Wrote {uplift_n} randomized uplift rows to {UPLIFT_OUT}")


if __name__ == "__main__":
    main()
