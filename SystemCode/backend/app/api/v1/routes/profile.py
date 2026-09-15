from fastapi import APIRouter, HTTPException

from app.schemas.profile import UserProfile
from app.services.profile_service import profile_service

router = APIRouter()


@router.get("", response_model=UserProfile)
def get_profile() -> UserProfile:
    if profile_service.profile is None:
        raise HTTPException(status_code=404, detail="尚未上传简历或保存画像")
    return profile_service.profile


@router.put("", response_model=UserProfile)
def save_profile(profile: UserProfile) -> UserProfile:
    # 整体覆盖：前端提交修改后的完整画像 + 求职约束；不要求先上传过 PDF
    profile_service.profile = profile
    return profile
