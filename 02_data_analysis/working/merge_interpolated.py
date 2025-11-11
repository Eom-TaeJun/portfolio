import pandas as pd
import os

# Directory containing the data
fred3_dir = "/home/tj/nonmoon/fred3/"

# Get a list of all files in the directory
all_files = os.listdir(fred3_dir)

# Identify the base names of the indicators
base_names = set()
for f in all_files:
    if f.endswith("_interpolated.csv"):
        base_names.add(f.replace("_interpolated.csv", ""))
    elif f.endswith(".csv"):
        base_names.add(f.replace(".csv", ""))

# Process each indicator
for name in base_names:
    original_file = os.path.join(fred3_dir, f"{name}.csv")
    interpolated_file = os.path.join(fred3_dir, f"{name}_interpolated.csv")

    # Check if both files exist
    if os.path.exists(original_file) and os.path.exists(interpolated_file):
        try:
            # Load the dataframes
            original_df = pd.read_csv(original_file, index_col='date', parse_dates=True)
            interpolated_df = pd.read_csv(interpolated_file, index_col='date', parse_dates=True)

            # Use the value from original_df if it exists, otherwise use interpolated_df
            original_col_name = original_df.columns[0]
            interpolated_col_name = interpolated_df.columns[0]
            original_df.rename(columns={original_col_name: 'value'}, inplace=True)
            interpolated_df.rename(columns={interpolated_col_name: 'value'}, inplace=True)

            # Combine the data
            combined_df = original_df.combine_first(interpolated_df)

            # Save the result, overwriting the original file
            combined_df.to_csv(original_file)

            # Verification step
            if os.path.exists(original_file):
                print(f"VERIFIED: {original_file} exists after writing.")
            else:
                print(f"ERROR: {original_file} does NOT exist after writing.")

        except Exception as e:
            print(f"Error processing {name}: {e}")
    elif os.path.exists(original_file):
        print(f"Skipping {name}: No interpolated file found.")

print("\nProcessing complete.")