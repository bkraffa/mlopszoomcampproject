import requests

def test_prediction():
    ride = {'start_station_id' : '515',
             'end_station_id' : 'TA1305000032',
             'rideable_type':'electric_bike',
             'member_casual': 'member' }
    
    url = 'http://ec2-18-117-234-13.us-east-2.compute.amazonaws.com:9696/predict'

    actual_response =  requests.post(url,json=ride).json()
    
    expected_response = {'duration': 18.810750678863172}

    assert actual_response == expected_response