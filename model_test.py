import pickle
import numpy as np

filename = "model.pkl"
model_unpickle = open(filename, "rb")
class_model = pickle.load(model_unpickle)
pred = np.array([2, 6, 2, 1, 1, 1])
print(pred)
print(class_model.predict(pred.reshape(1, -1)))
