import os
import requests

# def test_blueprint_x_test(api_v1_host):
#     endpoint = os.path.join(api_v1_host, 'path_for_blueprint_x', 'test')
#     response = requests.get(endpoint)
#     assert response.status_code == 200
#     json = response.json()
#     assert 'msg' in json
#     assert json['msg'] == "I'm the test endpoint from blueprint_x."

#for users

token = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTY1NzQ3MDU4MCwianRpIjoiNjA2OThmODItZmIxMi00M2Y2LWJlNWEtZmMwOWFmZmVkY2Y5IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6eyJlbWFpbCI6ImFAdC5jb20iLCJwYXNzd29yZCI6ImZmIn0sIm5iZiI6MTY1NzQ3MDU4MH0.h_vs8NSR9RX9kCW1vomIYBbS719vwvI9ywDEe0wiwQw"

def test_get_users(api_v1_host):
    endpoint = "http://localhost:5000/api/v1/users"
    headers = {"Authorization": token}
    response = requests.get(endpoint, headers=headers)
    assert response.status_code == 200

def test_get_users_contains(api_v1_host):
    endpoint = "http://localhost:5000/api/v1/users?contains=j"
    headers = {"Authorization": token}
    response = requests.get(endpoint, headers=headers)
    assert response.status_code == 200

def test_get_users_pagesize_pageindex(api_v1_host):
    endpoint = "http://localhost:5000/api/v1/users?contains=j&page_size=2&page_index=1"
    headers = {"Authorization": token}
    response = requests.get(endpoint, headers=headers)
    assert response.status_code == 200

def test_post_users(api_v1_host):
    endpoint = "http://localhost:5000/api/v1/users"
    headers = {"Authorization": token}
    datas = {
        "name": "audrey",
        "email": "audrey@t.com",
        "password": "pwd",
        "confirm_password": "pwd"
    }
    response = requests.post(endpoint, headers=headers, data = datas)
    assert response.status_code == 200
    print(response)