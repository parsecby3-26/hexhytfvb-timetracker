# automate_render_service.py
import requests
import json

API_KEY = "rnd_2wgw1mJ8CrzoCaMR2027rbrdjutc"
REPO_URL = "https://github.com/parsecby3-26/hexhytfvb-timetracker"
SERVICE_NAME = "hxf-timetracker-api"
OWNER_ID = "tea-d77n4aia214c73df5b6g"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def create_service():
    url = "https://api.render.com/v1/services"
    
    payload = {
        "type": "web_service",
        "name": SERVICE_NAME,
        "ownerId": OWNER_ID,
        "repo": REPO_URL,
        "branch": "master",
        "rootDir": "backend",
        "envVars": [
            {"key": "DATABASE_URL", "value": "postgresql://postgres.kpotdnigexmoxrkwsowb:nvkBIluO0i0OMtHl@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"},
            {"key": "JWT_SECRET_KEY", "value": "nngj5dg8zq13tu5a6a471p"},
            {"key": "JWT_ALGORITHM", "value": "HS256"},
            {"key": "ENVIRONMENT", "value": "production"},
            {"key": "SMTP_HOST", "value": "smtp.gmail.com"},
            {"key": "SMTP_PORT", "value": "587"},
            {"key": "SMTP_USER", "value": "hexhytfvb@gmail.com"},
            {"key": "SMTP_PASSWORD", "value": "tslwyfrciibuedrc"},
            {"key": "FRONTEND_URL", "value": "https://hxf-timetracker-app.vercel.app"},
            {"key": "PYTHON_VERSION", "value": "3.11.10"},
            {"key": "CRON_SECRET", "value": "hexhytfvb_secure_960"}
        ],
        "serviceDetails": {
            "runtime": "python",
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port 10000",
            "plan": "free"
        }
    }
    
    print(f"Creating Render Web Service: {SERVICE_NAME}...")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        print("✓ SUCCESS: Render Service created and linked to GitHub!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    create_service()
