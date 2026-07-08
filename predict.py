import joblib
import numpy as np

# load model
model = joblib.load("model.pkl")

def predict_status(attendance, classes_week, importance, trend, future_percentage):
    
    # convert to array
    features = np.array([[attendance, classes_week, importance, trend, future_percentage]])
    
    prediction = model.predict(features)
    
    return prediction[0]