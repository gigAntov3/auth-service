from fastapi import APIRouter

from .login import router as login_router
from .logout import router as logout_router
from .register import router as register_router
from .refresh import router as refresh_router
# from .verification import router as verification_router
# from .verify import router as verify_router


router = APIRouter(prefix="/auth", tags=["Auth"])

router.include_router(login_router)
router.include_router(logout_router)
router.include_router(register_router)
router.include_router(refresh_router)
# router.include_router(verification_router)
# router.include_router(verify_router)