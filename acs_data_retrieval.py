import pandas as pd
from census import Census
import time
import sys
import numpy as np

# --- CONFIGURATION ---
CENSUS_API_KEY = "473eefeb957e8b011f5ded70ad5d08d27788dea2" 

# Initialize the Census object
try:
    c = Census(CENSUS_API_KEY, year=2023) 
except Exception as e:
    print(f"Error initializing Census client: {e}")
    sys.exit(1)

# 2. Define the geographic scope and time frame
# We only want the 2019-2023 5-year estimate, which is defined by its end year: 2023.
YEARS = [2023]

# City Definitions: (City Name, State FIPS, {County FIPS: City Reference})
CITY_GEOGRAPHIES = {
    "Chicago, IL": {
        "state_fips": "17", 
        "counties": {"031": "Cook County"}
    },
    "New York City, NY": {
        "state_fips": "36", 
        "counties": {
            "061": "Manhattan",
            "047": "Brooklyn",
            "081": "Queens",
            "005": "The Bronx",
            "085": "Staten Island"
        }
    },
    "Dallas, TX": {
        "state_fips": "48", 
        "counties": {"113": "Dallas County"}
    },
    "Oklahoma City, OK": {
        "state_fips": "40", 
        "counties": {"109": "Oklahoma County"}
    }
}

# 3. Define the ACS Variables (Codes and their meaningful names)
# The API returns the code + 'E' (for Estimate).

VARIABLE_MAP = {
    # --- EMPLOYMENT (Target Variable) ---
    # B23025_004E: Civilian Labor Force (Denominator) 
    "B23025_004E": "Civilian_Labor_Force",
    # B23025_006E: Unemployed Population (Numerator) 
    "B23025_006E": "Unemployed_Population",
    
    # --- INCOME (Key Economic Predictor) ---
    "B19013_001E": "Median_Household_Income",
    
    # --- POVERTY (Distress Predictor) ---
    "B17001_001E": "Poverty_Universe",
    "B17001_002E": "Population_Below_Poverty",
    
    # --- EDUCATION (Opportunity Predictor) ---
    "B15003_001E": "Total_Pop_25_Plus",
    "B15003_022E": "Bachelors_Degree",
    "B15003_023E": "Masters_Degree",
    "B15003_024E": "Professional_Degree",
    "B15003_025E": "Doctorate_Degree",

    # --- URBAN DEVELOPMENT/ACCESS (B08134: Mean Travel Time to Work) ---
    "B08134_001E": "Mean_Travel_Time_Seconds",
}

# List of ALL variable codes needed for the API request
API_VAR_CODES = list(VARIABLE_MAP.keys())

# --- DATA ACQUISITION FUNCTION ---

def get_acs_data(year, state_fips, county_fips, api_vars):
    """Fetches ACS 5-year data for all census tracts within a specified county."""
    
    # The Census API expects a list of variables for the 'get' parameter
    data = c.acs5.get(
        ["NAME"] + api_vars, 
        geo={'for': 'tract:*', 'in': f'state:{state_fips} county:{county_fips}'},
        year=year
    )
    
    if not data:
        print(f"Warning: No data returned for year {year} in county {county_fips}.")
        return None

    # Convert to DataFrame and apply explicit renaming
    df = pd.DataFrame(data)
    
    # Map the API codes to the descriptive names
    df = df.rename(columns=VARIABLE_MAP)

    # Convert GEOID parts to strings and create the full GEOID
    df['state'] = df['state'].astype(str)
    df['county'] = df['county'].astype(str)
    df['tract'] = df['tract'].astype(str)
    df['GEOID'] = df['state'] + df['county'] + df['tract']
    
    return df

# --- MAIN EXECUTION ---
print("Starting ACS Data Acquisition...")

all_data_frames = []
total_counties = sum(len(geo['counties']) for geo in CITY_GEOGRAPHIES.values())
current_county_count = 0

