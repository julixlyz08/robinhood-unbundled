# Robinhood, Unbundled

**Five businesses, one stock: profitability, margins, competitiveness, growth and value by vertical**

*Robinhood Markets, Inc. (NASDAQ: HOOD) · Data through Q2 2026 · Prices as of October 16, 2026 close ($98.87, market cap $88.9B) · Q3 2026 forecast made October 18, 2026*

Julie Loyez · [Interactive dashboard](https://public.tableau.com/app/profile/julie.loyez/viz/RobinhoodUnbundled/RobinhoodUnbundled) · [Code and data](https://github.com/julixlyz08/robinhood-unbundled)

---

## Summary

Robinhood reports revenue by product but profit only for the company as a whole. This note rebuilds the company as five businesses and asks the same five questions of each: does it make money, how much per unit, who does it beat, is it growing, and what is it worth?

| Vertical | Q2 2026 revenue | YoY growth | Est. operating margin | Market-mood share of swings | Value (base case) | Role |
|---|---|---|---|---|---|---|
| Options | $342M | +29% | 45% | 23% | $19.0B | Engine |
| Equities | $129M | +95% | 45% | 35% | $6.4B | Engine, more cyclical |
| Crypto | $100M | −38% | 45% | 41% | $3.4B | Risk |
| Prediction markets | $156M | >10× (company-reported) | 45% | n/a | $10.4B | Option value |
| Subscriptions & Banking | $143M | +54% | 14% | 10% | $4.2B | Glue |

**Six findings:**

1. **Trading growth is all volume.** Robinhood earns about $0.44 per options contract, roughly what it earned two years ago, and 1.35 bps per dollar of stock traded, below early-2024 levels. Revenue rises because customers trade more, and they increasingly trade at Robinhood: its share of options contracts among comparable brokers rose from 50% to 54% in a year.
2. **Each extra trade is almost pure profit.** Direct costs are about 8% of trading revenue. Profitability comes from spreading a fixed platform over more activity.
3. **But operating leverage is fading.** From mid-2024 to Q3 2025, 69–87¢ of every new revenue dollar reached operating profit. In the last three quarters it was 29–55¢, as costs grew 33% a year to fund Rothera, Trump Accounts, international expansion and acquisitions.
4. **Prediction markets are already bigger than crypto** ($156M vs $100M in Q2) after barely a year. Robinhood is the largest broker distributor among those that disclose figures, but most of the economics sit with the exchanges, which is why its own exchange, Rothera, matters.
5. **Bitcoin is the swing factor, not the VIX.** A 30% Bitcoin drop is associated with about $135M less revenue per quarter across options, equities, crypto and Subscriptions & Banking (−19% of their revenue; prediction markets have too little history to test). Crypto is only about a quarter of that hit; options and equities move with it too.
6. **The parts are worth about $57B; the market pays $89B.** Even at the most generous peer multiples, the sum ($82B) falls short of the stock price. The market is paying about $32B for growth and for bets that barely show in revenue yet. Adjusted for growth, though, the price is reasonable: cheaper per point of growth than Interactive Brokers or Coinbase. **The stock is a bet that ~30%+ growth continues.**

![Revenue by line](figures/fig1_revenue_mix.png)

---

## 1. Why unbundle Robinhood?

In Q2 2021, crypto was over half of Robinhood's transaction revenue and the company was widely seen as a meme-stock and crypto trading app. By Q2 2026, crypto was 13% of transaction revenue, and the company had 13 business lines above $100M of annualized revenue. Revenue reached $1.31B in Q2 2026 (+32% YoY), with net income of $573M.

Treating Robinhood as one business hides that its lines behave very differently: they earn different amounts per unit, face different competitors, and react differently to markets. The company's own reporting splits revenue (options, cryptocurrencies, equities, event contracts, other transaction, net interest, other revenues) but not costs. This note fills that gap with an explicit, documented cost allocation.

**Scope.** Five verticals are analyzed. Net interest revenue (margin lending, cash sweep, securities lending; 30% of revenue) and the small "other transaction" line are not analyzed as verticals, but they are carried through the profit allocation and the valuation so the parts always add up to the whole company.

---

## 2. Options: the engine

**Profitability.** Options are Robinhood's largest line: $342M in Q2 2026, 26% of revenue. After direct transaction costs, the contribution margin is about 92%; after its share of platform costs, the estimated operating margin is 45% ($154M of operating profit), the largest profit pool among the five verticals (net interest, not analyzed here, is larger).

**Margins.** Robinhood earns about **$0.44 per contract**, within a $0.44–0.52 band since 2024. The take rate has drifted down from a 2025 peak of $0.51, possibly reflecting a mix shift toward more active, lower-priced traders.

**Competitiveness.** Contracts traded grew **+50%** year over year, against +17% at Interactive Brokers and +68% at Webull (from a much smaller base). Across the three, Robinhood's share rose from 50% to 54%.

**Growth.** Revenue +29% on volume +50%: growth is entirely more trading, partly offset by revenue per contract falling 14% from its Q2 2025 peak.

**Quality.** 64% of the swings in options revenue are explained by steady growth, only 23% by market mood. Options are steadier than their reputation.

**Verdict: engine.** The biggest, most profitable and steadiest of the trading lines, gaining share.

![Take rates](figures/fig2_take_rates.png)

---

## 3. Equities: the engine with a cyclical streak

**Profitability.** $129M in Q2 2026, estimated 45% operating margin ($58M).

**Margins.** About **1.35 bps** of notional traded ($13.50 per $100,000 traded), down from 1.7 bps in early 2024 but stable since mid-2024.

**Competitiveness.** Notional traded grew **+85%**, ahead of Webull (+73%) and of trade-count growth at Schwab (+57%) and Interactive Brokers (+36%). Robinhood is the fastest-growing large equity broker.

**Growth.** Revenue +95% on notional +85%: the fastest-growing of the established trading lines, with a small take-rate tailwind.

**Quality.** Only 39% of swings are steady growth; 35% is market mood. Equities move with risk appetite more than options do.

**Verdict: engine, but cyclical.** Strong share gains, but this line will fall hardest outside crypto when sentiment turns.

---

## 4. Crypto: the risk

**Profitability.** $100M in Q2 2026 (−38% YoY), estimated 45% operating margin (41–45% across scenarios).

**Margins.** The reported blended take rate fell from about 55 to 20–25 bps after the Bitstamp acquisition (June 2025). That is a mix effect, not a price cut. Solving two quarters together, the **retail app earns about 55 bps** while **Bitstamp (institutional) earns about 0.5 bps**. The blended number mostly tracks how much volume goes through each.

**Competitiveness.** Retail volume fell 36%, in line with Coinbase's consumer volume (−38%): Robinhood is holding share in a down market. It does so as the low-price option: Coinbase earns about **175 bps** on consumer volume, three times Robinhood. Bitstamp's $22B of quarterly volume is still small next to Coinbase's $121B institutional volume.

**Growth.** Negative, and driven by the market: volume −36%, revenue −38%.

**Quality.** The least predictable line: 41% of its swings are market mood and 32% unexplained; only 27% is steady growth. Revenue moves 1.3× the Bitcoin price in percentage terms.

**Verdict: risk.** Still profitable, but the line most exposed to the crypto cycle, and its pricing advantage vs Coinbase is also a ceiling on its economics.

![Profitability](figures/fig3_margins.png)

---

## 5. Prediction markets: the option value

**Profitability.** $156M in Q2 2026, up more than 10× year over year according to Robinhood, already larger than crypto. Estimated 45% operating margin, though this is the least certain number in the model: Robinhood began reporting event-contract revenue separately only in Q2 2026.

**Margins.** About **1.1¢ per contract** on 13.6 billion contracts traded in Q2: tiny bets at enormous scale.

**Competitiveness.** At roughly $624M annualized, Robinhood's prediction-market revenue is about **6× Coinbase's** ("$100M+"). But the exchanges keep most of the economics: Kalshi, which supplies many brokers' contracts, has a reported run-rate above $4B, and Polymarket above $1B (press reports, not filings). Kalshi was valued at $22B in its last closed round (reportedly in talks at $40B); Polymarket at $21B. In June 2026, Robinhood launched **Rothera**, a CFTC-licensed exchange and clearinghouse run through a joint venture with Susquehanna. Owning the venue, not just the customer, is how Robinhood could capture more of each contract.

**Growth.** The fastest-growing line by far, with the widest range in the Q3 forecast ($159–215M).

**Quality.** Too new to estimate; one quarter of clean data. Regulatory risk is real: state attorneys general have argued that prediction markets are illegal gambling (New York sued Coinbase and Gemini in 2026).

**Verdict: option value, and the swing factor in the valuation.** If the market is right about Robinhood's price, it is largely betting on this line (see Section 9).

---

## 6. Subscriptions & Banking: the glue

**Profitability.** $143M in Q2 2026 (+54%) of "other revenues": Robinhood Gold subscriptions, Trump Account services, the Gold Card and Banking. It is the least profitable vertical: estimated **14%** operating margin ($20M), 10–20% across scenarios. The main reason is $56M of credit-loss provisions, almost all from the Gold Card. Part of the card's income (interest) is booked in net interest, so the true margin is somewhat higher; moving $25M a quarter of card income back raises it to about 20%.

**Margins.** About **$119 of other revenue per Gold subscriber per year**, compared with $67–106 during 2025, helped in Q2 2026 by Trump Account service revenues.

**Competitiveness.** Gold subscribers grew **+37%** to 4.8M; about 40% of new funded customers sign up for Gold. Other revenues grew +54%, faster than SoFi's financial-services revenue (+29%) and Coinbase's subscription and services revenue (−12%). Banking reached over $3B of deposits from 240,000 customers; the Gold Card passed $100M of annualized revenue.

**Quality.** The steadiest line: 60% steady growth, only 10% market mood.

**Verdict: glue, not profit.** Its value is in what it does for the rest of the platform: it brings customers in, keeps them, and keeps their assets on Robinhood, where they trade.

![Competitiveness](figures/fig4_competition.png)

---

## 7. The company: profitable, but buying its growth

Robinhood's operating margin was 44% in Q2 2026, essentially unchanged from 44% a year earlier, despite revenue growing 32%. Costs grew 33% over the same period. The incremental margin (the share of each new revenue dollar that reaches operating profit, year over year, excluding named one-off items) fell from 69–87% between mid-2024 and Q3 2025 to 55%, 29% and 50% in the last three quarters.

This is a choice, not a failure: the spending funds Rothera, Trump Accounts (over 7 million sign-ups and nearly $1.5B deposited since July 4, 2026), international expansion (Singapore license in July 2026, WonderFi), and acquisitions (Bitstamp, TradePMR). Whether that spending pays back is the central question for the stock.

---

## 8. Revenue quality: Bitcoin is the swing factor

Each line's quarterly revenue since the 2021 IPO was regressed on a time trend, the VIX (market fear) and the Bitcoin price. The result splits each line's ups and downs into steady growth, market mood and other factors.

- The **VIX is not statistically significant for any of the four verticals tested**; **Bitcoin is significant for every one**, including options and equities. Bitcoin seems to work as a gauge of retail risk appetite.
- If Bitcoin falls 30%, options, equities, crypto and Subscriptions & Banking lose about **$135M of quarterly revenue (−19% of their combined revenue)**: options −$49M, crypto −$37M, equities −$30M, Subscriptions & Banking −$19M.
- **Subscriptions & Banking is the steadiest line and crypto the least.** Total company revenue is steadier than any trading line alone, because net interest moves differently.

![Revenue quality](figures/fig5_revenue_quality.png)

---

## 9. Valuation: what is the market paying for?

Each vertical was valued at the enterprise value / next-year revenue multiple of its closest listed peers, applied to FY2027 revenue (the $6.85B analyst consensus, split by this note's forecast mix).

| Line | FY2027 revenue | Multiple, low–base–high | Peers | Value, base |
|---|---|---|---|---|
| Options | $1.9B | 4.1×–9.9×–15.8× | Schwab – Interactive Brokers | $19.0B |
| Equities | $0.6B | 4.1×–9.9×–15.8× | Schwab – Interactive Brokers | $6.4B |
| Crypto | $0.5B | 5.0×–6.2×–7.5× | Coinbase ±20% | $3.4B |
| Prediction markets | $0.9B | 5.5×–11.6×–14.6× | Kalshi round – exchange average – CME | $10.4B |
| Subscriptions & Banking | $0.8B | 3.1×–5.5×–8.0× | SoFi – subscription premium (judgment) | $4.2B |
| Other transaction (not analyzed) | $0.2B | 4.1×–9.9×–15.8× | Schwab – Interactive Brokers | $2.3B |
| Net interest (not analyzed) | $1.9B | 3.1×–4.1×–6.0× | SoFi – Schwab – judgment | $7.6B |
| Net cash | | | | $3.2B |
| **Sum of the parts** | | | | **$57B (range $30–82B)** |
| **Market cap, Oct 16, 2026** | | | | **$88.9B** |

![Valuation](figures/fig6_sotp.png)

**What it means.**

- **Even with every line at its most generous peer multiple, the parts add up to less than the stock price.** The market is not valuing Robinhood as a collection of brokers, a crypto exchange and a bank. It is paying about $32B above the base case for growth and optionality.
- **Put the entire premium on prediction markets** and the market implies about **48× revenue, or ~$43B**, for that line alone: roughly twice Kalshi's last valuation, for a business that has mostly distributed Kalshi's contracts.
- **Adjusted for growth, the price looks reasonable.** Robinhood trades at 12.5× forward revenue with about 39% expected revenue growth (trailing twelve months to FY2027 consensus): 0.32× per point of growth, cheaper than Interactive Brokers (0.60×), Coinbase (0.40×), ICE (0.86×) and CME (1.61×), and dearer than Schwab (0.23×) and SoFi (0.07×).

**The stock is priced as a bet that ~30%+ growth continues.** If growth slows to an incumbent broker's pace, the sum of the parts is the more relevant anchor.

---

## 10. Q3 2026 forecast (made before the October 27 report)

Revenue for each vertical = monthly activity (July and August from Robinhood's monthly releases; September scaled up from the September 1–24 release) × the latest take rate. Ranges come from the method's own error in a nine-quarter backtest (options 3.8% average error, equities 7.5%).

| Vertical | Q2 2026 actual | Q3 2026 forecast | Range |
|---|---|---|---|
| Options | $342M | $400M | $385–415M |
| Equities | $129M | $135M | $125–145M |
| Crypto | $100M | $114M | $103–125M |
| Prediction markets | $156M | $187M | $159–215M |
| Subscriptions & Banking | $143M | $158M | $143–171M |
| Other transaction + net interest (held near Q2, ±5%) | $438M | $438M | $417–459M |
| **Total net revenue** | **$1,308M** | **$1,432M** | **$1,332–1,530M** |

![Q3 forecast](figures/fig7_q3_forecast.png)

*Scoring against reported results: to be added after October 27, 2026.*

---

## 11. Personal thesis

*To be written.*

---

## 12. Risks to this analysis

- **Cost allocation is an estimate.** Robinhood does not disclose costs by product. Shared costs are allocated by revenue, so the trading lines' operating margins are similar by construction; scenarios test the main alternatives.
- **Short history.** Volumes were first disclosed in 2024, prediction-market revenue in Q2 2026, and the regressions use 21 quarters.
- **Subscriptions & Banking is understated**, because part of the Gold Card's and Banking's income is booked in net interest.
- **Peer multiples move.** The valuation is a snapshot at the October 16, 2026 close; the subscription multiple and the Kalshi revenue figure are the weakest inputs.
- **Regulation.** Prediction markets and crypto both face open regulatory questions in the US.

---

## Methodology

- **Data.** 21 quarters (Q2 2021–Q2 2026) from Robinhood's earnings releases (SEC 8-K Exhibit 99.1 and investors.robinhood.com), every quarter reconciled to reported totals; monthly operating data releases for April–September 2026; competitor earnings releases and filings; VIX and Bitcoin prices from Yahoo Finance; valuation inputs at the October 16, 2026 close.
- **Take rates.** Revenue ÷ volume per vertical. Crypto's app and Bitstamp rates are solved jointly from Q1 and Q2 2026.
- **Profit per vertical.** Brokerage and transaction costs are allocated to transaction lines by revenue (scenario: double weight on crypto and prediction markets); credit-loss provisions to Subscriptions & Banking; technology, operations, marketing and G&A to all lines by revenue (scenario: 1.5× marketing weight on Subscriptions & Banking). A scenario also moves $25M a quarter of card income from net interest. The allocated pieces always sum to reported operating income.
- **Revenue quality.** Log-log regressions of quarterly revenue on a time trend, average VIX and average Bitcoin price; "steady growth" is the R² of the trend-only model, "market mood" the R² added by VIX and Bitcoin.
- **Valuation.** EV / FY2027 revenue multiples of listed peers; FY2027 revenue from consensus, split by forecast mix; net cash of $3.16B (cash minus the 2029 convertible notes).

All code, data and assumptions: [github.com/julixlyz08/robinhood-unbundled](https://github.com/julixlyz08/robinhood-unbundled).

*This note is an independent analytical project, not investment advice.*
