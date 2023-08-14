# mlops-zoomcamp-project Bruno Caraffa

This application leverages data from over 5 million trips in Chicago's bike-sharing system to accurately predict trip durations. It achieves this by considering four essential attributes: the pickup station, dropoff station, user type (member or casual), and bike type (electric or classic).

The vast dataset provides a robust foundation for the predictive model, allowing for accurate estimations of trip durations based on the specific combination of attributes. By analyzing historical trip patterns, the application can deliver reliable predictions to enhance the overall user experience and optimize bike-sharing operations.

The utilization of both user type and bike type as attributes ensures that the predictions are tailored to different groups of users and the type of bikes they prefer, further enhancing the model's precision.

This application uses Docker and Flask for the AWS deployment, Prefect for training orchestration, MLflow for model registry and Grafana/Evidently for model monitoring.

## How to train and deploy the model on aws:
0) Start the pipenv environment:
*  pipenv shell

1) Start mlflow for model and artifacts registry:

* 1.1) mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:flamengo@mlflow-database.cuownlz1peeo.us-east-2.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://mlflow-models-bruno

-MLFlow UI is running on: http://ec2-18-117-234-13.us-east-2.compute.amazonaws.com:5000

2) Start prefect for the orchestration deploy and then run the training orchestration using the deployment:

* 2.1) prefect server start

* 2.2) prefect deploy -n trip_prediction

* 2.3) prefect deployment run 'main-flow/trip_prediction'

* 2.4) python orchestrate.py

-Prefect UI will be running on: http://localhost:4200

3) Build and run the docker image (aws access key id and secret id are neccessary) containing the prediction application:

* 3.1) docker build -t mlopszoomcamp --build-arg AWS_ACCESS_KEY_ID={INSERT YOUR AWS ACCESS KEY ID HERE} --build-arg AWS_SECRET_ACCESS_KEY={INSERT YOUR AWS SECRET ACCESS KEY ID HERE} .

* 3.2) docker run -it -p 9696:9696 mlopszoomcamp

4) Test the deployed app (to test the prediction running on aws, parameters can be edited on the hard coded ride dictionary on test_prediction.py):

* 4.1) python test_prediction.py

5) Build the image for the model monitoring application and run the monitoring for the test data (march 2023):

* 5.1) cd model_monitoring

* 5.2) docker-compose up --build

* 5.3) python evidently_metrics_calculation.py

* 5.4) access http://ec2-18-117-234-13.us-east-2.compute.amazonaws.com:3000, login to grafana using admin/admin as credentials and build your dashboard using PostgreSQL table model_monitoring_metrics

--Grafana runs on: http://ec2-18-117-234-13.us-east-2.compute.amazonaws.com:3000
--Adminer runs on: http://ec2-18-117-234-13.us-east-2.compute.amazonaws.com:8080

MLFlow UI:
![alt text](https://i.ibb.co/rkRytYy/mlops2.png)

Prefect UI:
![alt text](https://i.ibb.co/FhRdNN5/mlops3.png)

Docker Containers:
![alt text](https://i.ibb.co/bH7q03C/mlops4.png)

Model deployed on the AWS:
![alt text](https://i.ibb.co/fSz1dWZ/mlops5.png)

Adminer Database:
![alt text](https://i.ibb.co/mvhjS37/mlops7.pngg)

Model monitoring dashboard on Grafana:
![alt text](https://i.ibb.co/6s4ZtZX/mlops6.png)

Pylint grade:
![alt text](https://i.ibb.co/WvdvbDd/mlops1.png)

Unit test:
![alt text](https://i.ibb.co/sFwtd14/mlops8.png)

Pre-commit hooks:
![alt text](https://i.ibb.co/xzg54PM/mlops9.png)
