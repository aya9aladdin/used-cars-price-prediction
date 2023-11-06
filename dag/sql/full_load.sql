-- Populate staging cars body/model data table

-- Insert unique combinations of brand, model, and body into the staging temp table
INSERT INTO cars.staging.temp (brand, model, body)
with grouped_body_data as (SELECT brand, model, body, COUNT(*) as total
  FROM cars.raw_schema.cars_body_data 
  group by brand, model, body
        )
SELECT brand, model, body
FROM cars.raw_schema.cars_body_data AS o
GROUP BY 1, 2, 3
HAVING COUNT(*) = (
  SELECT total
  FROM grouped_body_data AS i
  WHERE o.model = i.model AND o.brand = i.brand
  ORDER BY 1 DESC
  LIMIT 1
);

-- Insert distinct brand and model combinations into the staging cars_body_data table
INSERT INTO cars.staging.cars_body_data (model, brand)
SELECT model, brand
FROM cars.raw_schema.cars_data
GROUP BY 1, 2;

-- Update the body information in the staging cars_body_data table
UPDATE cars.staging.cars_body_data AS u
SET body = (
  SELECT body
  FROM cars.staging.temp t
  WHERE (u.model, u.brand) = (t.model, t.brand)
  LIMIT 1
);

-- Populate staging cars classes data table


-- Insert distinct model, brand, and class combinations into the staging cars_classes_data table
INSERT INTO cars.staging.cars_classes_data (model, brand, class)
SELECT DISTINCT b.model, b.brand, c.class
FROM cars.staging.cars_body_data AS b, cars.raw_schema.cars_data AS c
WHERE (c.model, c.brand) = (b.model, b.brand);

-- Populate staging cars main data table


-- Insert data into the staging cars_data table, cleaning and converting values
INSERT INTO cars.staging.cars_data (car_id, model_year, ad_date, transmission, price, fingerprint, km, color, fuel, city)
SELECT DISTINCT car_id, model_year, ad_date, transmission, 
  CASE REGEXP_REPLACE(price, '([^0-9])', '')
    WHEN '' THEN '0'
    ELSE REGEXP_REPLACE(price, '([^0-9])', '')
  END::integer,
  fingerprint,
  CASE REGEXP_REPLACE(km, '([^0-9])', '')
    WHEN '' THEN '0'
    ELSE REGEXP_REPLACE(km, '([^0-9])', '')
  END::integer,
  color, fuel, city
FROM cars.raw_schema.cars_data;

-- Populate production cars body/model data table


-- Insert distinct brand, model, and body combinations into the production cars_body_data table
INSERT INTO cars.prod.cars_body_data (brand, model, body)
SELECT DISTINCT brand, model, body
FROM cars.staging.cars_body_data;

-- Populate production cars classes data table


-- Insert distinct model, brand, and class combinations into the production cars_classes_data table
INSERT INTO cars.prod.cars_classes_data (model, brand, class)
SELECT DISTINCT model, brand, class
FROM cars.staging.cars_classes_data;

-- Populate production cars main data table


-- Insert data into the production cars_data table
INSERT INTO cars.prod.cars_data (car_id, model_year, ad_date, transmission, price, fingerprint, km, color, fuel, city)
SELECT DISTINCT car_id, model_year, ad_date, transmission, price, fingerprint, km, color, fuel, city
FROM cars.staging.cars_data;

-- Update class_id in the production cars_data table based on staging data

UPDATE cars.prod.cars_data AS u
SET class_id = (
  SELECT o.class_id
  FROM cars.prod.cars_classes_data AS o
  JOIN cars.raw_schema.cars_data AS r
  ON (r.model = o.model AND r.brand = o.brand AND (r.class = o.class))
  WHERE r.car_id = u.car_id
  LIMIT 1
);