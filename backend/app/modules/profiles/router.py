from fastapi import APIRouter

from app.modules.profiles.documents_router import router as documents_router
from app.modules.profiles.profile_router import router as profile_router


router = APIRouter()

router.include_router(profile_router)
router.include_router(documents_router)
