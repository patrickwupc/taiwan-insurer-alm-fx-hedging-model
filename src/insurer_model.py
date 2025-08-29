import pandas as pd
import numpy as np
from src.bond_utils import bond_price_calc, weighted_cash_flow_calc, daily_interest_income_calc, macaulay_duration_calc

class Insurer:
    def __init__(self, name, total_assets_twd, foreign_asset_ratio, usd_denom_ratio,
                 initial_twd_usd_spot, initial_us_bond_yield, initial_twd_equity,
                 initial_fevr_balance, liability_duration=None, bond_duration=None, hedge_ratio = None):
        
        ## instruments: long-duration investment grade corporate bonds, 
        self.name = name
        self.total_assets_twd = total_assets_twd

        self.foreign_asset_ratio = foreign_asset_ratio # e.g., 0.70 for 70%
        self.usd_denom_ratio = usd_denom_ratio # e.g., 0.95 for 95% of foreign assets in USD
        self.initial_twd_usd_spot = initial_twd_usd_spot     # Initial TWD/USD spot rate
        self.initial_us_bond_yield = initial_us_bond_yield  # Initial US bond yield (annualized, 0.045 for 4.5%)
        self.equity = initial_twd_equity        # Initial equity in TWD ( 2.5 trillion TWD)
        self.fevr_balance = initial_fevr_balance          # Initial FEVR balance in TWD (220 billion TWD)
        self.liability_duration = liability_duration # Optional, for ALM discussions
        self.bond_duration = bond_duration # For capital gains/losses on bonds
        self.hedge_ratio = hedge_ratio

        # Derived initial values
        self.foreign_assets_twd = self.total_assets_twd * self.foreign_asset_ratio
        self.usd_assets_usd = self.foreign_assets_twd * self.usd_denom_ratio / self.initial_twd_usd_spot
        self.unhedged_usd_assets_usd = self.usd_assets_usd  # Will be adjusted by hedge ratio

        # To store historical performance, for ananlysis and visulization
        self.history = pd.DataFrame(columns=['Date', 'TWD_USD_Spot', 'USD_Assets_TWD',
                                             'Net_FX_Impact', 'Hedging_Cost', 'Pre_Tax_Profit',
                                             'Equity', 'FEVR_Balance'])
    
    def calculate_bond_return(self, current_us_bond_yield, previous_us_bond_yield):
        # Implement bond interest income and capital gains/losses based on duration
        # For simplicity, let's assume a fixed annual interest income and then capital gain/loss
        interest_income_usd = self.usd_assets_usd * (self.initial_us_bond_yield / 12) # Monthly income
        
        # Capital gain/loss based on duration (simplified)
        # Price change = -Macaulay Duration * (Change in Yield) * Initial Price
        # Assuming initial price is 1 (par) for yield calculations
        yield_change = current_us_bond_yield - previous_us_bond_yield
        capital_gain_loss_usd = -self.usd_assets_usd * self.bond_duration * yield_change
        
        return interest_income_usd, capital_gain_loss_usd

    def apply_hedging_strategy_forward(self, hedge_ratio,
                                   current_twd_usd_spot, previous_twd_usd_spot,
                                   forward_rate, tenor_length_months,
                                   period_length_months = 1,
                                   previous_forward_rate = None,
                                   accrue=True,
                                   cost_bps_annual = 30.0, 
                                   impact_k_bps = 20 ):
        
        usd_notional = self.usd_assets_usd
        if hedge_ratio <= 0 or usd_notional == 0:
            fx_unhedged_twd = usd_notional * (current_twd_usd_spot - previous_twd_usd_spot)
            return fx_unhedged_twd, {
                'fx_unhedged_twd': fx_unhedged_twd,
                'hedge_carry_twd': 0.0, 'hedge_mtm_twd': 0.0,
                'exec_linear_twd': 0.0, 'exec_convex_twd': 0.0,
                'hedged_notional_usd': 0.0
            }


        # notionals
        hedged_usd  = usd_notional * hedge_ratio
        unhedged_usd = usd_notional * (1 - hedge_ratio)

        tenor_years = tenor_length_months / 12.0
        step_frac  = period_length_months / float(tenor_length_months)

        # 1) Unhedged FX
        fx_unhedged_twd = unhedged_usd * (current_twd_usd_spot - previous_twd_usd_spot)

        # 2) Carry (points over tenor: (F/S - 1)*S). For a short USD forward, carry is NEGATIVE if F>S.
        carry_points_step = (forward_rate / previous_twd_usd_spot - 1.0) * previous_twd_usd_spot * step_frac
        hedge_carry_twd   = -hedged_usd * carry_points_step

        # 3) Forward MTM from curve shift (optional; book when you pass previous_forward_rate)
        hedge_mtm_twd = 0.0
        if previous_forward_rate is not None:
            hedge_mtm_twd = - hedged_usd * (forward_rate - previous_forward_rate)

        # 4) Execution/credit COST (linear bps per year) — NEGATIVE
        linear_points_tenor = previous_twd_usd_spot * (cost_bps_annual / 100.0) * tenor_years
        exec_linear_twd = - hedged_usd * (linear_points_tenor * (step_frac if accrue else 1.0))

        # 5) Convex impact COST (in bps, convex in hedge ratio) — NEGATIVE
        # impact bps at full hedge times hr^2, applied per year on notional, then scaled to step
        impact_bps = impact_k_bps * (hedge_ratio ** 2)
        impact_points_tenor = previous_twd_usd_spot * (impact_bps / 10000.0) * tenor_years
        exec_convex_twd = - hedged_usd * (impact_points_tenor * (step_frac if accrue else 1.0))

        # Assemble this step’s hedge+FX effect
        net_fx_impact_twd = (
            fx_unhedged_twd + hedge_carry_twd + hedge_mtm_twd + exec_linear_twd + exec_convex_twd
        )

        components = {
            'fx_unhedged_twd': fx_unhedged_twd,
            'hedge_carry_twd': hedge_carry_twd,
            'hedge_mtm_twd':   hedge_mtm_twd,
            'exec_linear_twd': exec_linear_twd,
            'exec_convex_twd': exec_convex_twd,
            'hedged_notional_usd': hedged_usd
        }
        return net_fx_impact_twd, components
    
    def simulate_month_forward(self, date,
                           current_twd_usd_spot, previous_twd_usd_spot,
                           current_us_bond_yield, previous_us_bond_yield,
                           hedge_ratio,
                           forward_rate,          
                           tenor_length_months,  
                           period_length_months=1,
                           cost_bps_annual=30.0,
                           accrue=True):
        
        # 1 USD bond return
        interest_income_usd, capital_gain_loss_usd = self.calculate_bond_return(
            current_us_bond_yield, previous_us_bond_yield
        )
        total_investment_return_usd = interest_income_usd + capital_gain_loss_usd

        # Convert that USD P&L to TWD at current spot (simple assumption)
        investment_income_twd = total_investment_return_usd * current_twd_usd_spot

        # 2 Hedge effect (uses the forward tenor as arguments
        net_fx_impact_twd, total_hedging_cost_twd = self.apply_hedging_strategy_forward(
            hedge_ratio,
            current_twd_usd_spot, previous_twd_usd_spot,
            forward_rate, tenor_length_months,
            period_length_months=period_length_months,
            cost_bps_annual=cost_bps_annual,
            previous_forward_rate=None,
            accrue=accrue
        )

        # 3 Putting together investment income, fx impact to form P#L
        total_pnl_from_foreign_assets = investment_income_twd + net_fx_impact_twd

        ## Bring in domestic income and opex estimates (scraping balance sheets, next step)
      
        # Update equity; defer FEVR mechanics (we just log the balance)
        self.equity += total_pnl_from_foreign_assets

        # Log row
        self.history = pd.concat([self.history, pd.DataFrame([{
            'Date': date,
            'TWD_USD_Spot': current_twd_usd_spot,
            'USD_Assets_TWD': self.usd_assets_usd * current_twd_usd_spot,
            'Net_FX_Impact': net_fx_impact_twd,
            'Hedging_Cost': total_hedging_cost_twd,
            'Investment_Income_TWD': investment_income_twd,
            'Equity': self.equity,
            'FEVR_Balance': self.fevr_balance  # placeholder; real update later
        }])], ignore_index=True)

        return investment_income_twd, net_fx_impact_twd, total_hedging_cost_twd

    def simulate_day(self, date, current_twd_usd_spot, previous_twd_usd_spot,
                 current_us_bond_yield, previous_us_bond_yield,
                 forward_rate, tenor_length_months, 
                 previous_forward_rate=None):  ## implementin Mark to Market mechanic

        interest_income_usd, capital_gain_loss_usd = self.calculate_bond_return(
            current_us_bond_yield, previous_us_bond_yield
        )
        investment_income_twd = (interest_income_usd + capital_gain_loss_usd) * current_twd_usd_spot

        # Base hedge accrual/cost
        net_fx_impact_twd, components = self.apply_hedging_strategy_forward(
            hedge_ratio=self.hedge_ratio,
            current_twd_usd_spot=current_twd_usd_spot,
            previous_twd_usd_spot=previous_twd_usd_spot,
            forward_rate=forward_rate,
            previous_forward_rate=previous_forward_rate,
            tenor_length_months=tenor_length_months
        )

        # Total hedging cost components (negative values)
        hedging_cost_twd = -(components['exec_linear_twd'] + components['exec_convex_twd'] ) # positive 

        # NEW: forward MTM from curve shift (simple proxy)
        total_pnl = investment_income_twd + net_fx_impact_twd
        self.equity += total_pnl

        self.history = pd.concat([self.history, pd.DataFrame([{
            'Date': date,
            'TWD_USD_Spot': current_twd_usd_spot,
            'USD_Assets_TWD': self.usd_assets_usd * current_twd_usd_spot,
            'Net_FX_Impact': net_fx_impact_twd,
            'Hedging_Cost': hedging_cost_twd,
            'Investment_Income_TWD': investment_income_twd,
            'Equity': self.equity,
            'FEVR_Balance': self.fevr_balance
        }])], ignore_index=True)

        # optional: keep USD assets compounding
        self.usd_assets_usd += (interest_income_usd + capital_gain_loss_usd)

        return investment_income_twd, net_fx_impact_twd, hedging_cost_twd



def run_simulation(insurer, df_data, forward_col, tenor_length_months):
    previous_twd_usd_spot   = df_data.iloc[0]['spot']
    previous_us_bond_yield  = df_data.iloc[0]['yield_10Y']
    previous_forward_rate   = df_data.iloc[0].get(forward_col, previous_twd_usd_spot)

    for index, row in df_data.iterrows():
        current_twd_usd_spot  = row['spot']
        current_us_bond_yield = row['yield_10Y']
        current_forward_rate  = row.get(forward_col, current_twd_usd_spot)
        

        insurer.simulate_day(
            date=index,
            current_twd_usd_spot=current_twd_usd_spot,
            previous_twd_usd_spot=previous_twd_usd_spot,
            current_us_bond_yield=current_us_bond_yield,
            previous_us_bond_yield=previous_us_bond_yield,
            forward_rate=current_forward_rate,
            previous_forward_rate = previous_forward_rate, # NEW
            tenor_length_months=tenor_length_months
        )
        previous_twd_usd_spot  = current_twd_usd_spot
        previous_us_bond_yield = current_us_bond_yield
        previous_forward_rate  = current_forward_rate

    return insurer.history
