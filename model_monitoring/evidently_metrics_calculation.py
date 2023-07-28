import datetime
import time
import random
import logging 
import pandas as pd
import psycopg
import joblib
import pickle
import mlflow
import warnings
warnings.filterwarnings("ignore")  

from prefect import task, flow

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s]: %(message)s")

SEND_TIMEOUT = 10
rand = random.Random()

create_table_statement = """
drop table if exists model_monitoring_metrics;
create table model_monitoring_metrics(
	timestamp timestamp,
	prediction_drift float,
	member_casual_drift float,
	rideable_type_drift float
)
"""

reference_data = pd.read_parquet('data/reference.parquet')
test_data = pd.read_parquet('data/current.parquet')

logged_model = 's3://mlflow-models-bruno/1/3728029fb076441facd4bcb24bd70228/artifacts/model'
model = mlflow.pyfunc.load_model(logged_model)

with open ('../models/preprocessor.b', 'rb') as file:
    dv = pickle.load(file)
    
categorical = ['rideable_type','member_casual','start_end_id']
    
train_dicts = reference_data[categorical].to_dict(orient='records')
X_train = dv.transform(train_dicts)
test_dicts = test_data[categorical].to_dict(orient='records')
X_test = dv.transform(test_dicts)

reference_data['duration_prediction'] = model.predict(X_train)
test_data['duration_prediction'] = model.predict(X_test)

begin = datetime.datetime(2023, 3, 1, 0, 0)

column_mapping = ColumnMapping(target = None, prediction='duration_prediction', numerical_features=None, categorical_features=categorical)

report = Report(metrics=[ColumnDriftMetric(column_name='duration_prediction'),ColumnDriftMetric(column_name='member_casual'),ColumnDriftMetric(column_name='rideable_type')])

def prep_db():
	with psycopg.connect("host=localhost port=5432 user=postgres password=example", autocommit=True) as conn:
		res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
		if len(res.fetchall()) == 0:
			conn.execute("create database test;")
			print('success creating db test')
		with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example") as conn:
			conn.execute(create_table_statement)

def calculate_metrics_postgresql(curr, i):
	current_data = test_data[(test_data.started_at >= (begin + datetime.timedelta(i))) &(test_data.started_at < (begin + datetime.timedelta(i + 1)))]

	report.run(reference_data = reference_data, current_data = current_data,column_mapping=column_mapping)

	result = report.as_dict()
	prediction_drift = result['metrics'][0]['result']['drift_score'] 
	member_casual_drift = result['metrics'][1]['result']['drift_score'] 
	rideable_type_drift = result['metrics'][2]['result']['drift_score']

	curr.execute(
		"insert into model_monitoring_metrics(timestamp, prediction_drift, member_casual_drift, rideable_type_drift) values (%s, %s, %s, %s)",
		(begin + datetime.timedelta(i), prediction_drift, member_casual_drift, rideable_type_drift)	)

def batch_monitoring_backfill():
	prep_db()
	last_send = datetime.datetime.now() - datetime.timedelta(seconds=10)
	with psycopg.connect("host=localhost port=5432 dbname=test user=postgres password=example", autocommit=True) as conn:
		for i in range(0, 30):
			with conn.cursor() as curr:
				calculate_metrics_postgresql(curr, i)

			new_send = datetime.datetime.now()
			seconds_elapsed = (new_send - last_send).total_seconds()
			if seconds_elapsed < SEND_TIMEOUT:
				time.sleep(SEND_TIMEOUT - seconds_elapsed)
			while last_send < new_send:
				last_send = last_send + datetime.timedelta(seconds=10)
			logging.info("data sent")

if __name__ == '__main__':
	batch_monitoring_backfill()



