# automate_render_service.py
import requests
import json

API_KEY = "rnd_2wgw1mJ8CrzoCaMR2027rbrdjutc"
REPO_URL = "https://github.com/parsecby3-26/hexhytfvb-timetracker"
SERVICE_NAME = "hxf-timetracker-api"

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
        "ownerId": "owner-c8p0m6q68p6c738f6b0g", # This might need to be fetched, but I'll try without it first or use the one from previous triggers if available
        "repo": REPO_URL,
        "branch": "master",
        "rootDir": "backend",
        "runtime": "python",
        "envVars": [
            {"key": "DATABASE_URL", "value": "postgresql://postgres.kpotdnigexmoxrkwsowb:nvkBIluO0i0OMtHl@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres"},
            {"key": "JWT_SECRET_KEY", "value": "nngj5dg8zq13tu5a6a471p"},
            {"key": "JWT_ALGORITHM", "value": "HS256"},
            {"key": "ENVIRONMENT", "value": "production"},
            {"key": "SMTP_HOST", "value": "smtp.gmail.com"},
            {"key": "SMTP_PORT", "value": "587"},
            {"key": "SMTP_USER", "value": "hexhytfvb@gmail.com"},
            {"key": "SMTP_PASSWORD", "value": "tslwyfrciibuedrc"},
            {"key": "SMTP_FROM", "value": '"hexhytfvb TimeTracker <hexhytfvb@gmail.com>"'},
            {"key": "FRONTEND_URL", "value": "https://hxf-timetracker-app.vercel.app"},
            {"key": "CRON_SECRET", "value": "hexhytfvb_secure_960"}
        ],
        "serviceDetails": {
            "buildCommand": "pip install -r requirements.txt",
            "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port 10000",
            "plan": "free"
        }
    }
    
    print(f"Creating Render Service: {SERVICE_NAME}...")
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code in [200, 201]:
        print("✓ SUCCESS: Render Service created and linked to GitHub!")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"✗ ERROR: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    create_service()
