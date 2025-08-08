# Calculate the forward rate for different periods using interest rate parity formula 
import pandas as pd
import numpy as np

def calculate_forward_rate(row, period_year):
    """
    Calculates forward FX rate using Interest Rate Parity (IRP):

        F = S * ((1 + r_base * T) / (1 + r_price * T))

    Parameters:
    - row: DataFrame row with 'spot', 'rate_us', and 'rate_tw'
    - period_year: time period in years (e.g., 0.25 for 3M)

    Returns:
    - Forward FX rate
    """
    if pd.notna(row['rate_us']) and pd.notna(row['rate_tw']):
        rate_base= row['rate_us'] / 100
        rate_price = row['rate_tw'] / 100
        
        return row['spot'] * ((1 + rate_base*period_year) / (1 + rate_price*period_year)) 
    
    else:
        return np.nan
    
# Calculate the forward point from the forward rate and spot rate    
def forward_point(foward, spot):
    return (foward - spot) * 100

