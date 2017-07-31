import pandas as pd
import numpy as np
import xgboost as xgb
import pickle
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

train = pd.read_csv("data/train.csv")
train = train[['kills', 'deaths', 'assists', 'kda', 'gold_per_min', 'xp_per_min', 'last_hits', 'denies', 'main_role']]

train = train.dropna()

dataset = train.values

X = dataset[:,0:8]
Y = dataset[:,8]

label_encoder = LabelEncoder()
label_encoder = label_encoder.fit(Y)
label_encoded_y = label_encoder.transform(Y)
seed = 7

X_train, X_test, y_train, y_test = train_test_split(X, label_encoded_y, test_size=0.33, random_state=seed)

model = xgb.XGBClassifier()
model.fit(X_train, y_train)
print(model)
# make predictions for test data
y_pred = model.predict(X_test)
print(y_pred)
predictions = [round(value) for value in y_pred]
# evaluate predictions
accuracy = accuracy_score(y_test, predictions)
print("Accuracy: %.2f%%" % (accuracy * 100.0))

filename = 'finalized_model.pkl'
pickle.dump(model, open(filename, 'wb'))
