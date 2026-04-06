import http.client
import json

def handler(request):
    # Target backend URL
    backend_host = "hexhytfvb-timetracker.onrender.com"
    backend_path = "/api/ping"
    
    print(f"Pinging backend: {backend_host}{backend_path}")
    
    try:
        conn = http.client.HTTPSConnection(backend_host)
        conn.request("GET", backend_path)
        response = conn.getresponse()
        data = response.read().decode()
        
        print(f"Status: {response.status}")
        print(f"Response: {data}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "status": "success",
                "message": "Backend pinged successfully",
                "backend_response": json.loads(data)
            })
        }
    except Exception as e:
        print(f"Error pinging backend: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "status": "error",
                "message": str(e)
            })
        }
