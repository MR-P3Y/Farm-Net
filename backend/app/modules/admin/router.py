from fastapi import APIRouter

from app.modules.admin.roles_router import router as roles_router
from app.modules.admin.users_router import router as users_router
from app.modules.admin.verifications_router import router as verifications_router


router = APIRouter(
    prefix="/admin",
)

router.include_router(users_router)
router.include_router(roles_router)
router.include_router(verifications_router)
