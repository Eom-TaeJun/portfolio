import pandas as pd

file_path = "C:/Users/엄태준/Desktop/cg76_123.xlsx"
data = pd.read_excel(file_path)
data.head()  # To check the structure of the dataset
data['ln_cost'] = np.log(data['cost'])
data['ln_q'] = np.log(data['q'])
data['ln_pl'] = np.log(data['pl'])
data['ln_pk'] = np.log(data['pk'])
data['ln_pf'] = np.log(data['pf'])
import statsmodels.api as sm

X = data[['ln_q', 'ln_pl', 'ln_pk', 'ln_pf']]
X = sm.add_constant(X)
y = data['ln_cost']

model = sm.OLS(y, X).fit()
results = model.summary()
print(results)
