# Used Cars Price Prediction

Car prices in Egypt have been in a chaotic situation in the past couple of years, especially in the used car market. In this project, I developed a pipeline to scrap car data (nearly 3OK cars) listed on Hatla2ee.com (one of the biggest Egyptian used cars marketplaces) for sale then stored it [Amazone S3](https://aws.amazon.com/pm/serv-s3/?trk=3cda67b9-5fb7-4d3f-84e8-40b544661f21&sc_channel=ps&ef_id=EAIaIQobChMIvq6ItaiwggMVmZKDBx0lRQkQEAAYASAAEgIbbfD_BwE:G:s&s_kwcid=AL!4422!3!645208988791!e!!g!!amazon%20s3%20block%20storage!19580264380!143903638463) storage as a data lake and loaded it in [Amazon Redshift](https://aws.amazon.com/redshift/) data warehouse using [airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html) to run the pipeline daily. Next, I applied some analytics to the data to prepare it for
feeding to a neural network model to predict car prices based on its main
features (brand, model, class, km, transmission, and fuel type), and then I created a RESTful API to deploy the model using Apache Flask. Lastly, I developed a web application using
Plotly Dash provides an interactive user interface for predicting car prices

## Data Source:

I used the [beatifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library to scrap the whole used car data on hatla2ee.com. Firstly, I scraped the car's data based on the fuel type as a search filter to avoid the need to load every single car page to get
the fuel data (this was the only information that was not available on the car's list page and needed to load each car page to get). Then, I scraped data based on the car body search filter, because when I used
both fule and body data as filters at the same time, I found that only 10% of the data are being scraped, which turned out to be caused by the fact that not all cars have the body type information available so they don't appear in the search filter.
I scraped the available cars with body type information and used it to develop a data set with the available body data for each model, which can be used to get the body type of cars of the same model with no body data.



## Technologies
The technologies I used in developing the pipeline are:

    Scrapin: 
    Cloud: AWS
    Data Lake: S3
    Data Warehouse: Amazon Redshift
    Workflow Orchestration: Airflow
    API development: Apache Flask
    Web app development: Dash Plotly



## Project Flow

<img width="804" alt="image" src="https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/d484b6db-4141-41da-95a0-157ba826e427">


## Database Model

![image](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/b2b42f42-ce0f-48f0-8b5c-5ccf653b25fa)

- The cars_data table contains the main car scraped information, the `fingerprint` column is a combination of the `car_id` and `price` columns to be used as a signature to track if the car price has been changed by the seller and needs to be updated.
- car_body_data contains information about the body of the car for each car brand/model.
- car_class_data contains the classes available for each model.


## Data Analytics
