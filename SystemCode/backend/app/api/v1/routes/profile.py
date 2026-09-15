from fastapi import APIRouter, HTTPException

from app.schemas.profile import UserProfile
from app.services.profile_service import find_empty_fields, profile_service

router = APIRouter()


@router.get("", response_model=UserProfile)
def get_profile() -> UserProfile:
    if profile_service.profile is None:
        raise HTTPException(status_code=404, detail="尚未上传简历或保存画像")
    return profile_service.profile


@router.put("", response_model=UserProfile)
def save_profile(profile: UserProfile) -> UserProfile:
    # 整体覆盖：前端提交修改后的完整画像 + 求职约束；不要求先上传过 PDF。
    # parse-pdf 自动存入的画像可以不完整，用户手动提交时除选填字段外都必须填写
    empty_fields = find_empty_fields(profile.model_dump())
    if empty_fields:
        # 错误格式与 FastAPI 自带的 422 一致，前端用同一套逻辑定位出错字段
        raise HTTPException(
            status_code=422,
            detail=[{"loc": ["body", *loc], "msg": "不能为空", "type": "empty"} for loc in empty_fields],
        )
    profile_service.profile = profile
    return profile
