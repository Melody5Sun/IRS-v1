from io import BytesIO

from fastapi import APIRouter, File, HTTPException, UploadFile
from pdfminer.high_level import extract_text

from app.schemas.resume import ResumeDocument
from app.services.profile_service import profile_service
from app.services.resume_service import ResumeService

router = APIRouter()
resume_service = ResumeService()


@router.post("/parse-pdf", response_model=ResumeDocument)
def parse_resume_pdf(file: UploadFile = File(...)) -> ResumeDocument:
    if file.content_type not in ("application/pdf", "application/octet-stream") and not (
        file.filename or ""
    ).lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="只支持上传 PDF 文件")

    text = extract_text(BytesIO(file.file.read())).strip()
    if not text:
        raise HTTPException(
            status_code=422, detail="无法从 PDF 中提取文本，可能是扫描件图片版 PDF"
        )

    parsed = resume_service.parse_text(text)
    # 解析结果先存入画像（about 合并进 notes），用户之后通过 GET /profile 读取并修改
    profile_service.save_resume(parsed)
    # response_model 是 ResumeDocument，响应里不带 about
    return parsed
