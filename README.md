# mlops-zoomcamp-project

## How to deploy the model:
* mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:flamengo@mlflow-database.cuownlz1peeo.us-east-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-models-bruno

MLFlow UI will be available in: ec2-3-19-77-42.us-east-2.compute.amazonaws.com:5000 (change if ec2 server is reinitiated)


* prefect server start
prefect worker start -p mlopszoomcamp_pool -t process

prefect deploy -n trip_prediction

prefect deployment run 'main-flow/trip_prediction'

