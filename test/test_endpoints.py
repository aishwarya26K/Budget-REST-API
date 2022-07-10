import os
import requests

def test_blueprint_x_test(api_v1_host):
    endpoint = os.path.join(api_v1_host, 'path_for_blueprint_x', 'test')
    response = requests.get(endpoint)
    assert response.status_code == 200
    json = response.json()
    assert 'msg' in json
    assert json['msg'] == "I'm the test endpoint from blueprint_x."
