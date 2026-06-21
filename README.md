# Medication Demand Prediction and Restocking API

## Context
Efficient inventory management is a major challenge in the pharmaceutical sector. Poor anticipation of demand can lead to stock shortages or overstocking. This project is a predictive service capable of analyzing historical pharmacy data to estimate future medication demand and generate restocking recommendations via an API.

## Project Architecture
1. **Database:** Oracle Database (storing 6 years of historical pharmacy POS data).
2. **Machine Learning:** Scikit-Learn (`RandomForestRegressor`) for time-series demand forecasting.
3. **Backend API:** FastAPI for serving predictions and restocking recommendations to external systems.

## How to Run This Project
1. Run `zackfDB.sql` in Oracle SQL Developer to create the tables.
2. Install dependencies: `pip install -r requirements.txt`
3. Load data to Oracle: `python load_data.py`
4. Train the ML model: `python train_model.py`
5. Start the API Server: `python -m uvicorn api:app --reload`