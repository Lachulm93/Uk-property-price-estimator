import os
import urllib.request
import duckdb

DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "properties.duckdb")
CSV_URL = "http://prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-monthly-update-new-version.csv"
RAW_CSV_PATH = os.path.join(DATA_DIR, "raw_monthly.csv")

COLUMN_NAMES = [
    "transaction_id",
    "price",
    "transfer_date",
    "postcode",
    "property_type",
    "is_new_build",
    "tenure",
    "paon",
    "saon",
    "street",
    "locality",
    "town_city",
    "district",
    "county",
    "ppd_category",
    "record_status"
]

def download_data():
    """Downloads the latest monthly property sales records from HM Land Registry."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(RAW_CSV_PATH):
        print("Downloading HM Land Registry data (this takes ~10-15 seconds)...")
        urllib.request.urlretrieve(CSV_URL, RAW_CSV_PATH)
        print(f"Data saved to {RAW_CSV_PATH}")
    else:
        print("Data file already exists. Skipping download.")

def build_database():
    """Loads the raw CSV safely into DuckDB."""
    print("Connecting to DuckDB...")
    con = duckdb.connect(DB_PATH)

    print("Importing and cleaning data...")
    # Load directly using duckdb.read_csv with explicit column names
    df_view = con.read_csv(
        RAW_CSV_PATH,
        header=False,
        names=COLUMN_NAMES
    )

    # Filter out empty postcodes or nonsensical transactions (< £10,000)
    con.execute("""
        CREATE OR REPLACE TABLE sales AS 
        SELECT 
            transaction_id,
            CAST(price AS INTEGER) AS price,
            CAST(transfer_date AS TIMESTAMP) AS transfer_date,
            postcode,
            property_type,
            is_new_build,
            tenure,
            town_city,
            district,
            county
        FROM df_view
        WHERE price > 10000 
          AND postcode IS NOT NULL;
    """)

    # Verification query
    stats = con.execute("""
        SELECT 
            COUNT(*), 
            ROUND(AVG(price), 0),
            MIN(price),
            MAX(price)
        FROM sales;
    """).fetchone()

    print("\n--- DATABASE BUILT SUCCESSFULLY ---")
    print(f"Total Transactions: {stats[0]:,}")
    print(f"Average Price:      £{stats[1]:,.0f}")
    print(f"Min Price:          £{stats[2]:,}")
    print(f"Max Price:          £{stats[3]:,}\n")

    con.close()

if __name__ == "__main__":
    download_data()
    build_database()