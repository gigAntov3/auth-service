from fastapi import APIRouter

from .get_current_user import router as get_current_user_router
from .update_current_user import router as update_current_user_router


router = APIRouter(prefix="/users", tags=["Users"])

router.include_router(get_current_user_router)
router.include_router(update_current_user_router)