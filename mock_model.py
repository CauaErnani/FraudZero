import os
import joblib
from sklearn.dummy import DummyClassifier
import numpy as np

# Cria a pasta 'models' se ela não existir
os.makedirs('models', exist_ok=True)

# Cria um modelo burro que sempre diz que NÃO é fraude (0)
clf = DummyClassifier(strategy="constant", constant=0)
# Treina com dados falsos só para inicializar a estrutura (12 colunas)
clf.fit(np.zeros((1, 12)), [0])

# Agora ele vai salvar com sucesso, pois a pasta existe com certeza
joblib.dump(clf, "models/fraud_model.pkl")
print("Modelo mock gerado com sucesso!")