# Some documentaiton on the calculations and methodologies

## Hedging Cost “Haircut”
In addition to the forward points (forward – spot), hedging carries an inherent cost often referred to as a haircut. This reflects frictions in executing forward contracts:
1. Bid–Ask Spread
- Banks quote a bid/ask for FX forwards.
- For USD–TWD, spreads are usually tight (a few tenths of a pip for large institutions, wider for smaller clients).
- On an annualized basis, this translates to roughly 5–20 bps (0.05%–0.20%).

2. Balance Sheet / Credit Charge (CVA/FVA)
- Dealers also pass through funding and credit-related costs.
- These typically add another 10–30 bps per year for smaller or less liquid counterparties.

-> A conservative estimate is to apply a ~0.3% (30 bps annualized) haircut to the forward points when modeling hedging costs.