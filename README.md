# used-cars-price-prediction

Car prices in Egypt have been in a chaotic situation in the past couple of years, especially in the used car market. In this project, I will try to analyze the data of nearly a 3OK 
cars listed on Hatla2ee.com (one of the biggest Egyptian used cars marketplaces) for sale. After analyzing the data, I developed a neural network model to predict car prices based on its main
features (brand, model, class, km, transmission, and fuel type), and then I created a RESTful API to deploy the model using Apache Flask. Lastly, I developed a web application using
Plotly Dash provides an interactive user interface for predicting car prices

## Data source:

I used the `beatifulSoup` library to scrap the whole used car data on hatla2ee.com. Firstly, I scraped the car's data based on the fuel type as a search filter to avoid the need to load every single car page to get
the fuel data (this was the only information that was not available on the car's list page and needed to load each car page to get). Then, I scraped data based on the car body search filter, because when I used
both fule and body data as filters at the same time, I found that only 10% of the data are being scraped, which turned out to be caused by the fact that not all cars have the body type information so they don't appear in the search filter.
I scraped the available cars with body type information and used it to develop a data set with the available body data for each model which can be used with cars with no available body type info of the same model.


