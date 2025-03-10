import requests
import pandas as pd
from datetime import datetime
import logging
import os
import pathlib

# Configure basic logging
logger = logging.getLogger(__name__)

def get_data_filename(symbol, base_currency, interval, start_date, days):
    """
    Generate a standardized filename including start date.
    
    Parameters:
        start_date (datetime): The user-defined start date.
    
    Returns:
        str: Filename for the data
    """
    start_date_str = start_date.strftime('%Y-%m-%d')  # Format as YYYY-MM-DD
    return f"data/prices/{symbol}_{base_currency}_{interval}_{start_date_str}_{days}days.csv"


def fetch_crypto_data(symbol='BTC', base_currency='USDT', interval='hour', start_date=None, use_cache=True):
    """
    Fetch historical cryptocurrency price data from CryptoCompare API starting from a user-defined date.
    
    Parameters:
        start_date (datetime): The specific starting date for fetching data.
    """
    end_date = datetime.utcnow()
    days = (end_date - start_date).days  # Calculate days from start_date to today

    # Set seconds per period based on interval
    if interval.lower() == 'hour':
        seconds_per_period = 3600  # one hour
        limit = min(days * 24, 2000)  # maximum number of hours (data points)
        url = "https://min-api.cryptocompare.com/data/v2/histohour"
    else:
        seconds_per_period = 86400  # one day
        limit = min(days, 2000)      # maximum number of days (data points)
        url = "https://min-api.cryptocompare.com/data/v2/histoday"

    # Generate filename using start_date
    filename = get_data_filename(symbol, base_currency, interval, start_date, days)
    
    if use_cache and os.path.exists(filename):
        try:
            logger.info(f"Loading cached data from {filename}")
            return pd.read_csv(filename, parse_dates=['timestamp'])
        except Exception as e:
            logger.warning(f"Failed to load cached data: {str(e)}")

    try:
        # Convert start_date to Unix timestamp
        from_timestamp = int(start_date.timestamp())

        # Calculate the target timestamp based on the correct period multiplier
        toTs = from_timestamp + (limit * seconds_per_period)

        # Set API parameters
        params = {
            'fsym': symbol,
            'tsym': base_currency,
            'limit': limit,
            'toTs': toTs
        }

        logger.info(f"Fetching {symbol}/{base_currency} {interval}ly data from {start_date.strftime('%Y-%m-%d')}...")
        response = requests.get(url, params=params, timeout=10)
        data = response.json()

        if data.get('Response') != 'Success':
            error_msg = data.get('Message', 'Unknown error')
            logger.error(f"API error: {error_msg}")
            return None

        # Convert API response to DataFrame
        raw_data = data['Data']['Data']
        df = pd.DataFrame(raw_data)
        df['timestamp'] = pd.to_datetime(df['time'], unit='s')

        # Rename and filter relevant columns
        df = df.rename(columns={'time': 'unix_time', 'volumefrom': 'volume'})
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

def get_crypto_data(symbol='BTC', base_currency='USDT', interval='hour', day=1, month=1, year=2019):
    """
    Get cryptocurrency data starting from a specific date (day, month, year).
    
    Parameters:
        day (int): Start day
        month (int): Start month
        year (int): Start year
    
    Returns:
        DataFrame or None: Processed price data
    """
    start_date = datetime(year, month, day)  # Convert inputs to datetime
    end_date = datetime.utcnow()  # Current date
    days = (end_date - start_date).days  # Calculate total days

    if days < 0:
        logger.error("Start date cannot be in the future.")
        return None

    filename = get_data_filename(symbol, base_currency, interval, start_date, days)

    # Try to load from cache first
    if os.path.exists(filename):
        try:
            logger.info(f"Loading cached data from {filename}")
            data = pd.read_csv(filename, parse_dates=['timestamp'])
            return data
        except Exception as e:
            logger.warning(f"Failed to load cached data: {str(e)}")

    # Fetch from API if no cache
    data = fetch_crypto_data(symbol, base_currency, interval, start_date, use_cache=False)

    # Save to CSV if data is available
    if data is not None:
        save_to_csv(data, filename)
    else:
        logger.error("Failed to fetch data.")

    return data
