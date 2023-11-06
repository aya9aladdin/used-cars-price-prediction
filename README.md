# Used Cars Price Prediction

Car prices in Egypt have been in a chaotic situation in the past couple of years, especially in the used car market. In this project, I developed a pipeline to scrap car data (nearly 3OK cars) listed on Hatla2ee.com (one of the biggest Egyptian used cars marketplaces) for sale then stored it [Amazone S3](https://aws.amazon.com/pm/serv-s3/?trk=3cda67b9-5fb7-4d3f-84e8-40b544661f21&sc_channel=ps&ef_id=EAIaIQobChMIvq6ItaiwggMVmZKDBx0lRQkQEAAYASAAEgIbbfD_BwE:G:s&s_kwcid=AL!4422!3!645208988791!e!!g!!amazon%20s3%20block%20storage!19580264380!143903638463) storage as a data lake and loaded it in [Amazon Redshift](https://aws.amazon.com/redshift/) data warehouse using [airflow](https://airflow.apache.org/docs/apache-airflow/stable/index.html) to run the pipeline daily. Next, I applied some analytics to the data to prepare it for
feeding to a neural network model to predict car prices based on its main
features (brand, model, class, km, transmission, and fuel type), and then I created a RESTful API to deploy the model using Apache Flask. Lastly, I developed a web application using
Plotly Dash provides an interactive user interface for predicting car prices

## Data Source:

I used the [beatifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library to scrap the whole used car data on hatla2ee.com. Firstly, I scraped the car's data based on the fuel type as a search filter to avoid the need to load every single car page to get
the fuel data (this was the only information that was not available on the car's list page and needed to load each car page to get). Then, I scraped data based on the car body search filter, because when I used
both fule and body data as filters at the same time, I found that only 10% of the data were being scraped, which turned out to be caused by the fact that not all cars have the body type information available so they don't appear in the search filter.
I scraped the available cars with body type information and used it to develop a data set with the available body data for each model, which can be used to get the body type of cars of the same model with no body data.



## Technologies
The technologies I used in developing the pipeline are:

    Scrapin: beatifulSoup
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
All the analytics are found in detail in the notebook directory. I'll show the main charts here

### Brand popularity in the market
![image](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/007008c2-6da9-4989-b2e6-75eeb2c0bc87)

### Model popularity in the market 
![image](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/2b44697e-a21c-4d1b-9f74-6f4f68dd3f93)

### Most popular colors

![colors](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/42929434-5a52-458b-83d9-ceb2ba16e7d4)

### Average age of the car per brand
![image](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/2d5e70e2-db27-4bad-9758-43fab74a3662)

### Average Km of the car per Model (top 50)
![model km](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/23996c25-9479-4798-b01d-ff05da6172e6)

### Average Km per brand
![avg_km](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/a0ce8de5-d337-4b6b-9608-03625c828fea)

### Fuel, transmission, and body distributions 
![colle](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/5b182b83-18ea-4df8-a8d1-8b8cca43e4ae)

### Cars distribution per governorate
![gov](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/945e0e8b-9a4b-4281-af8b-639bfde7e01b)


### brands distribution per governorate
![govs](https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/a6063296-7d22-4019-874c-3914c9dc5148)



## Prediction model

I have built a neural network of three dense layers and trained the data on it. The accuracy of the model was around 92%. More details about building the model and data preparation are in the notebook directory. After training the model, I saved it as a pickle file along with
car data frame and trained scaler, to be used later by the prediction API and the web application

## Web application
This is the interface of the web application. The user selects the car properties and then clicks Predict to see the results, the application also shows statistics of car prices per popular brand and model.
here is a video demo showing the web app and how to use it: https://youtu.be/xCKlSArHJvQ

<img width="1440" alt="image" src="https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/51072c94-0224-47f9-98b7-6ee809655c16">

<img width="1440" alt="image" src="https://github.com/aya9aladdin/used-cars-price-prediction/assets/27581535/7cd411c5-e124-429e-a296-debfb284ddce">

