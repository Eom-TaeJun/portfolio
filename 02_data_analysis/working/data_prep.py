
import pandas as pd
import os
import glob

# Define paths
target_file = "/home/tj/nonmoon/target1/FEDFUNDS.csv"
fred_dir = "/home/tj/nonmoon/fred/"
output_file = "/home/tj/working/prepared_data.csv"

# Load target variable
try:
    target_df = pd.read_csv(target_file)
    target_df['observation_date'] = pd.to_datetime(target_df['observation_date'])
    target_df = target_df.rename(columns={'observation_date': 'date'})
    target_df.set_index('date', inplace=True)
except Exception as e:
    print(f"Error loading target file: {e}")
    exit()

# Load and merge explanatory variables
fred_files = glob.glob(os.path.join(fred_dir, '*.csv'))

# Exclude certain files
excluded_files = ['merged_snapshot_last1y.csv', 'wirp_daily.csv']
fred_files = [f for f in fred_files if os.path.basename(f) not in excluded_files]


merged_df = target_df.copy()

for file in fred_files:
    try:
        df = pd.read_csv(file)
        # Check for 'date' column and handle variations
        if 'observation_date' in df.columns:
            df = df.rename(columns={'observation_date': 'date'})
        elif 'DATE' in df.columns:
            df = df.rename(columns={'DATE': 'date'})
        
        if 'date' not in df.columns:
            print(f"Skipping {os.path.basename(file)}: No 'date' column found.")
            continue

        df['date'] = pd.to_datetime(df['date'])
        
        # Handle missing values represented as '.'
        if 'value' in df.columns:
            df['value'] = pd.to_numeric(df['value'], errors='coerce')

        df.set_index('date', inplace=True)

        # Resample to monthly and forward-fill
        # This handles both monthly and quarterly data
        df = df.resample('MS').ffill()

        # Get series name from filename (e.g., 'CPIAUCSL.csv' -> 'CPIAUCSL')
        series_name = os.path.basename(file).split('.')[0]
        
        # Rename 'value' column to series name
        if 'value' in df.columns:
            df = df.rename(columns={'value': series_name})
        elif series_name in df.columns: # If the column is already named correctly
            pass
        else:
            # If 'value' is not present, use the first column that is not 'date' or 'series_id'
            value_col = [col for col in df.columns if col.lower() not in ['date', 'series_id']]
            if value_col:
                df = df.rename(columns={value_col[0]: series_name})
            else:
                print(f"Skipping {os.path.basename(file)}: No suitable value column found.")
                continue
        
        # Select only the series column to merge
        merged_df = merged_df.join(df[[series_name]], how='left')

    except Exception as e:
        print(f"Error processing file {os.path.basename(file)}: {e}")


# Forward fill to handle misaligned dates between series
merged_df.ffill(inplace=True)

# Drop rows with any remaining NaN values (especially at the beginning)
merged_df.dropna(inplace=True)

# Save the prepared data
merged_df.to_csv(output_file)

print(f"Data preparation complete. Output saved to {output_file}")
print("Data summary:")
print(merged_df.info())
print("First 5 rows:")
print(merged_df.head())
print("Last 5 rows:")
print(merged_df.tail())
