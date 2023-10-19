
-- Populate staging cars body/model data table

INSERT INTO cars.staging.temp (brand, model, body)
select brand, model, body from cars.raw_schema.cars_body_data as o 
group by 1, 2, 3
having count(*) = (select count(*) from cars.raw_schema.cars_body_data as i  
                   group by model, brand, body 
                   having o.model = i.model
                  and o.brand = i.brand
                  order by 1 desc limit 1);
                  
                  
INSERT INTO cars.staging.cars_body_data (model, brand)
select model, brand from cars.raw_schema.cars_data
group by 1, 2;

UPDATE cars.staging.cars_body_data as u
SET body = (select body from cars.staging.temp t where (u.model, u.brand) = (t.model, t.brand) limit 1);
            
-- Populate staging cars classes data table

INSERT INTO cars.staging.cars_classes_data(model, brand, class)
SELECT distinct b.model, b.brand, replace(c.class, 'None', 'Basic') from cars.staging.cars_body_data as b, cars.raw_schema.cars_data as c 
WHERE (c.model, c.brand) = (b.model, b.brand);



-- Populate staging cars main data table

INSERT INTO cars.staging.cars_data (car_id, class_id, model_year, ad_date, transmission, price,
    fingerprint, km, color, fuel, city ) 
    SELECT distinct car_id, cl.class_id ,
    model_year ,
    ad_date ,
    transmission,
    case REGEXP_REPLACE(price, '([^0-9])','')
    when '' then '0' else REGEXP_REPLACE(price, '([^0-9])','') end::integer,
    fingerprint,
    case REGEXP_REPLACE(km, '([^0-9])','')
    when '' then '0' else REGEXP_REPLACE(km, '([^0-9])','')end::integer,
    color,
    fuel, 
    city 
    from cars.raw_schema.cars_data as main, cars.staging.cars_classes_data as cl
    WHERE (cl.class, cl.model, cl.brand) =(main.class, main.model, main.brand);


-- Populate production cars body/model data table
TRUNCATE cars.prod.cars_body_data;
INSERT INTO cars.prod.cars_body_data (brand, model,body)
SELECT distinct brand, model, body from cars.staging.cars_body_data;


-- Populate production cars classes data table
TRUNCATE cars.prod.cars_classes_data;
INSERT INTO cars.prod.cars_classes_data(model, brand, class)
select distinct model, brand, class from cars.staging.cars_classes_data as i where i.class !='';


-- Populate production cars main data table
TRUNCATE cars.prod.cars_data;
INSERT INTO cars.prod.cars_data (car_id, class_id, model_year, ad_date, transmission, price,
    fingerprint, km, color, fuel, city) 
    SELECT distinct car_id, class_id,
    model_year ,
    ad_date ,
    transmission,
    price,
    fingerprint,
    km,
    color,
    fuel, 
    city 
    from cars.staging.cars_data;


UPDATE cars.prod.cars_data as u
SET class_id = (select o.class_id from cars.prod.cars_classes_data as o join cars.staging.cars_classes_data as i 
on i.model = o.model and i.brand = o.brand and i.class = o.class
where i.class_id = u.class_id limit 1);