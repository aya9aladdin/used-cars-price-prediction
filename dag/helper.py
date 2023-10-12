from airflow.hooks.S3_hook import S3Hook
import pandas as pd
import requests
from datetime import datetime, timedelta
from bs4 import BeautifulSoup, SoupStrainer 
import itertools
import re
from pathlib import Path
import os

def get_page(session, html) -> BeautifulSoup:
    request = session.get(html)
    cars = SoupStrainer(id="listCar-container")
    return BeautifulSoup(request.text, 'html.parser', parse_only=cars)


def scrap_cars_data()  -> Path:
    session = requests.Session()

    body_types = ['sedan', 'hatchback', 'coupe', '4X4', 'mini Vans', 'SUV']
    fuel_types = ['gas', 'diesel', 'natural gas', 'electric', 'hybrid']
    properties = ['brand', 'model', 'color', 'class', 'km', 'city']

    cars_corpus = {}
    z = 0
    # itertools.product(body_types, fuel_types)
    car_index = 0
    for index, fuel in enumerate(fuel_types):
        
        #body = body_types.index(filter[0]) + 1
        print(fuel)
        html = f"https://eg.hatla2ee.com/en/car/search?fuel={index+1}&page="
        soup = get_page(session, html)
        paging = soup.find(attrs={"class": "pagination pagination-right"})

        try:
            pages_no = int(str(paging.find_all('li')[-2].string))
        except:
            pages_no = 1
    
        print(pages_no, " page numbers")

        for page in range(1, pages_no+1):
            print(page)
            html = f"https://eg.hatla2ee.com/en/car/search?fuel={index+1}&page={page}"
            soup = get_page(session, html)

            car_list = soup.find_all(attrs={"class": "newCarListUnit_data_wrap"})

            for i, child in enumerate(car_list):
                
                header = child.find('div', attrs={"class":"newCarListUnit_header"})
                title = str(header.find('a').string)
                
                year = re.search(r"(\d+)$", title)
    
                try:
                    year = year.group(1)
                except:
                    year = ""

                #get car id
                car_link = str(header.find('a').get('href'))
                id = re.search(r"/(\d+)$", car_link).group(1)

                #properties of the car
                metatags = header.findNextSibling()
                prop = []
                
                for p in metatags:
                    if p != '\n':
                        prop.append(str(p.string).strip())
                if len(prop)< 6:
                    prop.insert(3, None)
                
                other_data = child.find(attrs={"class":"otherData_Date"})
                date = str(other_data.find('span').string).strip()
                car_options = other_data.findNextSibling()
                try:
                    icon = str(car_options.find(attrs={"class":"tooltipDef"}).attrs["title"])
                    
                    automatic = 1 if icon == 'Automatic' else 0
                    
                except:
                    automatic = 0
                    
                price = str(child.find(attrs={"class":"main_price"}).find("a").string).strip().split()[0]

                keys = ['id', 'title', 'year', 'ad_date', 'transmission', 'price', 'fingerprint', 
                    'fuel',]+ properties
            
                values = [id, title, year, date, automatic, price, id + '-' + price, fuel,] + prop
                car_info = dict(zip(keys, values))

                cars_corpus[car_index] = car_info
                car_index += 1

    df = pd.DataFrame.from_dict(cars_corpus, orient='index')

    date = datetime.now()
    year = date.strftime("%Y")
    month = date.strftime("%m")
    day = date.strftime("%d")

    path = Path(f"./cars_raw_data/{year}/{month}")
    if not os.path.exists(path):
        os.makedirs(path)
        
    path = f'./cars_raw_data/{year}/{month}/{day}.csv'
    df.to_csv(path)
    return path[2:]



def local_to_s3(bucket_name:str, **kwargs) -> None:
    path = kwargs['ti'].xcom_pull(task_ids=['scrap'])[0]
    key = path
    hook = S3Hook('s3-bucket')
    hook.load_file(filename = path, key=key, bucket_name=bucket_name)
    return


