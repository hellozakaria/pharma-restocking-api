from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
from datetime import datetime

# 1. Initialize the FastAPI app
app = FastAPI(
    title="Pharmacy Restocking API",
    description="API to predict medication demand using Machine Learning",
    version="1.0"
)

# 2. Load the trained Machine Learning model
# This happens once when the server starts up
print("Loading Machine Learning model...")
try:
    model = joblib.load('rf_model_m01ab.joblib')
    print("Model loaded successfully!")
except Exception as e:
    print(f"Error loading model: {e}")

# 3. Define the data format we expect from the user
class PredictionRequest(BaseModel):
    target_date: str  # We expect a date string like "YYYY-MM-DD"

# 4. Create a simple welcome endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to the Pharmacy Restocking API! Go to /docs to test the predictions."}

# 5. Create the core prediction endpoint
@app.post("/predict")
def predict_demand(request: PredictionRequest):
    try:
        # Convert the string date into a Python datetime object
        date_obj = datetime.strptime(request.target_date, "%Y-%m-%d")
        
        # Extract the exact features our Random Forest model needs
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        day_of_week = date_obj.weekday() # Monday is 0, Sunday is 6
        
        # Put it into a Pandas DataFrame because that's what our model trained on
        input_data = pd.DataFrame([[year, month, day, day_of_week]], 
                                  columns=['Year', 'Month', 'Day', 'DayOfWeek'])
        
        # Ask the model to predict!
        prediction = model.predict(input_data)
        predicted_boxes = round(prediction[0], 2) # Round to 2 decimal places
        
        # Business Logic: Generate a restocking recommendation
        recommendation = "Normal Stocking"
        if predicted_boxes > 15: # Arbitrary threshold for this example
            recommendation = "High Demand Expected! Prioritize Restocking."
            
        # Return the JSON response to the user
        return {
            "requested_date": request.target_date,
            "drug_category": "M01AB (Anti-inflammatory)",
            "predicted_demand_boxes": predicted_boxes,
            "recommendation": recommendation
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Please use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))