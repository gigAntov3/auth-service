from fastapi import APIRouter

from api.v1.routes import (
    auth_routes, 
    user_routes, 
    role_routes
)

router = APIRouter()

router.include_router(auth_routes.router)
router.include_router(user_routes.router)
router.include_router(role_routes.router)