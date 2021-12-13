import requests
from django.conf import settings


def get_token():
    # POST 로 보낼 data 다
    access_data = settings.IAMPORT_ACCESS_DATA

    url = 'https://api.iamport.kr/users/getToken'

    # POST url 보낸다
    req = requests.post(url, data=access_data)
    access_req = req.json()

    # 만약 response 받은 값이 0이면 정보를 보낸다
    if access_req['code'] is 0:
        return access_req['response']['access_token']
    else:
        return None
