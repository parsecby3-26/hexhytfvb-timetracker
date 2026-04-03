import sys
import os
# Add the current directory to sys.path to import app
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, User, Role, UserRole
from app.core.security import hash_password, verify_password, create_access_token
from app.api.auth import get_user_profile
from datetime import datetime

# Setup in-memory database
engine = create_engine("sqlite:///:memory:")
SessionLocal = sessionmaker(bind=engine)
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Create seed data
    admin_role = Role(name="Admin")
    db.add(admin_role)
    db.commit()
    
    admin_user = User(
        name="Admin User",
        email="admin@tickmarks.com",
        password_hash=hash_password("Admin@123"),
        status=True,
        email_verified=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    user_role = UserRole(user_id=admin_user.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()
    
    print(f"User created: {admin_user}")
    print(f"User roles: {admin_user.roles}")
    
    # Simulate login logic
    email = "admin@tickmarks.com"
    password = "Admin@123"
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print("User not found")
    elif not verify_password(password, user.password_hash):
        print("Password mismatch")
    else:
        print("Login logic start...")
        access_token = create_access_token(data={"sub": str(user.id)})
        print(f"Token created: {access_token[:20]}...")
        profile = get_user_profile(user, db)
        print(f"Profile built: {profile}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
finally:
    db.close()



