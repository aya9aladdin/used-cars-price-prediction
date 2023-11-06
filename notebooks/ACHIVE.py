


num_unique_models = car_df.groupBy('brand', 'model').count().count()
embedding_size = min(np.ceil((num_unique_models)/2), 50)

pd_df = car_df.select(concat_ws(' / ', car_df.brand, car_df.model)
              .alias("brand/model"), 'brand', 'model', 'transmission', 'price', 'km', 'age', 'class_score').toPandas()


#pd_df['km'] = np.log1p(pd_df['km'])  # Log-transform
car_price = np.log1p(pd_df['price'])  # Log-transform



label_encoder = LabelEncoder()
pd_df['brand/model'] = label_encoder.fit_transform(pd_df['brand/model'])


scaler = RobustScaler()

x_train, x_test, y_train, y_test = train_test_split(
pd_df[['brand/model', 'transmission', 'km', 'age', 'class_score']], car_price, test_size=0.2, random_state=0)

x_train['km'] = scaler.fit(x_train['km'].array.reshape(-1, 1)).transform(x_train['km'].array.reshape(-1, 1))
x_test['km'] = scaler.fit(x_test['km'].array.reshape(-1, 1)).transform(x_test['km'].array.reshape(-1, 1))


training_data = [x_train['brand/model'], x_train['transmission'], x_train['km'], x_train['age'], x_train['class_score']]

# Input layers
input_car_brand = Input(shape=(1,))
input_car_price = Input(shape=(1,))
input_car_tansmission = Input(shape=(1,))
input_car_km = Input(shape=(1,))
input_car_age = Input(shape=(1,))
input_car_class = Input(shape=(1,))


embedding_layer = Embedding(input_dim=num_unique_models, output_dim=embedding_size, name='embedding_models')(input_car_brand)
flatten_layer = Flatten()(embedding_layer)
concatenated = Concatenate()([flatten_layer, input_car_tansmission, input_car_km, input_car_age, input_car_class])
dense_layer = Dense(128, activation='relu')(concatenated)
dense_layer2 = Dense(64, activation='relu')(dense_layer)  # Adding a dense layer with 64 units
dense_layer3 = Dense(32, activation='relu')(dense_layer2)  # Adding another dense layer with 32 units
output_price4 = Dense(1, activation='linear')(dense_layer3)  # Price prediction output

model = Model(inputs=[input_car_brand, input_car_tansmission, input_car_km, input_car_age, input_car_class], outputs=output_price4)
model.compile(optimizer='adam', loss='mean_squared_error')
model.fit(training_data, y_train, epochs=30, batch_size=4)



columns_names= ['w_' + str(x) for x in range(50)]

pd_df = pd.concat([pd_df, pd.DataFrame(columns=columns_names)], axis=1)






embedding_weights = model.get_layer('embedding_models').get_weights()[0]
def update_weghts(row):
    row[columns_names] = embedding_weights[row['brand/model']]
    return row

pd_df = pd_df.apply(update_weghts, axis=1)




spark_data_frame = spark_df = spark.createDataFrame(pd_df)
spark_data_frame = spark_data_frame.drop('model/brand', 'km', 'age', 'transmission', 'class_score')
car_df = car_df.join(spark_data_frame, on=['brand', 'model', 'price'])
car_df.columns






model_df = car_df.drop('ad_date', 'color', 'fuel', 'city', 'class', 'body', 'governorate', 'class_new', 'brand_indexed',
                       'fuel_indexed', 'body_indexed', 'brand/model', 'km', 'price', 'model', 'brand', 'model_year')


features =  model_df.drop('price_Scaled').columns
model_df = model_df.drop('price')
udf1 = F.udf(lambda x : float(x[0]),DoubleType())
model_df = model_df.withColumn('price_Scaled',udf1('price_Scaled'))




from pyspark.ml.regression import LinearRegression
from pyspark.ml.evaluation import RegressionEvaluator

assembler = VectorAssembler(
    inputCols=features,
    outputCol="features")
data = assembler.transform(model_df)
final_data = data.select("features",  "price_Scaled")

train_data, test_data = final_data.randomSplit([0.8, 0.2], seed=42)
lr = LinearRegression(featuresCol="features", labelCol="price_Scaled", predictionCol="predicted_price")
lr_model = lr.fit(train_data)




columns_to_encode = [ "fuel", "body"]
indexer = [StringIndexer(inputCol=col, outputCol=f"{col}_indexed") for col in columns_to_encode]
encoder = [OneHotEncoder(inputCol=f"{col}_indexed", outputCol=f"{col}_onehot") for col in columns_to_encode]

pipeline = Pipeline(stages=indexer + encoder)

encoderModel = pipeline.fit(car_df)
encoderData = encoderModel.transform(car_df)
car_df = encoderData
car_df = car_df.drop('fuel_indexed', 'body_indexed')

for i in ["km", "price"]:
    # VectorAssembler Transformation - Converting column to vector type
    assembler = VectorAssembler(inputCols=[i],outputCol=i+"_Vect")

    # RobustScaler Transformation
    scaler = RobustScaler(inputCol=i+"_Vect", outputCol=i+"_Scaled")

    # Pipeline of VectorAssembler and MinMaxScaler
    pipeline = Pipeline(stages=[assembler, scaler])

    # Fitting pipeline on dataframe
    car_df = pipeline.fit(car_df).transform(car_df).drop(i+"_Vect")

