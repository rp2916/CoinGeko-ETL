import os
import requests
import psycopg2
from datetime import datetime, timedelta

# 1. EXTRACT: Get free data (Example: CoinGecko Crypto Price)
def extract():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    return requests.get(url).json()['bitcoin']['usd']

# 2. LOAD & TEMP STORAGE (Keep only 4 days)
def load_to_postgres(price):
    conn = psycopg2.connect("YOUR_CONNECTION_STRING_HERE")
    cur = conn.cursor()
    
    # Create table if not exists
    cur.execute("CREATE TABLE IF NOT EXISTS crypto_temps (price FLOAT, created_at TIMESTAMP);")
    
    # Insert new data
    cur.execute("INSERT INTO crypto_temps (price, created_at) VALUES (%s, %s)", (price, datetime.now()))
    
    # DELETE data older than 4 days (Your "Temp Checking" requirement)
    four_days_ago = datetime.now() - timedelta(days=4)
    cur.execute("DELETE FROM crypto_temps WHERE created_at < %s", (four_days_ago,))
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    data = extract()
    load_to_postgres(data)