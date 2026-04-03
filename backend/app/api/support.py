from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.schemas import FeedbackCreate, APIResponse
from app.services.email_service import email_service

router = APIRouter()

@router.post("/feedback", response_model=APIResponse)
async def submit_feedback(request: FeedbackCreate):
    """Submit support request or feedback."""
    success = await email_service.send_support_feedback_email(
        name=request.name,
        email=request.email,
        category=request.category,
        message=request.message
    )
    
    if not success:
        return APIResponse(
            status="error",
            statusCode=500,
            message="Failed to send feedback email. Please try again later.",
            data=None,
            errors=["Email delivery failure"]
        )
        
    return APIResponse(
        status="success",
        statusCode=200,
        message="Feedback submitted successfully. Thank you!",
        data=None,
        errors=[]
    )
