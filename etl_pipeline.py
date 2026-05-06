import os
import requests
import psycopg2
import pandas as pd
from datetime import datetime, timedelta

def run_etl():
    # 1. GET DATA
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
    price = requests.get(url).json()['bitcoin']['usd']
    now = datetime.now()

    # 2. SAVE TO DATABASE (Supabase)
    db_url = os.getenv('DB_URL')
    conn = psycopg2.connect(db_url,sslmode='require')
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS crypto (price FLOAT, time TIMESTAMP);")
    cur.execute("INSERT INTO crypto (price, time) VALUES (%s, %s)", (price, now))
    
    # Keep only 4 days of data
    cur.execute("DELETE FROM crypto WHERE time < %s", (now - timedelta(days=4),))
    
    # 3. SAVE TO CSV (For Tableau)
    # We pull the last 4 days from the DB to make a clean file
    cur.execute("SELECT * FROM crypto ORDER BY time DESC")
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=['price', 'time'])
    df.to_csv("data_for_tableau.csv", index=False)
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    run_etl()