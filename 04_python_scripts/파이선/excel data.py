import numpy as np
from matplotlib.pyplot import imshow

# 2. Upload OliveOil.zip
!unzip OliveOil.zip -d olive_oil

!ls olive_oil

# 3. Load raw files as Pandas dataframes
from pathlib import Path
import pandas as pd

train_csv = Path('olive_oil/OliveOil_TRAIN.txt')
valid_csv = Path('olive_oil/OliveOil_TEST.txt')

train_df = pd.read_csv(train_csv, delim_whitespace=True, header=None)
valid_df = pd.read_csv(valid_csv, delim_whitespace=True, header=None)

# Concatenate train and valid set together
df = pd.concat([train_df, valid_df])
df.shape

# 4. Create label arrays (ground truth data)
y_train = train_df[[0]].to_numpy(dtype=int).reshape(-1)
y_valid = valid_df[[0]].to_numpy(dtype=int).reshape(-1)

# Label encoder (e.g, change ['bear', 'rabbit', 'dog'] to [0,1,2])
from sklearn.preprocessing import LabelEncoder

le = LabelEncoder()
y_train_new = le.fit_transform(y_train)
y_valid_new = le.transform(y_valid)

# From new to old label
le.inverse_transform([0, 1, 2, 3])

# 5. Remove labels from df and scale feature values
# Scale using standard score
from sklearn.preprocessing import StandardScaler

# Load scaler
scaler = StandardScaler()

# Scale train and valid sets
# Transform dataframes (take out first column which is label)
X_train = pd.DataFrame(scaler.fit_transform(train_df.iloc[:, 1:]), dtype='float32')
X_valid = pd.DataFrame(scaler.transform(valid_df.iloc[:, 1:]), dtype='float32')

X_train.head()

# 6. Plot some data
import matplotlib.pyplot as plt

# Plot some rows (class = 1)
plt.figure(figsize=(8, 8))
plt.plot(X_train.iloc[0])
plt.plot(X_train.iloc[2])
plt.show()

# Plot some rows (class = 4)
plt.figure(figsize=(8, 8))
plt.plot(X_train.iloc[24])
plt.plot(X_train.iloc[28])
plt.show()

# 7. Classify using XGBoost
import xgboost as xgb
print(xgb.__version__)

# 7.2. Train
# Set XGBoost regressor parameters
my_random_seed = 128
early_stop_rounds = 10

# Initialize XGBoost classifier
xgb_classify = xgb.XGBClassifier(random_state=my_random_seed, early_stopping_rounds=early_stop_rounds)

# Train the model
# xgb_classify.fit(X_train, y_train_new, eval_set=[(X_valid, y_valid_new)])

# 7.3 Predict and get accuracy
# Predict
y_predicted_vaild = xgb_classify.predict(X_valid)

from sklearn.metrics import accuracy_score

# Evaluate predictions
accuracy = accuracy_score(y_valid_new, y_predicted_vaild)
print("Valid set accuracy: {:.2f}%".format(accuracy * 100.0))

# 7.4 Evaluate performance using confusion matrix
from sklearn.metrics import confusion_matrix

conf_mx = confusion_matrix(y_valid_new, y_predicted_vaild)

# Confusion matrix plot
import itertools

def plot_confusion_matrix(cm, target_names, title='Confusion matrix', cmap=None, normalize=True):
    """
    given a sklearn confusion matrix (cm), make a nice plot
    """
    accuracy = np.trace(cm) / np.sum(cm).astype('float')
    misclass = 1 - accuracy

    plt.figure(figsize=(12, 9))

    if cmap is None:
        cmap = plt.get_cmap('Blues')

    if target_names is not None:
        tick_marks = np.arange(len(target_names))
        plt.xticks(tick_marks, target_names, rotation=45)
        plt.yticks(tick_marks, target_names)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.title(title)
    plt.colorbar()

    thresh = cm.max() / 1.5 if normalize else cm.max() / 2
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        if normalize:
            plt.text(j, i, "{:0.2f}".format(cm[i, j]), horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")
        else:
            plt.text(j, i, "{:,}".format(cm[i, j]), horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('True label')
    plt.xlabel('Predicted label\naccuracy={:0.3f}; misclass={:0.3f}'.format(accuracy, misclass))
    plt.show()

# Get class names
my_classes = le.inverse_transform(xgb_classify.classes_)
my_classes

# Plot confusion matrix (raw)
plot_confusion_matrix(conf_mx, my_classes, cmap=None, normalize=False)

# Plot confusion matrix (proportions)
plot_confusion_matrix(conf_mx, my_classes, cmap='Greens', normalize=True)

# 8. Interpretability
# Feature importance
print(xgb_classify.feature_importances_)

# Plot the top 10 features by weight
xgb.plot_importance(xgb_classify, importance_type='weight', max_num_features=10, height=0.5)
plt.title("Top 10 Features by Weight")
plt.show()

# Plot a specific tree (e.g., the first tree)
xgb.plot_tree(xgb_classify, num_trees=0)
plt.figure(figsize=(20, 10))  # Adjust the figure size as needed
plt.show()

# Plot the first 3 trees in the model
for i in range(3):
    plt.figure(figsize=(20, 10))
    xgb.plot_tree(xgb_classify, num_trees=i)
    plt.title(f"Tree {i}")
    plt.show()

# 9. Tune XGBoost parameters using Randomized Search CV
from xgboost import cv
from sklearn.model_selection import RandomizedSearchCV

# Range of parameters to do search
param_grid = {
    "max_depth": [3, 4, 5, 6],
    "learning_rate": [0.01, 0.05, 0.1, 0.15],
    "gamma": [0, 0.25, 0.5, 0.75, 1],
    "subsample": [0.4, 0.6, 0.8],
    "colsample_bytree": [0.25, 0.5, 0.75],
    "n_estimators": [100, 150, 200, 250, 300]
}

# Initialize Randomized Search CV
xgb_cl = xgb.XGBClassifier(random_state=my_random_seed)
search_seed = 42
search = RandomizedSearchCV(xgb_cl, param_distributions=param_grid, n_jobs=-1, cv=3, verbose=1,
                             random_state=search_seed, return_train_score=True)

# Fit the search
# search.fit(X_train, y_train_new)

# Display best parameters and scores
print("Best Parameters:", search.best_params_)
print("Best Score:", search.best_score_)
print("Best Estimator:", search.best_estimator_)

# Set up best estimator with early stopping
xgb_classify_best_estimator = search.best_estimator_.set_params(
    random_state=my_random_seed,
    early_stopping_rounds=early_stop_rounds
)

# Fit the best estimator
# xgb_classify_best_estimator.fit(X_train, y_train_new, eval_set=[(X_valid, y_valid_new)])

# Predict using the best estimator
y_predicted_vaild_tuned = xgb_classify_best_estimator.predict(X_valid)

# Evaluate predictions
accuracy = accuracy_score(y_valid_new, y_predicted_vaild_tuned)
print("Valid set accuracy after tuning: {:.2f}%".format(accuracy * 100.0))

conf_mx = confusion_matrix(y_valid_new, y_predicted_vaild_tuned)

# Plot confusion matrix (raw)
plot_confusion_matrix(conf_mx, my_classes, cmap=None, normalize=False)

# Plot confusion matrix (proportions)
plot_confusion_matrix(conf_mx, my_classes, cmap='Greens', normalize=True)

# Save the model
xgb_classify_best_estimator.save_model("xgb_model.json")

# Load model
# xgb_model = xgb.XGBClassifier()
# xgb_model.load_model("xgb_model.json")
