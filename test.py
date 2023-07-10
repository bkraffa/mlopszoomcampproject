import s3fs
import pandas as pd

df = pd.read_parquet('s3://chicago-bike-trips/dataset.parquet')
print(df.shape)