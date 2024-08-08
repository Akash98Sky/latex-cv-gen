import os
from typing import Any
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Response, UploadFile
from tempfile import TemporaryDirectory

from helpers.pdf_latex import PDFLatexConverter
from services.db import DbSvc
from services.parser import Parser


router = APIRouter(prefix="/templates", tags=["templates"])

@router.post("")
async def upload_template(
        files: list[UploadFile] = File(...),
        name: str = Form(...),
        entrypoint: str = Form('main.tex'),
        sample_data: UploadFile | None = File(None),
        db: DbSvc = Depends(DbSvc)
    ):
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="Template has no files")
    return await db.create_template(name, entrypoint, files, sample_data)

@router.get("")
async def get_templates(db: DbSvc = Depends(DbSvc)):
    return await db.get_templates()

@router.get("/{template_id}")
async def get_template(template_id: int, db: DbSvc = Depends(DbSvc)):
    template = await db.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template

@router.post("/{template_id}/generate")
async def generate_cv(template_id: int, data: dict[str, Any] = Body(), db: DbSvc = Depends(DbSvc)):
    template = await db.get_template(template_id, populate_content=True)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    elif not template.files:
        raise HTTPException(status_code=400, detail="Template has no files")

    parser = Parser()
    with TemporaryDirectory() as tmpdir:
        for templatefile in template.files:
            if templatefile.file is None:
                continue

            filename = templatefile.file.name
            tex_template = templatefile.file.content.decode_str()
            with open(os.path.join(tmpdir, filename), 'w') as f:
                # parse tex file
                parser.generate(tex_template)
                # render the template with profile data
                tex_compiled = str(parser.exec(data))
                # write to output file
                f.write(tex_compiled)
            
        latex_converter = PDFLatexConverter(template.entrypoint, tmpdir)
        latex_converter.convert_to_pdf(tmpdir)

        pdf_file = template.entrypoint.replace('.tex', '.pdf')
        with open(os.path.join(tmpdir, pdf_file), 'rb') as f:
            pdf = f.read()
            return Response(content=pdf, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="{pdf_file}"'}, status_code=200)