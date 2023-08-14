import pickle
import mlflow
from flask import Flask, request, jsonify


LOGGED_MODEL = 's3://mlflow-models-bruno/1/1485ca1c181a45e1afa6a4d265225bb2/artifacts/model'
model = mlflow.pyfunc.load_model(LOGGED_MODEL)

with open ('models/preprocessor.b', 'rb') as file:
    dv = pickle.load(file)

def prepare_features(bike_ride):
    features = {}
    features['start_end_id'] = bike_ride['start_station_id'] + '-' +bike_ride['end_station_id']
    features['rideable_type'] = bike_ride['rideable_type']
    features['member_casual'] = bike_ride['member_casual']
    return features

def predict(features):
    X = dv.transform(features)
    preds = model.predict(X)
    return float(preds[0])

app = Flask('bike-share-duration-prediction')

@app.route('/predict', methods = ['POST'])
def predict_endpoint():
    ride = request.get_json()
    features = prepare_features(ride)
    pred = predict(features)
    result = {'duration':pred}
    return jsonify (result)

if __name__ == "__main__":
    app.run(debug=True, host = '0.0.0.0', port = '9696')