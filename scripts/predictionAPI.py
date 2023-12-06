

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
    
