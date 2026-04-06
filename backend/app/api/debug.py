from fastapi import APIRouter, HTTPException
import aiosmtplib
from app.core.config import settings
import socket
import asyncio

router = APIRouter()

@router.get("/smtp-check")
async def check_smtp():
    """Diagnostic endpoint to test outbound SMTP connectivity."""
    results = []
    
    # Combinations to test
    targets = [
        {"host": "smtp.gmail.com", "port": 465, "use_tls": True, "start_tls": False},
        {"host": "smtp.gmail.com", "port": 587, "use_tls": False, "start_tls": True},
        {"host": "smtp.googlemail.com", "port": 465, "use_tls": True, "start_tls": False},
        {"host": "smtp.googlemail.com", "port": 587, "use_tls": False, "start_tls": True},
        {"host": "smtp.gmail.com", "port": 25, "use_tls": False, "start_tls": False}, # Port 25 is often blocked but worth checking
    ]
    
    for target in targets:
        host = target["host"]
        port = target["port"]
        use_tls = target["use_tls"]
        start_tls = target["start_tls"]
        
        result = {
            "target": f"{host}:{port}",
            "strategy": "SSL/TLS" if use_tls else ("STARTTLS" if start_tls else "Plain"),
            "status": "Testing...",
            "error": None
        }
        
        try:
            # 1. First test raw TCP connection to see if the port is even open
            print(f"DEBUG: Testing TCP connection to {host}:{port}")
            try:
                # Using lower level socket to check connectivity
                sock = socket.create_connection((host, port), timeout=5)
                sock.close()
                result["tcp_open"] = True
            except Exception as e:
                result["tcp_open"] = False
                result["status"] = "TCP Connection Failed"
                result["error"] = str(e)
                results.append(result)
                continue

            # 2. Test SMTP Handshake
            smtp = aiosmtplib.SMTP(
                hostname=host,
                port=port,
                use_tls=use_tls,
                timeout=10
            )
            
            await smtp.connect()
            if start_tls:
                await smtp.starttls()
            
            result["status"] = "Successfully Connected & Handshaked"
            await smtp.quit()
        except Exception as e:
            result["status"] = "SMTP Handshake Failed"
            result["error"] = f"{type(e).__name__}: {str(e)}"
        
        results.append(result)
    
    return {
        "smtp_user": settings.SMTP_USER,
        "smtp_from": settings.SMTP_FROM,
        "results": results
    }
