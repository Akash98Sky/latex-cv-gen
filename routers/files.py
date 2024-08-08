from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import ORJSONResponse, Response

from services.db import DbSvc


router = APIRouter(prefix="/files", tags=["files"])

@router.post("")
async def upload_file(file: UploadFile = File(...), db: DbSvc = Depends(DbSvc)):
    res = await db.create_file(file)
    return ORJSONResponse(
        content={
            "id": res.id,
            "name": res.name,
            "content_type": res.content_type
        },
        status_code=202
    )
    
@router.get("/{file_id}")
async def get_file(file_id: str, db: DbSvc = Depends(DbSvc)):
    file = await db.get_file(file_id)
    if not file:
        raise HTTPException(status_code=404, detail="File not found")
    return Response(content=file.content.decode(), media_type=file.content_type, status_code=200)