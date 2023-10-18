DROP SCHEMA IF EXISTS raw_schema CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS prod CASCADE;

CREATE SCHEMA raw_schema;
CREATE SCHEMA staging;
CREATE SCHEMA prod;

CREATE TABLE cars.raw_schema.cars_data (
    indx INTEGER,
	car_id text unique,
    title text,
    model_year INTEGER,
    ad_date DATE,
    transmission BOOLEAN,
    price text,
    fingerprint text unique,
    fuel text,
    brand text,
    model text,
    color text,
    class text,
    km text,
    city text
);




CREATE TABLE cars.raw_schema.cars_body_data (
    id INTEGER,
    brand text,
    model text,
    body text

);

CREATE TABLE cars.staging.temp (
    brand text,
    model text,
    body text,
    primary key(brand, model)
);

CREATE TABLE cars.staging.cars_body_data (
    brand text,
    model text,
    body text,
    primary key(brand, model)
);

CREATE TABLE cars.staging.cars_classes_data (
    class_id INTEGER IDENTITY(0, 1) primary key,
    class text,
    brand text, 
    model text,
    foreign key(brand, model) references cars.staging.cars_body_data

);

CREATE TABLE cars.staging.cars_data (
	car_id text primary key,
    class_id INTEGER,
    model_year INT2,
    ad_date DATE,
    transmission BOOLEAN,
    price INTEGER,
    fingerprint text unique,
    km INTEGER,
    color text,
    fuel text,
    city text,
    foreign key(class_id) references cars.staging.cars_classes_data
);


CREATE TABLE cars.prod.cars_body_data (
    brand text,
    model text,
    body text,
    primary key(brand, model)
);

CREATE TABLE cars.prod.cars_classes_data (
    class_id INTEGER IDENTITY(0, 1) primary key,
    class text,
    brand text, 
    model text,
    foreign key(brand, model) references cars.staging.cars_body_data

);

CREATE TABLE cars.prod.cars_data (
	car_id text primary key,
    class_id INTEGER,
    model_year INT2,
    ad_date DATE,
    transmission BOOLEAN,
    price INTEGER,
    fingerprint text unique,
    km INTEGER,
    color text,
    fuel text,
    city text,
    foreign key(class_id) references cars.staging.cars_classes_data
);