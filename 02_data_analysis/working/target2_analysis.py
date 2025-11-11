
import pandas as pd
import numpy as np
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import shap
import matplotlib.pyplot as plt

# --- Target Variable Preparation (Consolidated) ---

# Load the consolidated meeting data
concat_file = "/home/tj/nonmoon/target2/FedMeetings_concat.csv"
df_target = pd.read_csv(concat_file)

# The probability columns are of the form (lower-upper)
def get_midpoint(col_name):
    if isinstance(col_name, str):
        matches = re.findall(r'\((\d+)_(\d+)\)', col_name)
        if matches:
            lower = int(matches[0][0])
            upper = int(matches[0][1])
            return (lower + upper) / 2
    return None

# Calculate the expected rate
expected_rates = []
for index, row in df_target.iterrows():
    expected_rate = 0
    total_prob = 0
    for col_name, value in row.items():
        midpoint = get_midpoint(col_name)
        if midpoint is not None and pd.notna(value):
            try:
                prob = float(value)
                expected_rate += midpoint * prob
                total_prob += prob
            except (ValueError, TypeError):
                continue
    if total_prob > 0:
        expected_rates.append(expected_rate / total_prob)
    else:
        expected_rates.append(None)

df_target['expected_rate'] = expected_rates

# Keep only the date and the new target variable
target_df = df_target[['date', 'meeting_date_from_filename', 'expected_rate']].copy()
target_df['date'] = pd.to_datetime(target_df['date'])

# --- Explanatory Variables Preparation ---
fred3_dir = "/home/tj/nonmoon/fred3/"
fred_files = [f for f in os.listdir(fred3_dir) if f.endswith('.csv')]

all_fred_dfs = []
for file in fred_files:
    try:
        df_fred = pd.read_csv(os.path.join(fred3_dir, file), index_col='date', parse_dates=True)
        
        value_col = df_fred.columns[0]
        series_name = file.replace('.csv', '').replace('_interpolated', '')
        df_fred.rename(columns={value_col: series_name}, inplace=True)
        
        all_fred_dfs.append(df_fred[[series_name]])
    except Exception as e:
        print(f"Error processing {file}: {e}")

if all_fred_dfs:
    explanatory_df = pd.concat(all_fred_dfs, axis=1)
    for col in explanatory_df.columns:
        explanatory_df[col] = pd.to_numeric(explanatory_df[col], errors='coerce')
else:
    explanatory_df = pd.DataFrame()

# --- Consolidated Analysis --- #

merged_df = pd.merge(target_df, explanatory_df, left_on='date', right_index=True, how='left')
merged_df.sort_values(by='date', inplace=True)
merged_df.ffill(inplace=True)
merged_df.dropna(inplace=True)

print("--- Consolidated Analysis ---")

if not merged_df.empty:
    X = merged_df.drop(['date', 'meeting_date_from_filename', 'expected_rate'], axis=1)
    y = merged_df['expected_rate']

    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    plt.figure()
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)
    plt.title("Consolidated SHAP Summary Plot")
    plt.savefig("/home/tj/working/consolidated_shap_plot.png", bbox_inches='tight')
    plt.close()

    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    feature_importance = pd.DataFrame(list(zip(X.columns, mean_abs_shap)), columns=['feature', 'mean_abs_shap'])
    feature_importance.sort_values(by='mean_abs_shap', ascending=False, inplace=True)

    print("\nSHAP Feature Importance (Consolidated):")
    print(feature_importance.head(10))
    print("\nConsolidated analysis complete. SHAP plot saved to /home/tj/working/consolidated_shap_plot.png")

    # --- Individual Meeting Analysis (using consolidated model) --- #

    print("\n--- Individual Meeting Analysis (using consolidated model) ---")

    meeting_dates = merged_df['meeting_date_from_filename'].unique()

    for meeting_date in sorted(meeting_dates):
        print(f"\n--- Analyzing Meeting: {meeting_date} ---")
        
        meeting_mask = (merged_df['meeting_date_from_filename'] == meeting_date).values
        
        if np.any(meeting_mask):
            shap_values_meeting = shap_values[meeting_mask]
            X_meeting = X[meeting_mask]

            if X_meeting.shape[0] > 0:
                mean_abs_shap_meeting = np.abs(shap_values_meeting).mean(axis=0)
                feature_importance_meeting = pd.DataFrame(list(zip(X.columns, mean_abs_shap_meeting)), columns=['feature', 'mean_abs_shap'])
                feature_importance_meeting.sort_values(by='mean_abs_shap', ascending=False, inplace=True)

                print("Top 5 Features:")
                print(feature_importance_meeting.head(5))
            else:
                print("No data for this meeting.")
        else:
            print("No data for this meeting.")

else:
    print("Could not generate consolidated data for analysis.")
