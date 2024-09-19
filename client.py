import requests

resp = requests.post(
    url="http://127.0.0.1:5000/authn",
    headers={
        "x-api-key": "123"
    },
    json={
        "play_token": "321"
    }
)

print(resp.url, resp.status_code, resp.json())
token = resp.json()["token"]
# token = resp.json()["token"]+"123132" # to test out server response to an invalid token

#####################################################################

resp2 = requests.post(
    url="http://127.0.0.1:5000/telemetry",
    headers={
        "x-api-key": "123",
        "Authorization": f"Bearer {token}"
    },
    json={
        "telemetry_data": "???"
    }
)

print(resp2.url, resp2.status_code, resp2.json())
