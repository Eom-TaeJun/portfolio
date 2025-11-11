import pandas as pd
import numpy as np
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import shap
import matplotlib.pyplot as plt

# --- Target Variable Preparation ---

# Load the CME targets panel data
cme_file = "/home/tj/nonmoon/target2/cme_targets_panel.csv"
df_target = pd.read_csv(cme_file)

# Rename asof_date to date for merging
df_target.rename(columns={'asof_date': 'date'}, inplace=True)
target_df = df_target[['date', 'meeting_date', 'exp_rate_bp']].copy()
target_df['date'] = pd.to_datetime(target_df['date'])

# --- Explanatory Variables Preparation ---
fred3_dir = "/home/tj/nonmoon/fred3/"
fred_files = [f for f in os.listdir(fred3_dir) if f.endswith('.csv') and 'DGS2' not in f]

all_fred_dfs = []
for file in fred_files:
    try:
        df_fred = pd.read_csv(os.path.join(fred3_dir, file), index_col='date', parse_dates=True)
        
        # Find the value column
        value_col = df_fred.columns[0]
        
        # Rename it to the name of the file (without extension)
        series_name = file.replace('.csv', '').replace('_interpolated', '')
        df_fred.rename(columns={value_col: series_name}, inplace=True)
        
        # Keep only the renamed value column
        all_fred_dfs.append(df_fred[[series_name]])
    except Exception as e:
        print(f"Error processing {file}: {e}")

# Concatenate all dataframes
if all_fred_dfs:
    explanatory_df = pd.concat(all_fred_dfs, axis=1)
    for col in explanatory_df.columns:
        explanatory_df[col] = pd.to_numeric(explanatory_df[col], errors='coerce')
else:
    explanatory_df = pd.DataFrame()

# --- Consolidated Analysis --- #

# Merge target and explanatory data
merged_df = pd.merge(target_df, explanatory_df, left_on='date', right_index=True, how='left')

# Forward-fill and drop NaNs
merged_df.sort_values(by='date', inplace=True)
merged_df.ffill(inplace=True)
merged_df.dropna(inplace=True)

print("--- Consolidated Analysis (excluding DGS2) ---")

if not merged_df.empty:
    # Define target and features
    X = merged_df.drop(['date', 'meeting_date', 'exp_rate_bp'], axis=1)
    y = merged_df['exp_rate_bp']

    # Train a RandomForestRegressor model
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X, y)

    # Explain the model's predictions using SHAP
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)

    # Create a SHAP summary plot
    plt.figure()
    shap.summary_plot(shap_values, X, plot_type="bar", show=False)
    plt.title("Consolidated SHAP Summary Plot (excluding DGS2)")
    plt.savefig("/home/tj/working/cme_consolidated_shap_plot.png", bbox_inches='tight')
    plt.close()

    # Quantitative analysis of feature importance
    mean_abs_shap = np.abs(shap_values).mean(axis=0)
    feature_importance = pd.DataFrame(list(zip(X.columns, mean_abs_shap)), columns=['feature', 'mean_abs_shap'])
    feature_importance.sort_values(by='mean_abs_shap', ascending=False, inplace=True)

    print("\nSHAP Feature Importance (Consolidated, excluding DGS2):")
    print(feature_importance.head(10))
    print("\nConsolidated analysis complete. SHAP plot saved to /home/tj/working/cme_consolidated_shap_plot.png")

else:
    print("Could not generate consolidated data for analysis.")