import pandas as pd
import oracledb
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import warnings

# Suppress the Pandas SQLAlchemy warning to keep our terminal clean
warnings.filterwarnings('ignore', category=UserWarning)

# DATABASE CREDENTIALS
DB_USER = "sys"
DB_PASSWORD = "XXXXXX"  # Replace with your actual password
DB_SERVICE = "FREEPDB1"
DB_HOST = "localhost"
DB_PORT = "1521"

def fetch_data_and_train():
    print("1. Connecting to Oracle to fetch historical data...")
    dsn = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE}"
    connection = oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=dsn, mode=oracledb.SYSDBA)
    
    # We write a SQL query to get the Date and the sales for ONE drug category (M01AB)
    query = "SELECT SALE_DATE, M01AB FROM PHARMA_SALES ORDER BY SALE_DATE"
    
    # We told Pandas to run this SQL query and put the results into a DataFrame called 'df'
    df = pd.read_sql(query, con=connection)
    connection.close()
    
    print(f"Data fetched successfully! {len(df)} rows loaded.\n")

    # --- FEATURE ENGINEERING (Preparing data for the ML Model) ---
    print("2. Preparing data for Machine Learning...")
    # ML models don't understand "Dates", they understand numbers. 
    # So we break the date into Year, Month, and Day.
    df['SALE_DATE'] = pd.to_datetime(df['SALE_DATE'])
    df['Year'] = df['SALE_DATE'].dt.year
    df['Month'] = df['SALE_DATE'].dt.month
    df['Day'] = df['SALE_DATE'].dt.day
    df['DayOfWeek'] = df['SALE_DATE'].dt.dayofweek

    # 'X' is the data we use to predict (Features: Year, Month, Day)
    # 'y' is what we are trying to predict (Target: M01AB Sales)
    X = df[['Year', 'Month', 'Day', 'DayOfWeek']]
    y = df['M01AB']

    # We split our data: 80% to train the model, 20% to test it (Standard ML practice)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    # --- MACHINE LEARNING ---
    print("3. Training the Random Forest Regression Model...")
    # Random Forest is great for this because it can learn seasonal patterns (like higher sales in winter)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    print("4. Testing the Model...")
    predictions = model.predict(X_test)
    
    # Evaluate how wrong our model is on average (Mean Absolute Error)
    mae = mean_absolute_error(y_test, predictions)
    print(f"\n*** MODEL RESULTS ***")
    print(f"Mean Absolute Error (MAE): {mae:.2f}")
    print("This means our model's prediction is usually off by about {:.2f} boxes of medicine per day.".format(mae))

    print("\n5. Saving the trained model for the API...")
    # This saves the trained 'brain' to a file so our API can use it later
    joblib.dump(model, 'rf_model_m01ab.joblib')
    print("Model saved successfully as 'rf_model_m01ab.joblib'!")

if __name__ == "__main__":
    fetch_data_and_train()