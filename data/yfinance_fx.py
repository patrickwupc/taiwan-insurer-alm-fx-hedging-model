## using yfinance api to scrape forex data

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def fetch_forex_data(pair, start_date, end_date):
    """
    Fetch historical forex data for a given currency pair.
    
    :param pair: Currency pair (e.g., 'EURUSD=X')
    :param start_date: Start date in 'YYYY-MM-DD' format
    :param end_date: End date in 'YYYY-MM-DD' format
    :return: DataFrame with forex data
    """
    df = yf.download(pair, start=start_date, end=end_date)
    if df.empty:
        raise ValueError(f"No data found for {pair} between {start_date} and {end_date}")
    
    df.reset_index(inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def fetch_bond_etf_data(etf, start_date, end_date):
    """
    Fetch historical bond ETF data for a given ETF.
    
    :param etf: Bond ETF ticker (e.g., 'LQD')
    :param start_date: Start date in 'YYYY-MM-DD' format
    :param end_date: End date in 'YYYY-MM-DD' format
    :return: DataFrame with bond ETF data
    """
    df = yf.download(etf, start=start_date, end=end_date)
    if df.empty:
        raise ValueError(f"No data found for {etf} between {start_date} and {end_date}")
    
    df.reset_index(inplace=True)
    df["Date"] = pd.to_datetime(df["Date"])
    return df

# Example usage
lqd_data = fetch_bond_etf_data('LQD', '2021-01-01', '2025-07-31')
print(lqd_data)