for city, geo_info in CITY_GEOGRAPHIES.items():
    state_fips = geo_info['state_fips']
    for county_fips, county_name in geo_info['counties'].items():
        current_county_count += 1
        
        for year in YEARS:
            acs_period = f"{year-4}-{year}"
            
            print(f"[{current_county_count}/{total_counties}] Fetching {city} ({county_name}) for period: {acs_period}...")
            
            try:
                df_temp = get_acs_data(year, state_fips, county_fips, API_VAR_CODES)
                
                if df_temp is not None:
                    df_temp['City'] = city
                    df_temp['County_Name'] = county_name
                    df_temp['ACS_Year'] = year
                    df_temp['ACS_Period'] = acs_period
                    all_data_frames.append(df_temp)
                
                time.sleep(0.1) 
            except Exception as e:
                print(f"An error occurred while fetching data for {city} in {acs_period}: {e}")
                time.sleep(2) 
                continue

if not all_data_frames:
    print("No data was successfully retrieved. Check your API key and FIPS codes.")
    sys.exit(1)

# 4. Concatenate and Clean the Final DataFrame
raw_df = pd.concat(all_data_frames, ignore_index=True)

# Convert all raw count and numeric columns to numbers, coercing errors to NaN
numeric_cols = list(VARIABLE_MAP.values())

for col in numeric_cols:
    raw_df[col] = pd.to_numeric(raw_df[col], errors='coerce')


# --- CALCULATE FINAL METRICS ---

# Sum the four degree columns to get the total Bachelors+ count
education_cols = ['Bachelors_Degree', 'Masters_Degree', 'Professional_Degree', 'Doctorate_Degree']
raw_df['Bachelors_Plus'] = raw_df[education_cols].sum(axis=1, skipna=True)


# 1. Unemployment Rate (%)
# Formula: (Unemployed / Civilian Labor Force) * 100
raw_df['Unemployment_Rate'] = (
    (raw_df['Unemployed_Population'] / raw_df['Civilian_Labor_Force']) * 100
).replace([np.inf, -np.inf], np.nan).round(2)

# 2. Poverty Rate (%)
# Formula: (Below Poverty / Poverty Universe) * 100
raw_df['Poverty_Rate'] = (
    (raw_df['Population_Below_Poverty'] / raw_df['Poverty_Universe']) * 100
).replace([np.inf, -np.inf], np.nan).round(2)

# 3. Bachelors Degree or Higher Rate (%)
# Formula: (Bachelors+ / Total Pop 25+) * 100
raw_df['Bachelors_Plus_Rate'] = (
    (raw_df['Bachelors_Plus'] / raw_df['Total_Pop_25_Plus']) * 100
).replace([np.inf, -np.inf], np.nan).round(2)

# 4. Mean Travel Time (Convert from Seconds to Minutes)
# The variable B08134_001E returns the aggregate travel time in seconds, divided by 60 to get the time in minutes. 
raw_df['Mean_Travel_Time_Minutes'] = (raw_df['Mean_Travel_Time_Seconds'] / 60).round(2)

# Drop rows where the key rates could not be calculated (denominator was 0 or NaN)
clean_df = raw_df.dropna(subset=['Unemployment_Rate', 'Poverty_Rate', 'Bachelors_Plus_Rate'])

# Select final columns for EDA
final_columns = [
    'GEOID', 'NAME', 'City', 'County_Name', 'ACS_Year', 'ACS_Period',
    'Unemployment_Rate', 'Poverty_Rate', 'Bachelors_Plus_Rate',
    'Median_Household_Income', 'Mean_Travel_Time_Minutes'
]

final_df = clean_df[final_columns].copy()

# Save the final cleaned data to a CSV file for EDA
output_filename = "urban_economic_opportunity_data.csv"
final_df.to_csv(output_filename, index=False)

print("\n--- Data Acquisition Complete ---")
print(f"Total rows retrieved: {len(raw_df)}")
print(f"Clean rows ready for EDA: {len(final_df)}")
print(f"Data saved to: {output_filename}")