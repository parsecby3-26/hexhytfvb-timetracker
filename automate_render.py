# automate_render.py
import requests
import json
import sys

# User-provided Render API Key
API_KEY = "rnd_2wgw1mJ8CrzoCaMR2027rbrdjutc"
REPO_URL = "https://github.com/parsecby3-26/hexhytfvb-timetracker"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def trigger_blueprint():
    print(f"Triggering Render Blueprint for: {REPO_URL}")
    
    url = "https://api.render.com/v1/blueprint-batches"
    payload = {
        "repo": REPO_URL,
        "branch": "master"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code in [200, 201]:
            print("\n" + "="*50)
            print("✓ SUCCESS: Render Blueprint Batch Created!")
            print("✓ Render is now building your backend from the /backend folder.")
            print("="*50 + "\n")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"\n✗ ERROR: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"\n✗ EXCEPTION: {str(e)}")

if __name__ == "__main__":
    trigger_blueprint()
