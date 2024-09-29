import pandas as pd
import ast
import os
import re
from sklearn.preprocessing import LabelEncoder

# Function to clean and convert price from string (Lakhs) to integer value without decimals
def clean_price(price_str):
    try:
        clean_str = re.sub(r'[^\d.]', '', price_str).strip()
        if 'Lakh' in price_str:
            return int(float(clean_str) * 100000)
        elif clean_str:
            return int(float(clean_str))
        else:
            return None
    except ValueError:
        return None

# Function to clean km_driven: remove 'kms', commas, and convert to integer
def clean_km_driven(km_str):
    try:
        return int(km_str.replace('kms', '').replace(',', '').strip())
    except ValueError:
        return None

# Function to clean mileage: remove units like 'kmpl' or 'km/kg' and convert to float
def clean_mileage(mileage_str):
    try:
        return float(re.sub(r'[^\d.]', '', mileage_str))
    except ValueError:
        return None

# Function to extract details from each row and standardize data
def extract_details(row):
    try:
        detail = ast.literal_eval(row.get('new_car_detail', '{}'))
        overview = ast.literal_eval(row.get('new_car_overview', '{}'))
        features = ast.literal_eval(row.get('new_car_feature', '{}'))
        specs = ast.literal_eval(row.get('new_car_specs', '{}'))

        owner_info = next((item['value'] for item in overview.get('top', []) if 'Owner' in item.get('key', '')), None)
        owner = owner_info if owner_info else detail.get('owner')

        registration_year = next((item['value'] for item in overview.get('top', []) if 'Registration Year' in item.get('key', '')), None)
        manufacturing_year = detail.get('modelYear')
        price = clean_price(detail.get('price', ''))

        feature_list = [item['value'] for item in features.get('top', [])]
        spec_list = {item['key']: item['value'] for item in specs.get('top', [])}
        mileage = clean_mileage(spec_list.get('Mileage', ''))

        oem = detail.get('oem')
        model = detail.get('model')
        seats = detail.get('seats')
        transmission = detail.get('transmission')
        variant_name = detail.get('variantName')

        km_driven = clean_km_driven(detail.get('km', ''))
        registration_year = int(registration_year) if registration_year else None

        extracted_data = {
            'fuel_type': detail.get('ft'),
            'body_type': detail.get('bt'),
            'km_driven': km_driven,
            'owner': owner,
            'price': price,
            'manufacturing_year': manufacturing_year,
            'link': row.get('car_links'),
            'features': ', '.join(feature_list),
            'oem': oem,
            'model': model,
            'registration_year': registration_year,
            'Mileage': mileage,
            'Seats': seats or spec_list.get('Seats'),
            'transmission': transmission,
            'variantName': variant_name
        }
        return extracted_data
    except Exception as e:
        print(f"Error processing row {row.get('car_links', 'unknown')}: {e}")
        return None

# Function to handle missing values
def handle_missing_values(df):
    numerical_cols = df.select_dtypes(include=['float64', 'int64']).columns
    categorical_cols = df.select_dtypes(include=['object']).columns

    for col in numerical_cols:
        mean_value = df[col].mean()
        df[col].fillna(mean_value, inplace=True)
        print(f"Filled missing values in numerical column '{col}' with mean: {mean_value}")

    for col in categorical_cols:
        mode_value = df[col].mode()[0] if not df[col].mode().empty else 'Unknown'
        df[col].fillna(mode_value, inplace=True)
        print(f"Filled missing values in categorical column '{col}' with mode: {mode_value}")

    return df

# Function to encode categorical variables
def encode_categorical(df):
    label_encoder = LabelEncoder()

    # One-hot encode nominal categorical columns
    nominal_columns = ['fuel_type', 'body_type', 'transmission', 'owner', 'City', 'Seats']
    df = pd.get_dummies(df, columns=nominal_columns, drop_first=True)

    # Label encode ordinal categorical columns (assuming no clear ordinal columns here)
    # Example if needed for ordinal columns:
    # df['some_ordinal_column'] = label_encoder.fit_transform(df['some_ordinal_column'])

    return df

# Function to convert the Excel data into structured format and save it to CSV
def convert_to_structured_format(file_path, city_name, output_dir):
    df = pd.read_excel(file_path)
    structured_data = []

    for index, row in df.iterrows():
        details = extract_details(row)
        if details:
            details['City'] = city_name
            structured_data.append(details)

    structured_df = pd.DataFrame(structured_data)

    # Handle missing values
    structured_df = handle_missing_values(structured_df)

    # Encode categorical variables
    structured_df = encode_categorical(structured_df)

    output_file_path = os.path.join(output_dir, f"{city_name}_structured.csv")
    structured_df.to_csv(output_file_path, index=False)
    print(f"Structured data for {city_name} saved to {output_file_path}.")
    return structured_df

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

for city, file_name in cities.items():
    file_path = os.path.join(data_directory, file_name)
    if os.path.exists(file_path):
        city_data = convert_to_structured_format(file_path, city, data_directory)
        all_cities_data.append(city_data)
    else:
        print(f"File not found: {file_path}")

all_cities_df = pd.concat(all_cities_data, ignore_index=True)

all_cities_output_path = os.path.join(data_directory, "All_Cities.csv")
all_cities_df.to_csv(all_cities_output_path, index=False)
print(f"All cities structured data saved to {all_cities_output_path}.")