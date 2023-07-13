# mlops-zoomcamp-project

How to run MLFlow Server:
mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:flamengo@mlfl
ow-database.cuownlz1peeo.us-east-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-models-bruno

MLFlow UI will be available in: http://ec2-18-117-176-70.us-east-2.compute.amazonaws.com:5000