# Robinhood, Unbundled

**A sell-side-style research note that breaks Robinhood (NASDAQ: HOOD) into its business lines and asks of each: does it make money, how much per unit, who does it beat, is it growing, and is it worth owning?**

---

## The problem this project solves

Robinhood reports *revenue* by product (options, equities, crypto, event contracts, other), but it reports profit for the company as a whole. Nobody outside the company can download "options operating margin" or "how profitable are prediction markets."

So the core of this project is an **estimated profit-and-loss statement for each vertical**, built from public numbers and a clearly stated set of cost-allocation rules. Every estimate is shown as a range, and every rule is written down so a reader can disagree with a specific assumption instead of the whole model.

## The five verticals

| Vertical | Revenue line it maps to | Volume driver |
|---|---|---|
| Options | Options revenue | Options contracts traded |
| Equities | Equities revenue | Equity notional volume |
| Crypto | Cryptocurrencies revenue (Robinhood app + Bitstamp) | Crypto notional volume |
| Prediction markets | Event contracts revenue | Event contracts traded |
| Subscriptions & Banking | Other revenues (Gold, Trump Accounts services, Gold Card, Banking) | Gold subscribers, funded customers |

**Deliberately left out:** net interest revenue (margin lending, cash sweep, securities lending) and the small "other transaction-based" line (futures and other products). They still appear in the valuation as single unanalyzed lines, so the parts add up to the whole company.

**Known limitation:** some Gold Card and Banking economics (interest earned on card balances, interest on banking deposits) are booked in net interest, not in other revenues. The Subscriptions & Banking vertical therefore *understates* that business's full revenue. The note says so wherever it matters.

## Each vertical gets the same five questions

1. **Profitability:** estimated contribution profit after allocated costs
2. **Margins:** revenue earned per unit of activity (the "take rate")
3. **Competitiveness:** that take rate and growth against the relevant rival
4. **Growth:** split into *more activity* vs *more revenue per unit of activity*
5. **Thesis:** a one-paragraph verdict, labeled as engine, cash cow, option value, or risk

## The layers that go past "so what?"

- **Vertical P&L:** estimated profit per vertical (above)
- **Revenue quality score:** how much of each vertical's revenue moves with market hype (VIX, Bitcoin price, market volume) vs grows on its own
- **Sum-of-the-parts valuation:** a peer multiple per vertical, totaled and compared to Robinhood's actual market value. What is the market paying for?
- **Live forecast:** a published Q3 2026 revenue forecast per vertical, made *before* Robinhood reports on **October 27, 2026**, then scored against the actual results

## Project steps (and where to find each one)

| Step | What happens | Output |
|---|---|---|
| 1. Data collection | Pull revenue, costs, volumes and customer metrics from every quarterly earnings release since the 2021 IPO | `data/raw/`, `data/processed/quarters.csv` |
| 2. Take rates | Revenue ÷ volume for each vertical, each quarter | `data/processed/take_rates.csv` |
| 3. Q3 2026 forecast | Monthly volumes for Jul–Sep 2026 × recent take rates | `outputs/q3_2026_forecast.csv` |
| 4. Vertical P&L | Allocate each cost line to verticals using stated drivers | `data/processed/vertical_pnl.csv` |
| 5. Competitors | Same metrics for Schwab, Interactive Brokers, Coinbase, Kalshi, SoFi | `data/processed/competitors.csv` |
| 6. Revenue quality | Regressions of vertical revenue on market conditions | `outputs/revenue_quality.csv` |
| 7. Valuation | Sum-of-the-parts vs market cap | `outputs/sotp.csv` |
| 8. The note | Written research note + one-page summary | `note/` |
| 9. Tableau | Vertical scorecard dashboard | Tableau Public |

## Progress log

### Step 1–2: Data and take rates (done Oct 18, 2026)
- 21 quarters (2021Q2–2026Q2) collected from Robinhood's own earnings releases. Every quarter reconciles to the reported revenue and expense totals.
- Trading volumes first appear in Q1 2024 releases, so take rates start there.
- Before 2025 Robinhood didn't print an "other transaction" revenue line; it is filled in as the gap between named products and the transaction total (flagged in `other_transaction_derived`).
- **Options** take rate has stayed in a narrow $0.44–0.52 per contract: options growth is almost entirely *more trading*, not *higher pricing*.
- **Crypto** blended take rate fell from ~55 to ~20–25 bps after Bitstamp joined. That isn't a price cut. Solving two quarters together gives about **55 bps on the retail app vs 0.5 bps on Bitstamp**, so the blended number mostly tracks the mix of the two.
- **Prediction markets** revenue is reported on its own only from Q2 2026: about 1.1¢ per contract.
- The credit-loss provision (mostly the Gold Card) only became its own expense line from Q4 2024. Earlier it sits inside other lines.

