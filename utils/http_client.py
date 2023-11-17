import requests


def fetch(endpoint, method, data):
    # データをJSON形式でPOSTリクエストとして送信
    if method == "GET":
        response = requests.get(endpoint)
    elif method == "POST":
        response = requests.post(endpoint, json=data)
    else:
        response = None
    return response
