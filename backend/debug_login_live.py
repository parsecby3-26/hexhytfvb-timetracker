import sys
import os
# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

import dotenv
dotenv.load_dotenv()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import User, Role, UserRole
from app.core.security import verify_password, create_access_token
from app.api.auth import get_user_profile
from app.core.config import settings

# Setup database connection
print(f"Connecting to: {settings.DATABASE_URL.split('@')[-1]}")
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

db = SessionLocal()

try:
    # Simulate login logic
    email = "admin@tickmarks.com"
    password = "Admin@123"
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print("User not found")
        # Check if any user exists
        count = db.query(User).count()
        print(f"Total users in DB: {count}")
    elif not verify_password(password, user.password_hash):
        print("Password mismatch")
    else:
        print("Login logic start...")
        access_token = create_access_token(data={"sub": str(user.id)})
        print(f"Token created: {access_token[:20]}...")
        
        print("Building profile...")
        profile = get_user_profile(user, db)
        print(f"Profile built successfully: {profile}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()



