# app.py
import dash_daq as daq
import pandas as pd
from dash import Dash, Input, Output, dcc, html, State
from datetime import datetime
import plotly.express as px
import requests
import json
import dash

API_URL = 'http://127.0.0.1:5000/predict_car_price'


features = pd.read_pickle('../models/ohe_features.pkl')

fuel_data = pd.read_pickle("../models/ohe_fuel.pkl")

date = datetime.now()
year = int(date.strftime("%Y"))
model_year = range(1920, year + 2)

brands = features["brand"].sort_values().unique()


top_brands = features.groupby('brand').agg(average=('price', 'mean'), count=('brand','count')).sort_values(by='count', ascending=False)[:20]
brands_data = top_brands.sort_values(by='average', ascending=True)

top_models = features.groupby(['brand', 'model']).agg(average=('price', 'mean'), count=('model','count')).sort_values(by='count', ascending=False)[:40]
models_data = top_models.sort_values(by='average', ascending=True)
avg_model_price_y = top_models.sort_values(by='average', ascending=True)['average'].values




external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "car price prediction"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🚗", className="header-emoji"),
                html.H1(
                    children="Predict your car price!", className="header-title"
                ),
                html.P(
                    children=(
                        "Car price prediction platform based on analytics of "
                        "used cars market data in Egypt"
                    ),
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Brand", className="menu-title"),
                        dcc.Dropdown(
                            id="brand-selector",
                            options=[
                                {"label": brand, "value": brand}
                                for brand in brands
                            ],
                            value="Albany",
                            clearable=True,
                            className="",
                        ),
                    ]
                ),

                html.Div(
                    children=[
                        html.Div(children="Model", className="menu-title"),
                        dcc.Dropdown(
                            id="model-selector",
                            value="model",
                            clearable=True,
                            className="",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Class", className="menu-title"),
                        dcc.Dropdown(
                            id="class-selector",
                            value="class",
                            clearable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(children="Model year", className="menu-title"),
                        dcc.Dropdown(
                            id="year-selector",
                            options=[
                                {
                                    "label": year,
                                    "value": year,
                                }
                                for year in model_year
                            ],
                            value="year",
                            clearable=True,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Transmission", className="menu-title"
                        ),
                        dcc.Dropdown(
                            id="transmission-selector",
                            options=[
                                {
                                    "label": transmission,
                                    "value": transmission,
                                }
                                for transmission in ['Automatic', 'Manual']
                            ],
                        ),
                    ]
                ),

                html.Div(
                    children=[
                        html.Div(
                            children="Fuel", className="menu-title"
                        ),
                        dcc.Dropdown(
                            id="fuel-selector",
                            options=[
                                {
                                    "label": fuel,
                                    "value": fuel,
                                }
                                for fuel in fuel_data['fuel'].sort_values().unique()
                            ],
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="km", className="menu-title"
                        ),
                        dcc.Input(
                            id = "km",
                            className="Input",
                            type='number',
                            min=0,
                            required=True,
                            max=999999,
                        ),
                    ]
                ),
                html.Div([
                    html.Button('Predict Price',
                                id='predict-button',
                                n_clicks=None,
                                className='Button')
                ]),
            ],
            className="menu",
        ),
        
        html.Div(
            children=[
                html.P(
                    children="", className="price-display", id="price-section"
                ),]),

        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        config={
			'displayModeBar':False,
			'queueLength':0
		},
                        figure={
                            
                            'data': [
                                {'x': brands_data.index, 'y': brands_data['average'].values, 'type': 'bar', 'name': 'brands',  'marker' : { "color" : "#4CAF50"}},
                            ],
                            'layout': {
                                'title': 'Average used cars price for top brands in Egypt',
                            }
                        },
                                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                       figure={  
                            'data': [
                                {'x': [f"{i[1]}({i[0]})" for i in models_data.index], 'y': models_data['average'].values, 'type': 'bar', 'name': 'models',  'marker' : { "color" : "#4CAF50"}},
                            ],
                            'layout': {
                                'title': 'Average used cars price for top car models in Egypt',
                                 'xaxis': {
                            'tickangle': 45, # Set the tick angle for the x-axis,
                            'automargin': True  
                        },

                            }
                        }
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    Output(component_id='model-selector', component_property='options'),
    Input(component_id='brand-selector', component_property='value')
)
def filter_brands(brand):
    options = [
        {
            "label": model.title(),
            "value": model,
        }
        for model in features.query(f"brand == @brand")['model'].sort_values().unique()
    ]
    return options


@app.callback(
    Output(component_id='class-selector', component_property='options'),
    Input(component_id='brand-selector', component_property='value'),
    Input(component_id='model-selector', component_property='value')
)
def filter_class(brand, model):
    options = [
        {
            "label": car_class.capitalize().title(),
            "value": car_class.capitalize(),
        }
        for car_class in features.query(f"brand == @brand and model == @model")['class_new'].sort_values().unique()
    ]
    return options

@app.callback(
    Output('price-section', 'children'),

    inputs=dict(n_clicks=Input('predict-button', 'n_clicks')),
    state=dict(brand=State('brand-selector', 'value'),
    model=State('model-selector', 'value'),
    year =State('year-selector', 'value'),
    km=State('km', 'value'),
    transmission=State('transmission-selector', 'value'),
    fuel=State('fuel-selector', 'value'),
    class_name=State('class-selector', 'value'),)
)
def predict_price(n_clicks, brand, model, year, km, transmission, fuel,  class_name):
    if n_clicks is not None:
        

        input_data = {
        'brand': brand,
        'model': model,
        'year': year,
        'km': km,
        'transmission':transmission ,
        'fuel': fuel,
        'class':class_name
    }

        response = requests.post(API_URL, json=input_data)
        if response.status_code == 200:
            result = response.json()
            avg_price = features.query(f"brand == @brand and model == @model")['price'].mean()
            output = f"Estimated price: {round(float(result.get('predicted_price')))} EGP. (Average price for this model is: {round(avg_price)} EGP)"
            return output
        else:
            return "Not enough data to predict price"


if __name__ == "__main__":
    app.run_server(debug=True)
