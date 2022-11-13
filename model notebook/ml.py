import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

df = pd.read_excel(r'Book1.xlsx')

# seperating X and y
X = df.iloc[:, :-1].values
y = df.iloc[:, -1].values

# dividing into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=0)

regressor = LinearRegression()
regressor.fit(X_train, y_train)

y_pred = regressor.predict(X_test)

import pickle
with open('salemodel.pkl', 'wb') as f:
    pickle.dump(regressor, f)
