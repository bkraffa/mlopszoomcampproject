# mlops-zoomcamp-project

## How to deploy the model:
* mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:flamengo@mlflow-database.cuownlz1peeo.us-east-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-models-bruno

MLFlow UI will be available in: http://ec2-18-117-176-70.us-east-2.compute.amazonaws.com:5000 (change if ec2 server is reinitiated)


* prefect server start