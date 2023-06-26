import json

import numpy as np
from category_encoders import TargetEncoder
import pandas as pd
import warnings
from xgboost import XGBRegressor
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
import plotly.graph_objects as go
from sklearn.cross_decomposition import PLSRegression
df = pd.read_csv('../imoveis.csv', sep=';')

df = df.drop('link', axis=1)



df_encoded = df.copy()


# get only the values of 'preco' column larger than 0
df_encoded = df_encoded[df_encoded['preco'] > 0]

# # i want to apply an normalization to the 'preco' column
# df_encoded['preco'] = df_encoded['preco'].apply(lambda x: np.log(x))

# Initialize the target encoder
encoder = TargetEncoder(cols=['bairro'])

df_encoded = df_encoded[df_encoded['preco'] < df_encoded['preco'].quantile(0.75)]
df_encoded = df_encoded[df_encoded['area'] < df_encoded['area'].quantile(0.99)]
df_encoded = df_encoded[df_encoded['quartos'] < df_encoded['quartos'].quantile(0.99)]
df_encoded = df_encoded[df_encoded['vagas'] < df_encoded['vagas'].quantile(0.99)]
df_encoded = df_encoded[df_encoded['banheiros'] < df_encoded['banheiros'].quantile(0.99)]

# Fit the target encoder on the 'bairro' column and transform the data
df_encoded['bairro_encoded'] = encoder.fit_transform(df_encoded['bairro'], df_encoded['preco'])

# Save the neighborhood encoding mapping to a JSON file
neighborhood_encoding = dict(zip(df['bairro'].values.tolist(), df_encoded['bairro_encoded'].values.tolist()))
with open('neighborhood_encoding.json', 'w') as f:
    json.dump(neighborhood_encoding, f)

#
# plot the correlation matrix with seaborn
import seaborn as sns
import matplotlib.pyplot as plt
corr = df_encoded.corr()
sns.heatmap(corr, annot=True, cmap='coolwarm')
plt.show()
#


X = df_encoded.drop(['preco','Imobiliaria', 'Data_scrape', 'bairro', 'last_seen'], axis=1)

y = df_encoded['preco']


X_train_val, X_test, y_train_val, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
X_train, X_val, y_train, y_val = train_test_split(X_train_val, y_train_val, test_size=0.25, random_state=0)

# Define the PLS model
pls = PLSRegression()

# PLS é um método estatístico que busca relacionar um conjunto de variáveis independentes a um conjunto de variáveis dependentes,
# construindo combinações lineares relevantes entre elas

# Fit the PLS model on the original features
pls.fit(X_train, y_train)  # X_train and y_train represent your training data

# Transform the original features to the reduced latent variables
X_train_pls = pls.transform(X_train)  # X_train_pls represents the transformed training data

# Define the XGBoost model
xgb = XGBRegressor()

parameters = {
              'objective':['reg:squarederror'],
              'learning_rate': [.0001, 0.001, .01],
              'max_depth': [3, 5, 7],
              'min_child_weight': [3,5,7],
              'subsample': [0.1,0.5,1.0],
              'colsample_bytree': [0.1, 0.5, 1.0],
              'n_estimators': [500]}


grid_search = GridSearchCV(xgb, parameters, scoring='neg_mean_squared_error', cv=5)
grid_search.fit(X_train_pls, y_train)


best_xgb = grid_search.best_estimator_

eval_set = [(X_train, y_train),
            (X_val, y_val)]

fit_model = best_xgb.fit(
    X_train,
    y_train,
    eval_set=eval_set,
    eval_metric="mae",
    early_stopping_rounds=50,
    verbose=False)

print("MAE:", mean_absolute_error(y_val, fit_model.predict(X_val)))
print("MSE:", mean_squared_error(y_val, fit_model.predict(X_val)))
print("R2:", r2_score(y_val, fit_model.predict(X_val)))

fit_model.save_model('xgb_model.json')