# fetch_owner.py
import requests
import json

API_KEY = "rnd_2wgw1mJ8CrzoCaMR2027rbrdjutc"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Accept": "application/json"
}

def get_owners():
    r = requests.get('https://api.render.com/v1/owners', headers=headers)
    if r.status_code == 200:
        print(json.dumps(r.json(), indent=2))
    else:
        print(f"Error: {r.status_code}")
        print(r.text)

if __name__ == "__main__":
    get_owners()
