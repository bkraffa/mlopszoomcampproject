#import s3fs
import pandas as pd
import mlflow
import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error
from prefect import flow, task
import pathlib
import pickle
import warnings

@task(retries = 3, retry_delay_seconds=2)
def read_data(path):
     df = pd.read_parquet(path)
     return df

@task
def pre_processing(df):
    df.dropna(inplace=True)
    df['start_end_id'] = df['start_station_id'] + '-' +df['end_station_id']
    df = df[(df.duration >= 1) & (df.duration <= 60)]
    columns = ['ride_id','started_at','ended_at','start_station_name','end_station_name','start_station_id','end_station_id',
               'start_lat','start_lng','end_lat','end_lng']
    df.drop(columns=columns, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

@task
def training_preparation(df):
    categorical = ['rideable_type','member_casual','start_end_id']

    X = df.drop(columns=['duration'])
    y = df.duration

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

    dv = DictVectorizer()

    train_dicts = X_train[categorical].to_dict(orient='records')
    X_train = dv.fit_transform(train_dicts)
    test_dicts = X_test[categorical ].to_dict(orient='records')
    X_test = dv.transform(test_dicts)

    pathlib.Path('models').mkdir(exist_ok=True)
    with open('models/preprocessor.b', "wb") as f_out:
            pickle.dump(dv,f_out)
    mlflow.log_artifact('models/preprocessor.b',artifact_path="dv_preprocessor")

    return X_train, X_test, y_train, y_test  

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

    TRACKING_SERVER_HOST = "ec2-18-217-76-61.us-east-2.compute.amazonaws.com" #change if ec2 instance is reinitiated
    mlflow.set_tracking_uri(f"http://{TRACKING_SERVER_HOST}:5000")
    mlflow.set_experiment("chicago-bike-share")

    with mlflow.start_run():
        df = read_data('s3://chicago-bike-trips/dataset.parquet')
        df = pre_processing(df)
        X_train, X_test, y_train, y_test  = training_preparation(df)
        model = train(X_train,y_train)
        mlflow.sklearn.log_model(model, artifact_path='model')
        rmse = calculate_mse(model,X_test,y_test)
        mlflow.log_metric("rmse", rmse)
    mlflow.end_run()

if __name__ == "__main__":
    main_flow()