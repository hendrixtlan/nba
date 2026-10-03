from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RNG = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample" / "training.csv"


def main(n: int = 6000) -> None:
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
        action_id = RNG.choice(actions)
        margin, discount, contact, price, risk = economics[action_id]
        affinity = RNG.beta(4, 2)
        discount_response = RNG.beta(2.5, 3)
        price_sensitivity = RNG.beta(2, 3)
        freq = int(RNG.poisson(5))
        recency = int(RNG.integers(0, 31))
        avg_ticket = float(np.clip(RNG.normal(330, 85), 80, 700))
        contact_count = int(RNG.integers(0, 4))
        channel = RNG.choice(["traditional_trade", "modern_trade", "digital"])
        region = RNG.choice(["MX-CENTRAL", "MX-NORTH", "BR-SE", "CO-ANDES"])

        logit = (
            -1.1
            + 2.1 * affinity
            + 1.0 * discount_response * (action_id == "targeted_discount")
            + 0.08 * min(freq, 10)
            - 1.2 * price_sensitivity * (price > avg_ticket)
            - 0.02 * recency
            - 0.22 * contact_count
            + 0.25 * (action_id == "promote_core_pack")
        )
        p = 1 / (1 + np.exp(-logit))
        response = int(RNG.random() < p)

        rows.append(
            {
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

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"Wrote {n} rows to {OUT}")


if __name__ == "__main__":
    main()
