from fastapi import Depends, HTTPException, status
from app.models.persistence import User
from app.api_server import get_current_user

def role_required(allowed_roles: list):
    def decorator(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return decorator

# Example usage:
# @app.post("/admin/reboot")
# def reboot_system(user: User = Depends(role_required(["admin"]))):
#     return {"status": "rebooting"}
