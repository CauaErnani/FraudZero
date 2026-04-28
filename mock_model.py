import joblib
import numpy as np
from sklearn.dummy import DummyClassifier

# 12 colunas = exatamente o FEATURE_COLUMNS do analysis.py
clf = DummyClassifier(strategy='constant', constant=0)
clf.fit(np.zeros((1, 12)), [0])

joblib.dump(clf, 'models/fraud_model.pkl')
print('Modelo mock gerado com sucesso!')
