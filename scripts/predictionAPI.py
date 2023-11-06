

from flask import Flask
from flask_restful import Resource, Api, reqparse

from pricePrediction import predict_car_price
#from flask import Flask, request, jsonify

import numpy as np
import pickle

from datetime import datetime

import pandas as pd



# Initiate API and JobPrediction object
app = Flask(__name__)

"""""
car_model = PricePredictor(model_path=MODEL_PATH,
                           scaler_path=SCALER_PATH,
                           ohe_features_path=OHE_FEATURES_PATH,
                           ohe_fuel_path=OHE_FUEL_PATH,
                           )


# Create prediction endpoint 
@app.route('/predict_car_price', methods=['POST'])
def predict_jobs_probs():
    car_properties = request.get_json()
    predictions = car_model.predict_price(car_properties).to_dict()
    return jsonify(predictions)


"""



api = Api(app)

class CarPricePrediction(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        arguments = [
        ('brand', str),
        ('model', str),
        ('year', str),
        ('km', int),
        ('transmission', str),
        ('fuel', str),
        ('class', str)
    ]
        for arg_name, arg_type in arguments:
            parser.add_argument(arg_name, type=arg_type, required=True)

        args = parser.parse_args()
        
        prediction = predict_car_price(args)
        return {'predicted_price': prediction}

api.add_resource(CarPricePrediction, '/predict_car_price')



if __name__ == '__main__':
    app.run()
    