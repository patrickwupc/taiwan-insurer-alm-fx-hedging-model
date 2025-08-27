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
        self.unhedged_usd_assets_usd = self.usd_assets_usd # Will be adjusted by hedge ratio

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
                                   cost_bps_annual=30.0,
                                   accrue=True):
        

        if self.hedge_ratio == 0:
            total_hedging_cost_twd = 0
            unhedged_notional_usd = self.usd_assets_usd
            # Calculate FX impact on the entire portfolio and return with zero cost
            fx_impact_unhedged_twd = unhedged_notional_usd * (current_twd_usd_spot - previous_twd_usd_spot)
            net_fx_impact_twd = fx_impact_unhedged_twd
            return net_fx_impact_twd, total_hedging_cost_twd

        else:
            # Hedged / unhedged notionals
            hedged_notional_usd = self.usd_assets_usd * hedge_ratio
            unhedged_notional_usd = self.usd_assets_usd * (1 - hedge_ratio)

            # Forward points at entry (market mid)
            forward_points = forward_rate - previous_twd_usd_spot  # TWD per USD

            # execution/credit cost as a haircut on the forward points (annualized bps as 30, reasoning explained in README)
            tenor_fraction = tenor_length_months / 12.0
            cost_points = previous_twd_usd_spot * (cost_bps_annual / 100.0) * tenor_fraction

            # Effective points after cost
            effective_points = forward_points - cost_points  # worse for us

            # Hedging cost booking:
            # - accrue=True: recognize proportionally each step (smooth, simple), i.e if three months
            # foward contract, divide the cost (forward- spot) by three to account the cost monthly/ by step
            # - accrue=False: book full points once (use only on trade date, not every step)
            if accrue:
                hedge_points_present_step = effective_points * (period_length_months / tenor_length_months)
            else:
                hedge_points_present_step = effective_points

            # This period's hedging cost in TWD
            total_hedging_cost_twd = hedged_notional_usd * hedge_points_present_step

            # FX impact on the unhedged portion
            fx_impact_unhedged_twd = unhedged_notional_usd * (current_twd_usd_spot - previous_twd_usd_spot)

            # Net FX impact (unhedged FX + accrued hedge cost)
            net_fx_impact_twd = fx_impact_unhedged_twd + total_hedging_cost_twd
            
            return net_fx_impact_twd, total_hedging_cost_twd
    
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

        # 2 Hedge effect (uses the forward tenor you pass in)
        net_fx_impact_twd, total_hedging_cost_twd = self.apply_hedging_strategy_forward(
            hedge_ratio,
            current_twd_usd_spot, previous_twd_usd_spot,
            forward_rate, tenor_length_months,
            period_length_months=period_length_months,
            cost_bps_annual=cost_bps_annual,
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
                     forward_rate, tenor_length_months):
        
        interest_income_usd, capital_gain_loss_usd = self.calculate_bond_return(
            current_us_bond_yield, previous_us_bond_yield
        )
        total_investment_return_usd = interest_income_usd + capital_gain_loss_usd

        investment_income_twd = total_investment_return_usd * current_twd_usd_spot
        
        # Corrected line: Pass the self.hedge_ratio attribute
        net_fx_impact_twd, total_hedging_cost_twd = self.apply_hedging_strategy_forward(
            hedge_ratio=self.hedge_ratio, # Added the missing argument
            current_twd_usd_spot=current_twd_usd_spot,
            previous_twd_usd_spot=previous_twd_usd_spot,
            forward_rate=forward_rate,
            tenor_length_months=tenor_length_months
        )

    

        total_pnl = investment_income_twd + net_fx_impact_twd
        self.equity += total_pnl

        self.history = pd.concat([self.history, pd.DataFrame([{
            'Date': date,
            'TWD_USD_Spot': current_twd_usd_spot,
            'USD_Assets_TWD': self.usd_assets_usd * current_twd_usd_spot,
            'Net_FX_Impact': net_fx_impact_twd,
            'Hedging_Cost': total_hedging_cost_twd,
            'Investment_Income_TWD': investment_income_twd,
            'Equity': self.equity,
            'FEVR_Balance': self.fevr_balance
        }])], ignore_index=True)
        
        self.usd_assets_usd += total_investment_return_usd





