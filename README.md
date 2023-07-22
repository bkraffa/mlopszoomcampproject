# mlops-zoomcamp-project

## How to deploy the model:
* mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:flamengo@mlflow-database.cuownlz1peeo.us-east-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-models-bruno

* prefect orchestration and deployment:

prefect server start

prefect deploy -n trip_prediction

prefect deployment run 'main-flow/trip_prediction'

* docker image:

docker build -t mlopszoomcamp .

docker run mlopszoomcamp
