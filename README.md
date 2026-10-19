# Robinhood, Unbundled

**A sell-side-style research note that breaks Robinhood (NASDAQ: HOOD) into its business lines and asks of each: does it make money, how much per unit, who does it beat, is it growing, and is it worth owning?**

---

**Read the research note:** [markdown](note/robinhood_unbundled.md) · [PDF](note/robinhood_unbundled.pdf) · [Interactive dashboard](https://public.tableau.com/app/profile/julie.loyez/viz/RobinhoodUnbundled/RobinhoodUnbundled)

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
| *Other transaction + net interest (not analyzed, held near Q2 ±5%)* | $438M | $438M | $417–459M |
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

### Step 5: Competitiveness (Q2 2026 vs Q2 2025)
Only like-for-like metrics are compared (full table in `outputs/competitive_scorecard.csv`).

| Vertical | Robinhood | Rivals | Verdict |
|---|---|---|---|
| Options | contracts +50% | IBKR +17%, Webull +68% (smaller base) | **Gaining share**: 50% → 54% of contracts across the three |
| Equities | notional +85% | Webull +73%; trade counts: Schwab +57%, IBKR +36% | **Gaining share**, growing fastest among the large brokers |
| Crypto | retail volume −36%; take rate ~55 bps | Coinbase retail volume −38%; take rate ~175 bps | **Holding share** in a down market, as the *cheap* option: about a third of Coinbase's price per dollar traded. Bitstamp ($22B) is still small next to Coinbase institutional ($121B) |
| Prediction markets | ~$624M annualized revenue | Coinbase "$100M+"; Kalshi ~$4B run-rate and Polymarket "$1B+" (press reports) | **Leading broker distributor**, about 6× Coinbase. The exchanges capture far more of the economics, which is exactly why Robinhood launched its own (Rothera) |
| Subscriptions & Banking | Gold +37%, other revenues +54% | SoFi members +35%, financial-services revenue +29% | **Growing faster than SoFi** on revenue, from a smaller base |

The "so what": in trading, Robinhood wins on **price and product breadth, not on margin per trade**. Its growth comes from taking activity away from competitors. In prediction markets, its real upside depends on moving from *distributor* to *exchange owner*.

### Step 6: Revenue quality (2021Q2–2026Q2)
For each vertical, quarterly revenue was regressed on a time trend, the VIX (market fear) and the Bitcoin price, all in logs. The fit splits each line's ups and downs into steady growth, market mood, and other factors:

| Line | Steady growth | Market mood | Other (launches, one-offs) |
|---|---|---|---|
| Options | 64% | 23% | 13% |
| Equities | 39% | 35% | 26% |
| Crypto | 27% | 41% | 32% |
| Subscriptions & Banking | 60% | 10% | 30% |

What it means:
- **Bitcoin, not the VIX, is the market indicator that moves with every line**, including options and equities. It works as a gauge of retail risk appetite.
- **Subscriptions & Banking is the steadiest revenue**, and options are steadier than they look. Crypto is the least predictable.
- Caveats: 21 quarters is a short history, the trend is fitted before market mood (so the split depends on that order), and net interest is driven by interest rates, which aren't in the model.

### Step 6b: Trading-volume stress test (`src/volume_stress.py`)
What happens if customers trade less? Starting from Q2 2026, trading volume is lowered across all trading lines at constant take rates. Transaction costs (8% of transaction revenue) fall with volume; all other costs ($672M a quarter), Subscriptions & Banking and net interest stay fixed.

| Scenario | Revenue | Operating profit | Operating margin |
|---|---|---|---|
| Q2 2026 actual | $1,308M | $574M | 44% |
| Volume −10% | −6% | −12% | 41% |
| Volume −20% | −12% | −25% | 37% |
| Volume −30% | −18% | −37% | 33% |
| Volume −50% | −30% | −62% | 24% |
| 2022 replay (options −31%, equities −60%, crypto −52%) | −23% | −48% | 30% |

What it means:
- **Profit falls about 2.1× as fast as revenue**: operating leverage in reverse.
- At −30% volume, each trading vertical's operating margin falls from about 45% to about 25%; Subscriptions & Banking is untouched.
- **Break-even is far away**: operating profit reaches zero only if volume falls about 80% with no cost cuts.
- The test is generous on two points: Gold revenue fell in 2022, and the margin book shrinks when trading slows; both are held constant.

### Step 7: Sum-of-the-parts valuation (prices at Oct 16, 2026 close)
Each vertical is valued at its closest listed peers' enterprise value ÷ next-year revenue. FY2027 revenue uses the analyst consensus ($6.85B), split by our forecast mix.

| Line | FY27 revenue | Multiple (low–base–high) | Value, base |
|---|---|---|---|
| Options | $1.9B | 4.1–10.0–15.8× (Schwab–IBKR) | $19B |
| Equities | $0.7B | same | $6B |
| Crypto | $0.6B | 5.0–6.2–7.5× (Coinbase) | $3B |
| Prediction markets | $0.9B | 5.5–11.6–14.6× (Kalshi round–exchanges–CME) | $10B |
| Subscriptions & Banking | $0.8B | 3.1–5.5–8.0× (SoFi–judgment) | $4B |
| Net interest + other transaction | $2.1B | | $10B |
| Net cash | | | $3B |
| **Sum of parts** | | | **$30B / $57B / $82B** |
| **Market cap** | | | **$89B ($98.87/share)** |

The "so what":
- **Even with every vertical at its *most generous* peer multiple, the parts add up to less than the stock price.** The market isn't valuing Robinhood as a collection of brokers, a crypto exchange and a bank. It is paying about **$32B above the base case for growth and for things that barely show up in revenue yet**: Rothera, international expansion, Trump Accounts, tokenization.
- Put the whole premium on prediction markets and the market implies about **48× revenue, or ~$43B, for that vertical alone**. That's about twice Kalshi's last private valuation, for a business that is mostly a *distributor* of Kalshi's contracts.
- **Adjusted for growth, it looks reasonable.** Robinhood trades at 12.5× forward revenue with about 39% expected growth, roughly 0.32× per growth point. That's cheaper than IBKR (0.60), Coinbase (0.40) and the exchanges, and dearer than Schwab (0.23) and SoFi (0.07). **The stock is a bet that ~30%+ growth continues.**
- Full tables are in `outputs/sotp.csv` and `outputs/growth_adjusted_multiples.csv`.

## Data sources

- Robinhood quarterly earnings releases (investors.robinhood.com, SEC 8-K Exhibit 99.1)
- Robinhood monthly operating data releases
- Competitor earnings releases and filings
- Market data for the revenue-quality regressions (VIX, Bitcoin, market volume)

## Units used throughout

Dollars in **$ millions** unless a column name says otherwise (`_b` = billions, `_m` = millions). Quarters are written `2026Q2`.
