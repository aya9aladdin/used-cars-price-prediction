-- Populate staging cars body/model data table
-- Clear the staging table before inserting data
TRUNCATE cars.staging.temp;

-- Insert unique combinations of brand, model, and body from raw data into the staging table
INSERT INTO cars.staging.temp (brand, model, body)
SELECT brand, model, body
FROM cars.raw_schema.cars_body_data AS o
GROUP BY 1, 2, 3
HAVING COUNT(*) = (
  SELECT COUNT(*)
  FROM cars.raw_schema.cars_body_data AS i
  WHERE o.model = i.model AND o.brand = i.brand
  ORDER BY 1 DESC
  LIMIT 1
);

-- Insert distinct brand and model combinations into the staging cars_body_data table
INSERT INTO cars.staging.cars_body_data (model, brand)
SELECT DISTINCT model, brand
FROM cars.raw_schema.cars_data
EXCEPT
SELECT DISTINCT model, brand
FROM cars.staging.cars_body_data;

-- Update body information in the staging cars_body_data table
UPDATE cars.staging.cars_body_data AS u
SET body = (
  SELECT body
  FROM cars.staging.temp t
  WHERE (u.model, u.brand) = (t.model, t.brand)
  LIMIT 1
)
WHERE body IS NULL;

-- Populate staging cars classes data table
INSERT INTO cars.staging.cars_classes_data (model, brand, class)
SELECT DISTINCT b.model, b.brand, REPLACE(c.class, 'None', 'Basic')
FROM cars.staging.cars_body_data AS b, cars.raw_schema.cars_data AS c
WHERE (c.model, c.brand) = (b.model, b.brand)
EXCEPT
SELECT DISTINCT model, brand, class
FROM cars.staging.cars_classes_data;

-- Populate staging cars main data table
-- Clear the staging table before inserting data
TRUNCATE cars.staging.cars_data;

-- Insert data into the staging cars_data table, mapping class_id to class data
INSERT INTO cars.staging.cars_data (car_id, model_year, ad_date, transmission, price, fingerprint, km, color, fuel, city)
SELECT car_id,
       model_year,
       ad_date,
       transmission,
       CASE REGEXP_REPLACE(price, '([^0-9])', '')
         WHEN '' THEN '0'
         ELSE REGEXP_REPLACE(price, '([^0-9])', '')
       END::integer,
       fingerprint,
       CASE REGEXP_REPLACE(km, '([^0-9])', '')
         WHEN '' THEN '0'
         ELSE REGEXP_REPLACE(km, '([^0-9])', '')
       END::integer,
       color,
       fuel,
       city
FROM cars.raw_schema.cars_data;

-- Populate production cars body/model data table
-- Insert unique combinations of brand, model, and body into the production table
INSERT INTO cars.prod.cars_body_data (brand, model, body)
SELECT DISTINCT brand, model, body
FROM cars.staging.cars_body_data
EXCEPT
SELECT DISTINCT brand, model, body
FROM cars.prod.cars_body_data;

-- Populate production cars classes data table
-- Clear the production table before inserting data
TRUNCATE cars.prod.cars_classes_data;

-- Insert distinct model, brand, and class combinations into the production table
INSERT INTO cars.prod.cars_classes_data (model, brand, class)
SELECT DISTINCT model, brand, class
FROM cars.staging.cars_classes_data AS i
WHERE i.class != '';

-- Perform an UPDATE for existing cars data
-- Update production data with staging data where fingerprint is different
UPDATE cars.prod.cars_data AS prod
SET
  fingerprint = stg.fingerprint,
  price = stg.price,
  ad_date = stg.ad_date
FROM cars.staging.cars_data AS stg
WHERE prod.car_id = stg.car_id AND prod.fingerprint != stg.fingerprint;

-- Add new cars data
-- Insert distinct car data from staging into production
INSERT INTO cars.prod.cars_data (car_id, model_year, ad_date, transmission, price, fingerprint, km, color, fuel, city)
SELECT DISTINCT car_id, model_year, ad_date, transmission, price, fingerprint, km, color, fuel, city
FROM cars.staging.cars_data
EXCEPT
SELECT DISTINCT car_id, model_year, ad_date, transmission, price, fingerprint, km, color, fuel, city
FROM cars.prod.cars_data;

-- Update class_id in the production cars_data table based on staging data
UPDATE cars.prod.cars_data AS u
SET class_id = (
  SELECT o.class_id
  FROM cars.prod.cars_classes_data AS o
  JOIN cars.raw_schema.cars_data AS r
  ON r.model = o.model AND r.brand = o.brand AND r.class = o.class
  WHERE r.car_id = u.car_id
  LIMIT 1
);
