import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import export_graphviz
import shap
import matplotlib.pyplot as plt
import os

# Load the prepared data
data_file = "/home/tj/working/prepared_data.csv"
df = pd.read_csv(data_file, index_col='date', parse_dates=True)

# Define target and features
X = df.drop('FEDFUNDS', axis=1)
y = df['FEDFUNDS']

# Split data into training and testing sets (time-based split)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Train a RandomForestRegressor model
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X_train, y_train)

# --- SHAP Analysis ---
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Create a SHAP summary plot
plt.figure()
shap.summary_plot(shap_values, X_test, plot_type="bar", show=False)
plt.title("SHAP Summary Plot: Feature Importance for FEDFUNDS Rate")
plt.savefig("/home/tj/working/shap_summary_plot.png", bbox_inches='tight')
plt.close()

# Quantitative analysis of feature importance
mean_abs_shap = np.abs(shap_values).mean(axis=0)
feature_importance = pd.DataFrame(list(zip(X.columns, mean_abs_shap)), columns=['feature', 'mean_abs_shap'])
feature_importance.sort_values(by='mean_abs_shap', ascending=False, inplace=True)

print("SHAP Feature Importance (Quantitative):")
print(feature_importance)

print("\nAnalysis complete. SHAP summary plot saved to /home/tj/working/shap_summary_plot.png")

# --- Tree Visualization ---

# Select one tree from the forest (e.g., the 5th tree)
estimator = model.estimators_[5]

# Export as dot file
dot_file = "/home/tj/working/tree.dot"

# A smaller tree for better visualization
small_tree_model = RandomForestRegressor(n_estimators=10, max_depth=3, random_state=42)
small_tree_model.fit(X_train, y_train)
small_estimator = small_tree_model.estimators_[5]

export_graphviz(small_estimator, out_file=dot_file,
                feature_names = X.columns,
                rounded = True, proportion = False,
                precision = 2, filled = True)

print(f"\nOne decision tree from the Random Forest has been exported to {dot_file}")