### Step 3: Q3 2026 forecast (made Oct 18, 2026, before the Oct 27 report)
Method: monthly activity for Jul–Aug, plus September scaled up from the Sep 1–24 release, multiplied by the latest take rate. Ranges come from the method's own historical error.

| Vertical | Q2 2026 actual | Q3 2026 forecast (base) | Range |
|---|---|---|---|
| Options | $342M | $400M | $385–415M |
| Equities | $129M | $135M | $125–145M |
| Crypto | $100M | $114M | $103–125M |
| Prediction markets | $156M | $187M | $159–215M |
| Subscriptions & Banking | $143M | $158M | $143–171M |
| *Other transaction + net interest (not analyzed, held flat)* | $438M | $438M | |
| **Total net revenue** | **$1,308M** | **$1,432M** | **$1,332–1,530M** |

How trustworthy is this? The method was backtested over nine quarters: options were off by **3.8%** on average and equities by **7.5%**. The September scale-up was tested on September 2025 and landed within about 1% of the actual numbers. Prediction markets and Subscriptions & Banking have the least history and the widest ranges.

### Step 4: Profit per vertical (Q2 2026)
Costs are split into **direct** costs, which a vertical causes, and **shared** platform costs, which are split by revenue. Two margins come out of that:

| Line | Revenue | Contribution margin | Operating margin (base) | Range across scenarios |
|---|---|---|---|---|
| Options | $342M | 92% | 45% | 45–47% |
| Equities | $129M | 92% | 45% | 45–47% |
| Crypto | $100M | 92% | 45% | 41–45% |
| Prediction markets | $156M | 92% | 45% | 41–45% |
| Subscriptions & Banking | $143M | 61% | 14% | 10–20% |
| *Net interest (not analyzed)* | $389M | 100% | 53% | |
| **Company** | **$1,308M** | | **44%** | |

What it means:
- **The trading verticals cost almost nothing at the margin.** Direct costs are about 8% of revenue, so each extra trade is nearly pure profit. Profitability comes from spreading a fixed platform over more activity.
- **Subscriptions & Banking is the least profitable vertical today**, mainly because of Gold Card credit losses ($56M). Even after moving card interest income back from net interest, it reaches only about 20%. It works as an acquisition and retention engine: about 40% of new customers sign up for Gold.
- **The fully-loaded margins of the trading verticals are almost identical by construction**, because shared costs are split by revenue. Robinhood doesn't disclose anything that would let anyone separate them further, so they aren't presented as more precise than that.

**Operating leverage is fading.** Incremental margin is the change in operating profit divided by the change in revenue, year over year, with one-off items removed:

| | 2024Q2–2025Q3 | 2025Q4 | 2026Q1 | 2026Q2 |
|---|---|---|---|---|
| Share of each new revenue $ reaching operating profit | 69–87¢ | 55¢ | 29¢ | 50¢ |

Costs are now growing about 33% a year as Robinhood funds its own exchange (Rothera), Trump Accounts, international expansion and acquisitions. Whether that spending pays off is central to the thesis.

Scenarios (in `src/vertical_pnl.py`):
- **base**: shared costs split by revenue
- **costly_new**: crypto and prediction markets carry double the transaction costs
- **subs_heavy**: 1.5× marketing weight on Subscriptions & Banking
- **card_adjusted**: $25M a quarter of card income moved from net interest to Subscriptions & Banking

## Data sources

- Robinhood quarterly earnings releases (investors.robinhood.com, SEC 8-K Exhibit 99.1)
- Robinhood monthly operating data releases
- Competitor earnings releases and filings
- Market data for the revenue-quality regressions (VIX, Bitcoin, market volume)

## Units used throughout

Dollars in **$ millions** unless a column name says otherwise (`_b` = billions, `_m` = millions). Quarters are written `2026Q2`.
