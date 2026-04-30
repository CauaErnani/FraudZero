import joblib
import numpy as np
from sklearn.dummy import DummyClassifier

# Treina com as duas classes (0 e 1) para predict_proba retornar 2 colunas
clf = DummyClassifier(strategy='constant', constant=0)
clf.fit(np.zeros((2, 12)), [0, 1])

joblib.dump(clf, 'models/fraud_model.pkl')
print('Modelo mock gerado com sucesso!')