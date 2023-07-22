# mlops-zoomcamp-project Bruno Caraffa

This application leverages data from over 3 million trips in Chicago's bike-sharing system to accurately predict trip durations. It achieves this by considering four essential attributes: the pickup station, dropoff station, user type (member or casual), and bike type (electric or classic).

The vast dataset provides a robust foundation for the predictive model, allowing for accurate estimations of trip durations based on the specific combination of attributes. By analyzing historical trip patterns, the application can deliver reliable predictions to enhance the overall user experience and optimize bike-sharing operations.

The utilization of both user type and bike type as attributes ensures that the predictions are tailored to different groups of users and the type of bikes they prefer, further enhancing the model's precision.

This application uses Docker and Flask for the AWS deployment, Prefect for training orchestration, and MLflow for model registry.

## How to train and deploy the model on aws:
* 1 Start mlflow for model and artifacts registry:

#### 1.1) mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:flamengo@mlflow-database.cuownlz1peeo.us-east-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-models-bruno

* 2 Start prefect for the orchestration deploy and then run the training orchestration using the deployment:

#### 2.1) prefect server start

#### 2.2) prefect deploy -n trip_prediction

#### 2.3) prefect deployment run 'main-flow/trip_prediction'

* 3 Build and run the docker image (aws access key id and secret id are neccessary) containing the prediction application:

#### 3.1) docker build -t mlopszoomcamp --build-arg AWS_ACCESS_KEY_ID={INSERT YOUR AWS ACCESS KEY ID HERE} --build-arg AWS_SECRET_ACCESS_KEY={INSERT YOUR AWS SECRET ACCESS KEY ID HERE} .

#### 3.2) docker run -it -p 9696:9696 mlopszoomcamp

* 4 Test the deployed app (to test the prediction running on aws, parameters can be edited on the hard coded ride dictionary on test_prediction.py):

#### 4.1) python test_prediction.py 
