import pandas as pd
import numpy as np
from src.bond_utils import bond_price_calc, weighted_cash_flow_calc, daily_interest_income_calc, macaulay_duration_calc

class Insurer:
    def __init__(self, name, total_assets_twd, foreign_asset_ratio, usd_denom_ratio,
                 initial_twd_usd_spot, initial_us_bond_yield, initial_twd_equity,
                 initial_fevr_balance, liability_duration=None, bond_duration=None):
        
        ## instruments: long-duration investment grade corporate bonds, 
        
        self.name = name
        self.total_assets_twd = total_assets_twd

        # 70 percent 
        self.foreign_asset_ratio = foreign_asset_ratio # e.g., 0.70 for 70%
        self.usd_denom_ratio = usd_denom_ratio # e.g., 0.95 for 95% of foreign assets in USD
        self.initial_twd_usd_spot = initial_twd_usd_spot     # Initial TWD/USD spot rate
        self.initial_us_bond_yield = initial_us_bond_yield  # Initial US bond yield (annualized, 0.045 for 4.5%)
        self.equity = initial_twd_equity        # Initial equity in TWD ( 2.5 trillion TWD)
        self.fevr_balance = initial_fevr_balance          # Initial FEVR balance in TWD (220 billion TWD)
        self.liability_duration = liability_duration # Optional, for ALM discussions
        self.bond_duration = bond_duration # For capital gains/losses on bonds

        # Derived initial values
        self.foreign_assets_twd = self.total_assets_twd * self.foreign_asset_ratio
        self.usd_assets_usd = self.foreign_assets_twd * self.usd_denom_ratio / self.initial_twd_usd_spot
        self.unhedged_usd_assets_usd = self.usd_assets_usd # Will be adjusted by hedge ratio

        # To store historical performance
        self.history = pd.DataFrame(columns=['Date', 'TWD_USD_Spot', 'USD_Assets_TWD',
                                             'Net_FX_Impact', 'Hedging_Cost', 'Pre_Tax_Profit',
                                             'Equity', 'FEVR_Balance'])
    
    def apply_hedging_strategy(self, hedge_ratio, current_twd_usd_spot, previous_twd_usd_spot):
        pass
    
    def simulate_month(self, date, current_twd_usd_spot, previous_twd_usd_spot,
                       current_us_bond_yield, previous_us_bond_yield,
                       us_short_rate, tw_short_rate, hedge_ratio):
        pass

    def simulate_day(self, date, current_twd_usd_spot, previous_twd_usd_spot,
                     current_us_bond_yield, previous_us_bond_yield,
                     fwd_point_for_period, hedge_ratio):
        pass # Implement this last for simulation




