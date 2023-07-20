import requests

ride = {'start_station_id' : '515', 'end_station_id' : 'TA1305000032', 'rideable_type':'electric_bike','member_casual': 'member' }
url = 'http://localhost:9696/predict'
print(requests.post(url,json=ride).json())
