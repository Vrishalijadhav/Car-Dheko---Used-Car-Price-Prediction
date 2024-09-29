import streamlit as st
import pandas as pd
import joblib

# Load the trained model
model = joblib.load(r'C:\Users\VRISHALI\car_price_model.pkl')

# Function to preprocess user input
def preprocess_input(input_data):
    # Create a DataFrame from the input data
    input_df = pd.DataFrame([input_data])

    # Define all feature columns that your model was trained on
    feature_columns = [
        'km_driven', 'manufacturing_year', 'Seats',
        'fuel_type_Cng', 'fuel_type_Diesel', 'fuel_type_Electric', 'fuel_type_Lpg', 'fuel_type_Petrol',
        'body_type_Coupe', 'body_type_Hatchback', 'body_type_MUV',
        'body_type_Minivans', 'body_type_Pickup Trucks', 'body_type_SUV',
        'body_type_Sedan', 'owner_0th Owner', 'owner_Fifth Owner', 'owner_First Owner',
        'owner_Fourth Owner', 'owner_Second Owner', 'owner_Third Owner',
        'transmission_Automatic', 'transmission_Manual',
        'City_Bangalore', 'City_Chennai', 'City_Delhi',
        'City_Hyderabad', 'City_Jaipur', 'City_Kolkata'
    ]
    
    # Reindex the input DataFrame to include all feature columns
    for col in feature_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # Ensure the input DataFrame matches the feature columns expected by the model
    input_df = input_df[feature_columns]
    return input_df

# Streamlit application layout
st.title("Used Car Price Prediction")

# User input fields
km_driven = st.number_input("Kms Driven", min_value=0, value=0)
manufacturing_year = st.number_input("Year of Manufacture", min_value=1980, max_value=2024, value=2020)
owner = st.selectbox("Owner", options=["0th Owner", "First Owner", "Second Owner", "Third Owner", "Fourth Owner", "Fifth Owner"])
transmission = st.selectbox("Transmission", options=["Automatic", "Manual"])
fuel_type = st.selectbox("Fuel Type", options=["Petrol", "Diesel", "CNG", "Electric", "LPG"])
city = st.selectbox("City", options=["Bangalore", "Chennai", "Delhi", "Hyderabad", "Jaipur", "Kolkata"])
body_type = st.selectbox("Body Type", options=["Coupe", "Hatchback", "MUV", "Minivans", "Pickup Trucks", "SUV", "Sedan"])
seats = st.number_input("Seats", min_value=1, max_value=10, value=5)  # Default to 5 seats

# Prepare the input data
input_data = {
    'km_driven': km_driven,
    'manufacturing_year': manufacturing_year,
    'Seats': seats,
    'fuel_type_Cng': 1 if fuel_type == "CNG" else 0,
    'fuel_type_Diesel': 1 if fuel_type == "Diesel" else 0,
    'fuel_type_Electric': 1 if fuel_type == "Electric" else 0,
    'fuel_type_Lpg': 1 if fuel_type == "LPG" else 0,
    'fuel_type_Petrol': 1 if fuel_type == "Petrol" else 0,
    'body_type_Coupe': 1 if body_type == "Coupe" else 0,
    'body_type_Hatchback': 1 if body_type == "Hatchback" else 0,
    'body_type_MUV': 1 if body_type == "MUV" else 0,
    'body_type_Minivans': 1 if body_type == "Minivans" else 0,
    'body_type_Pickup Trucks': 1 if body_type == "Pickup Trucks" else 0,
    'body_type_SUV': 1 if body_type == "SUV" else 0,
    'body_type_Sedan': 1 if body_type == "Sedan" else 0,
    'owner_0th Owner': 1 if owner == "0th Owner" else 0,
    'owner_First Owner': 1 if owner == "First Owner" else 0,
    'owner_Second Owner': 1 if owner == "Second Owner" else 0,
    'owner_Third Owner': 1 if owner == "Third Owner" else 0,
    'owner_Fourth Owner': 1 if owner == "Fourth Owner" else 0,
    'owner_Fifth Owner': 1 if owner == "Fifth Owner" else 0,
    'transmission_Automatic': 1 if transmission == "Automatic" else 0,
    'transmission_Manual': 1 if transmission == "Manual" else 0,
    'City_Bangalore': 1 if city == "Bangalore" else 0,
    'City_Chennai': 1 if city == "Chennai" else 0,
    'City_Delhi': 1 if city == "Delhi" else 0,
    'City_Hyderabad': 1 if city == "Hyderabad" else 0,
    'City_Jaipur': 1 if city == "Jaipur" else 0,
    'City_Kolkata': 1 if city == "Kolkata" else 0
}

# Process input data
processed_data = preprocess_input(input_data)

# Prediction button
if st.button("Predict Price"):
    try:
        predicted_price = model.predict(processed_data)
        st.success(f"The predicted price of the car is: ₹{predicted_price[0]:,.2f}")
    except ValueError as e:
        st.error(f"Error in prediction: {e}")
