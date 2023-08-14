import warnings
import pathlib
import pickle
import pandas as pd
import mlflow
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from prefect import flow, task



@task(retries = 3, retry_delay_seconds=2)
def read_data(path):
    df = pd.read_parquet(path)
    return df

@task
def pre_processing(df):
    df.dropna(inplace=True)
    df.started_at = df.started_at.astype('datetime64[ns]')
    df.ended_at = df.ended_at.astype('datetime64[ns]')
    df['start_end_id'] = df['start_station_id'] + '-' +df['end_station_id']
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    columns = ['start_station_name','end_station_name','start_station_id','end_station_id',
               'start_lat','start_lng','end_lat','end_lng']
    df.drop(columns=columns, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

@task
def training_preparation(df):
    categorical = ['rideable_type','member_casual','start_end_id']
    train_data = df.loc[df['started_at'] < '2023-03-01 00:00:00' ]
    test_data = df.loc[df['started_at'] > '2023-03-01 00:00:00' ]
    dict_vectorizer = DictVectorizer()
    train_dicts = train_data[categorical].to_dict(orient='records')
    x_train = dict_vectorizer.fit_transform(train_dicts)
    test_dicts = test_data[categorical].to_dict(orient='records')
    x_test = dict_vectorizer.transform(test_dicts)
    pathlib.Path('models').mkdir(exist_ok=True)
    with open('models/preprocessor.b', "wb") as f_out:
        pickle.dump(dict_vectorizer,f_out)
    mlflow.log_artifact('models/preprocessor.b',artifact_path="dv_preprocessor")
    return x_train, train_data, x_test, test_data

@task()
def train(X_train,y_train):
    print('beginning training ...')
    lr = Ridge(alpha=.5)
    lr.fit(X_train, y_train)
    return lr

@task
def calculate_mse(model,X_test,y_test):
    y_pred = model.predict(X_test)
    rmse = mean_squared_error(y_test, y_pred, squared=False)
    return rmse

@flow
def main_flow():
    warnings.filterwarnings("ignore")
    TRACKING_SERVER_HOST = "ec2-18-117-234-13.us-east-2.compute.amazonaws.com" #change if ec2 instance is reinitiated
    mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
    mlflow.set_experiment("chicago-bike-share")

    with mlflow.start_run():
        df = read_data('s3://chicago-bike-trips/dataset.parquet')
        df = pre_processing(df)
        X_train, train_data, X_test, test_data  = training_preparation(df)
        pathlib.Path('model_monitoring/data').mkdir(exist_ok=True)
        train_data.to_parquet('model_monitoring/data/reference.parquet')
        test_data.to_parquet('model_monitoring/data/current.parquet')
        model = train(X_train,train_data['duration'])
        mlflow.sklearn.log_model(model, artifact_path='model')
        train_rmse = calculate_mse(model,X_train,train_data['duration'])
        mlflow.log_metric("train_rmse", train_rmse)
        test_rmse = calculate_mse(model,X_test,test_data['duration'])
        mlflow.log_metric("test_rmse", test_rmse)
    mlflow.end_run()

if __name__ == "__main__":
    main_flow()