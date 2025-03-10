import requests
import pandas as pd
from datetime import datetime
import logging
import os
import pathlib

# Configure basic logging
logger = logging.getLogger(__name__)

def get_data_filename(symbol, base_currency, interval, days):
    """
    Generate a standardized filename based on the parameters.
    
    Returns:
        str: Filename for the data
    """
    return f"data/prices/{symbol}_{base_currency}_{interval}_{days}days.csv"

def fetch_crypto_data(symbol='BTC', base_currency='USDT', interval='hour', days=30, use_cache=True):
    """
    Fetch historical cryptocurrency price data from CryptoCompare API.
    Checks local cache first if use_cache is True.
    
    Parameters:
        symbol (str): Crypto symbol (default: 'BTC')
        base_currency (str): Base currency (default: 'USDT')
        interval (str): 'hour' or 'day' for timeframe
        days (int): How many days of data to fetch
        use_cache (bool): Whether to check local files first
        
    Returns:
        DataFrame or None: Processed price data or None if fetch fails
    """
    # Check if we should and can use cached data
    if use_cache:
        filename = get_data_filename(symbol, base_currency, interval, days)
        if os.path.exists(filename):
            try:
                logger.info(f"Loading cached data from {filename}")
                return pd.read_csv(filename, parse_dates=['timestamp'])
            except Exception as e:
                logger.warning(f"Failed to load cached data: {str(e)}")
    
    try:
        # Select the appropriate endpoint based on interval
        if interval.lower() == 'hour':
            url = "https://min-api.cryptocompare.com/data/v2/histohour"
            limit = min(days * 24, 2000)  # API limit is 2000
        else:
            url = "https://min-api.cryptocompare.com/data/v2/histoday"
            limit = min(days, 2000)
        
        # Set up parameters
        params = {
            'fsym': symbol,
            'tsym': base_currency,
            'limit': limit
        }
        
        logger.info(f"Fetching {symbol}/{base_currency} {interval}ly data...")
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('Response') != 'Success':
            error_msg = data.get('Message', 'Unknown error')
            logger.error(f"API error: {error_msg}")
            return None
            
        # Process data into DataFrame
        raw_data = data['Data']['Data']
        df = pd.DataFrame(raw_data)
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['time'], unit='s')
        
        # Rename and select columns
        df = df.rename(columns={
            'time': 'unix_time',
            'volumefrom': 'volume'
        })
        
        result_df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        logger.info(f"Successfully fetched {len(result_df)} records")
        
        return result_df
        
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        return None

def save_to_csv(df, filename=None, symbol=None, base_currency=None, interval=None, days=None):
    """
    Save DataFrame to CSV file.
    
    Can specify either a direct filename or parameters to generate filename.
    """
    if df is None:
        return False
        
    # If parameters are provided but no filename, generate one
    if filename is None and symbol is not None:
        filename = get_data_filename(symbol, base_currency, interval, days)
    
    # Create directory if it doesn't exist
    pathlib.Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
    
    df.to_csv(filename, index=False)
    logger.info(f"Data saved to {filename}")
    return True

def get_crypto_data(symbol='BTC', base_currency='USDT', interval='hour', days=30):
    """
    Get cryptocurrency data, first trying local cache then API.
    
    Returns:
        DataFrame or None: Processed price data or None if fetch fails
    """
    filename = get_data_filename(symbol, base_currency, interval, days)
    
    # Try to load from cache first
    if os.path.exists(filename):
        try:
            logger.info(f"Loading cached data from {filename}")
            data = pd.read_csv(filename, parse_dates=['timestamp'])
            if data is not None:
                logger.info(f"Data retrieved successfully with {len(data)} records")

            return data
        except Exception as e:
            logger.warning(f"Failed to load cached data: {str(e)}")
    
    # If no cache or cache loading failed, fetch from API
    data = fetch_crypto_data(symbol, base_currency, interval, days, use_cache=False)
    
    # Save the data if fetched successfully
    if data is not None:
        save_to_csv(data, filename)
    else:
        logger.error("Failed to fetch Bitcoin price data")
    
    return data