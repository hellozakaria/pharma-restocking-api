import pandas as pd
import oracledb

DB_USER = "sys"
DB_PASSWORD = "XXXXXX"  # Replace with your actual password
DB_SERVICE = "FREEPDB1"

DB_HOST = "localhost"
DB_PORT = "1521"
CSV_FILE_PATH = "salesdaily.csv"

def load_data_to_oracle():
    print("Loading CSV Data...")
    df = pd.read_csv(CSV_FILE_PATH)
    df['datum'] = pd.to_datetime(df['datum'])
    
    # We explicitly tell Pandas to only keep these 9 columns, ignoring the extra ones
    columns_to_keep = ['datum', 'M01AB', 'M01AE', 'N02BA', 'N02BE', 'N05B', 'N05C', 'R03', 'R06']
    df = df[columns_to_keep]

    df = df.where(pd.notnull(df), None)
    data_to_insert = [tuple(x) for x in df.to_numpy()]

    print("Connecting to Oracle Database...")
    try:
        dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
        
        # Notice mode=oracledb.SYSDBA is here because you are using the 'sys' user!
        connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn, mode=oracledb.SYSDBA)
        cursor = connection.cursor()

        print("Inserting data into PHARMA_SALES table... This might take a minute.")
        insert_sql = """
            INSERT INTO PHARMA_SALES (SALE_DATE, M01AB, M01AE, N02BA, N02BE, N05B, N05C, R03, R06)
            VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
        """
        cursor.executemany(insert_sql, data_to_insert)
        connection.commit()
        print(f"Success! {cursor.rowcount} rows inserted into Oracle.")

    except oracledb.Error as e:
        print(f"An error occurred with Oracle: {e}")
    except Exception as e:
        print(f"A general error occurred: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'connection' in locals(): connection.close()
        print("Database connection closed.")

if __name__ == "__main__":
    load_data_to_oracle()