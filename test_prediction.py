import requests

ride = {'start_station_id' : '515', 'end_station_id' : 'TA1305000032', 'rideable_type':'electric_bike','member_casual': 'member' }
url = 'http://ec2-18-217-76-61.us-east-2.compute.amazonaws.com:9696/predict' #change if ex2 changes
print(requests.post(url,json=ride).json())
