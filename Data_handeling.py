import pandas as pd
import ast
import os
import re  # Import regex for price cleaning

# Function to clean and convert price from string (Lakhs) to numeric value
def clean_price(price_str):
    try:
        # Remove ₹ symbol and any non-numeric characters, then trim spaces
        clean_str = re.sub(r'[^\d.]', '', price_str).strip()

        # Check if the price is given in Lakhs, and if so, multiply by 100,000
        if 'Lakh' in price_str:
            return float(clean_str) * 100000  # Convert to numeric and adjust for Lakhs
        elif clean_str:
            return float(clean_str)  # Return the cleaned numeric value
        else:
            return None
    except ValueError:
        return None

# Function to extract details from each row
def extract_details(row):
    try:
        # Parse the JSON structure from 'new_car_detail', 'new_car_overview', 'new_car_feature', 'new_car_specs'
        detail = ast.literal_eval(row.get('new_car_detail', '{}'))
        overview = ast.literal_eval(row.get('new_car_overview', '{}'))
        features = ast.literal_eval(row.get('new_car_feature', '{}'))
        specs = ast.literal_eval(row.get('new_car_specs', '{}'))

        # Extract owner information from overview
        owner_info = next((item['value'] for item in overview.get('top', []) if 'Owner' in item.get('key', '')), None)
        owner = owner_info if owner_info else detail.get('owner')  # Use owner from detail if not found in overview

        # Extract registration year
        registration_year = next((item['value'] for item in overview.get('top', []) if 'Registration Year' in item.get('key', '')), None)

        # Extract manufacturing year from detail
        manufacturing_year = detail.get('modelYear')

        # Extract and clean price details
        price = clean_price(detail.get('price', ''))

        # Extract features
        feature_list = [item['value'] for item in features.get('top', [])]

        # Extract specifications
        spec_list = {item['key']: item['value'] for item in specs.get('top', [])}

        # Extract OEM, Model, and Seats from detail
        oem = detail.get('oem')
        model = detail.get('model')
        seats = detail.get('seats')

        # Construct the final data dictionary
        extracted_data = {
            'fuel_type': detail.get('ft'),
            'body_type': detail.get('bt'),
            'km_driven': detail.get('km'),
            'owner': owner,
            'price': price,
            'manufacturing_year': manufacturing_year,
            'link': row.get('car_links'),
            'features': ', '.join(feature_list),  # Join features into a single string
            'oem': oem,
            'model': model,
            'registration_year': registration_year,
            'Mileage': spec_list.get('Mileage'),
            'Engine': spec_list.get('Engine'),
            'Seats': seats or spec_list.get('Seats')  # Seats from detail or specs
        }

        return extracted_data
    except Exception as e:
        print(f"Error processing row {row.get('car_links', 'unknown')}: {e}")
        return None

# Function to handle missing values
def handle_missing_values(df):
    # Separate numerical and categorical columns
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    # Impute missing values in numerical columns with the mean
    for col in numerical_cols:
        mean_value = df[col].mean()
        df[col].fillna(mean_value, inplace=True)
        print(f"Filled missing values in numerical column '{col}' with mean: {mean_value}")

    # Impute missing values in categorical columns with mode or 'Unknown'
    for col in categorical_cols:
        mode_value = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
        df[col].fillna(mode_value, inplace=True)
        print(f"Filled missing values in categorical column '{col}' with mode: {mode_value}")

    return df

# Function to convert the Excel data into structured format and save it to CSV
def convert_to_structured_format(file_path, city_name, output_dir):
    # Load the Excel file
    df = pd.read_excel(file_path)
    
    # Create an empty list to store the structured data
    structured_data = []

    # Iterate over each row in the dataframe
    for index, row in df.iterrows():
        details = extract_details(row)
        if details:
            details['City'] = city_name  # Add the city name for each row
            structured_data.append(details)

    # Convert the structured data into a new DataFrame
    structured_df = pd.DataFrame(structured_data)

    # Handle missing values
    structured_df = handle_missing_values(structured_df)

    # Save the structured data to CSV
    output_file_path = os.path.join(output_dir, f"{city_name}_structured.csv")
    structured_df.to_csv(output_file_path, index=False)
    print(f"Structured data for {city_name} saved to {output_file_path}.")
    return structured_df  # Return the structured DataFrame

# Directory containing the Excel files
data_directory = r'D:\CarDekho\Dataset'

# List of city names and corresponding file names
cities = {
    "Bangalore": "bangalore_cars.xlsx",
    "Chennai": "chennai_cars.xlsx",
    "Delhi": "delhi_cars.xlsx",
    "Hyderabad": "hyderabad_cars.xlsx",
    "Jaipur": "jaipur_cars.xlsx",
    "Kolkata": "kolkata_cars.xlsx"
}

# Initialize a list to hold all city DataFrames
all_cities_data = []

# Process each city file and save the structured data
for city, file_name in cities.items():
    file_path = os.path.join(data_directory, file_name)
    if os.path.exists(file_path):
        city_data = convert_to_structured_format(file_path, city, data_directory)
        all_cities_data.append(city_data)  # Add the structured data for this city to the list
    else:
        print(f"File not found: {file_path}")

# Concatenate all city DataFrames into a single DataFrame
all_cities_df = pd.concat(all_cities_data, ignore_index=True)

# Save the combined DataFrame to CSV
all_cities_output_path = os.path.join(data_directory, "All_Cities.csv")
all_cities_df.to_csv(all_cities_output_path, index=False)
print(f"All cities structured data saved to {all_cities_output_path}.")