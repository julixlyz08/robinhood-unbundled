"""
Step 4: estimated profit and margin per vertical.

Robinhood reports profit only for the whole company, so we estimate it per vertical
by assigning each cost line with a stated rule (a "driver"):

  Direct costs (caused by a specific vertical)
    - Brokerage & transaction (clearing, exchange, network fees) -> transaction verticals,
      in proportion to their revenue (weights vary by scenario)
    - Provision for credit losses (mostly the Gold Card)          -> Subscriptions & Banking

  Shared platform costs (tech, operations, marketing, G&A)
    -> every revenue line, in proportion to its revenue
       (scenario "subs_heavy" tilts marketing toward Subscriptions & Banking,
        because Gold promotions and the Gold Card drive a lot of acquisition spend)

Net interest and "other transaction" revenue are not analyzed as verticals, but they
still carry their share of costs, otherwise the five verticals would absorb costs that
belong to them.

Known bias, handled as a scenario: some Gold Card income (card interest) is booked in
net interest, not in other revenues, so Subscriptions & Banking looks worse than it is.
Robinhood says its credit card business is >$100M of annualized revenue (~$25M/quarter);
scenario "card_adjusted" moves up to that amount from net interest to the vertical.

Run:  python src/vertical_pnl.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
q = pd.read_csv(ROOT / "data/processed/quarters.csv").set_index("quarter")
OUT = ROOT / "data/processed"

VERTICALS = ["Options", "Equities", "Crypto", "Prediction markets", "Subscriptions & Banking"]
NOT_ANALYZED = ["Other transaction", "Net interest"]
TRANSACTION = ["Options", "Equities", "Crypto", "Prediction markets", "Other transaction"]


def revenue_lines(r, card_shift=0.0):
    return {
        "Options": r.options_rev, "Equities": r.equities_rev, "Crypto": r.crypto_rev,
        "Prediction markets": r.event_contracts_rev,
        "Subscriptions & Banking": r.other_rev + card_shift,
        "Other transaction": r.other_transaction_rev,
        "Net interest": r.net_interest_rev - card_shift,
    }


SCENARIOS = {
    # brokerage weight per transaction vertical, marketing tilt to Subs & Banking, card shift ($M)
    "base":          ({"Crypto": 1.0, "Prediction markets": 1.0}, 1.0, 0.0),
    "costly_new":    ({"Crypto": 2.0, "Prediction markets": 2.0}, 1.0, 0.0),   # new products carry more fees
    "subs_heavy":    ({"Crypto": 1.0, "Prediction markets": 1.0}, 1.5, 0.0),   # Gold drives acquisition spend
    "card_adjusted": ({"Crypto": 1.0, "Prediction markets": 1.0}, 1.0, 25.0),  # card income moved out of NII
}


def pnl(quarter, scenario="base"):
    r = q.loc[quarter]
    weights, mkt_tilt, card = SCENARIOS[scenario]
    rev = revenue_lines(r, card)
    total = sum(rev.values())

    # Direct: brokerage & transaction, by weighted transaction revenue
    w = {k: rev[k] * weights.get(k, 1.0) for k in TRANSACTION}
    brokerage = {k: r.brokerage_transaction_exp * w.get(k, 0) / sum(w.values()) for k in rev}
    credit = {k: (r.credit_loss_exp if k == "Subscriptions & Banking" else 0.0) for k in rev}

    # Shared: tech, operations, G&A by revenue share; marketing optionally tilted
    shared_ex_mkt = r.tech_dev_exp + r.operations_exp + r.g_and_a_exp
    mw = {k: rev[k] * (mkt_tilt if k == "Subscriptions & Banking" else 1.0) for k in rev}
    shared = {k: shared_ex_mkt * rev[k] / total + r.marketing_exp * mw[k] / sum(mw.values()) for k in rev}

    rows = []
    for k in rev:
        contribution = rev[k] - brokerage[k] - credit[k]
        op = contribution - shared[k]
        rows.append({"quarter": quarter, "scenario": scenario, "line": k, "revenue": rev[k],
                     "direct_costs": brokerage[k] + credit[k], "contribution": contribution,
                     "shared_costs": shared[k], "operating_profit": op,
                     "contribution_margin": contribution / rev[k], "operating_margin": op / rev[k]})
    df = pd.DataFrame(rows)
    # Sanity: the pieces must add back to the company's reported operating income
    reported_op = r.total_net_rev - r.total_opex
    assert abs(df.operating_profit.sum() - reported_op) < 0.5, (quarter, scenario)
    return df


if __name__ == "__main__":
    all_rows = pd.concat([pnl("2026Q2", s) for s in SCENARIOS], ignore_index=True)
    all_rows.to_csv(OUT / "vertical_pnl.csv", index=False)

    base = all_rows[all_rows.scenario == "base"].set_index("line")
    rng = all_rows.groupby("line").operating_margin.agg(["min", "max"])
    summary = base[["revenue", "direct_costs", "contribution", "contribution_margin",
                    "shared_costs", "operating_profit", "operating_margin"]].join(rng)
    summary = summary.loc[VERTICALS + NOT_ANALYZED]
    summary.to_csv(OUT / "vertical_pnl_summary_2026q2.csv")

    pd.set_option("display.width", 200)
    fmt = summary.copy()
    for c in ["contribution_margin", "operating_margin", "min", "max"]:
        fmt[c] = (fmt[c] * 100).round(1).astype(str) + "%"
    print("Q2 2026 estimated P&L by line ($M), base scenario; min/max = operating margin across scenarios")
    print(fmt.round(1).to_string())
    r = q.loc["2026Q2"]
    print(f"\nCompany operating margin Q2 2026: {(r.total_net_rev - r.total_opex) / r.total_net_rev:.1%}")

    # Operating leverage: of each extra revenue dollar vs a year ago, how much reached operating profit?
    # One-off expense items named in the releases (positive = charge, negative = benefit),
    # removed so the trend reflects the running business rather than accounting events.
    one_offs = {"2023Q1": 485,   # cancelled 2021 founders' stock award
                "2023Q3": 104,   # regulatory accrual
                "2024Q3": 10,    # regulatory accrual
                "2024Q4": -55,   # reversal of a regulatory accrual
                "2026Q2": 23}    # restructuring
    q["one_off"] = pd.Series(one_offs).reindex(q.index).fillna(0)
    q["op_income"] = q.total_net_rev - q.total_opex
    q["op_income_adj"] = q.op_income + q.one_off
    yoy = q[["total_net_rev", "op_income", "op_income_adj", "total_opex"]].diff(4).dropna()
    yoy["incremental_margin"] = yoy.op_income / yoy.total_net_rev
    yoy["incremental_margin_adj"] = yoy.op_income_adj / yoy.total_net_rev
    yoy.to_csv(OUT / "incremental_margin.csv")
    print("\nIncremental margin (change in operating income / change in revenue, vs same quarter last year):")
    print(yoy.loc["2024Q2":].round(2).to_string())
