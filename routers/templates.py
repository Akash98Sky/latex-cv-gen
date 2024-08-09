import json
import os
from typing import Any
from fastapi import APIRouter, Body, Depends, File, Form, HTTPException, Response, UploadFile
from tempfile import TemporaryDirectory

from helpers.data import sanitize_data
from helpers.pdf_latex import PDFLatexConverter
from services.db import DbSvc
from services.tex_parser import TexParser


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
    elif sample_data and sample_data.content_type not in ['application/json', 'application/x-json']:
        raise HTTPException(status_code=400, detail="Sample data must be a JSON file")
    
    data = None
    pdf = None
    if sample_data:
        data_bin = await sample_data.read()
        data = json.loads(data_bin.decode())
        sanitize_data(data)
        with TemporaryDirectory() as tmpdir:
            async with TexParser(files) as parsed:
                for template in parsed.templates():
                    filename = str(template)
                    tex_compiled = await parsed.render(template, data)
                    with open(os.path.join(tmpdir, filename), 'w') as f:
                        # write to output file
                        f.write(tex_compiled)
            
            latex_converter = PDFLatexConverter(entrypoint, tmpdir)
            latex_converter.convert_to_pdf(tmpdir)
            pdf_file = entrypoint.replace('.tex', '.pdf')

            with open(os.path.join(tmpdir, pdf_file), 'rb') as f:
                pdf = f.read()
    
    return await db.create_template(name, entrypoint, files, data, pdf)

@router.get("")
async def get_templates(db: DbSvc = Depends(DbSvc)):
    return await db.get_templates()

@router.get("/{template_id}")
async def get_template(template_id: str, db: DbSvc = Depends(DbSvc)):
    template = await db.get_template(template_id, populate_sample=True)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return template

@router.get("/{template_id}/sample")
async def sample_cv(template_id: str, db: DbSvc = Depends(DbSvc)):
    sample = await db.get_sample(template_id)

    if not sample or not sample.file:
        raise HTTPException(status_code=404, detail="Sample not found")
    
    return Response(
        content=sample.file.content.decode(),
        media_type='application/pdf',
        headers={'Content-Disposition': f'attachment; filename="{sample.file.name}"'},
        status_code=200
    )

@router.post("/{template_id}/generate")
async def generate_cv(template_id: str, data: dict[str, Any] = Body(), db: DbSvc = Depends(DbSvc)):
    template = await db.get_template(template_id, populate_content=True)

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    elif not template.files:
        raise HTTPException(status_code=400, detail="Template has no files")

    sanitize_data(data)
    with TemporaryDirectory() as tmpdir:
        async with TexParser(template.files) as parsed:
            for tex_template in parsed.templates():
                filename = str(tex_template)
                tex_compiled = await parsed.render(tex_template, data)
                with open(os.path.join(tmpdir, filename), 'w') as f:
                    # write to output file
                    f.write(tex_compiled)
            
        latex_converter = PDFLatexConverter(template.entrypoint, tmpdir)
        latex_converter.convert_to_pdf(tmpdir)

        pdf_file = template.entrypoint.replace('.tex', '.pdf')
        with open(os.path.join(tmpdir, pdf_file), 'rb') as f:
            pdf = f.read()
            return Response(content=pdf, media_type='application/pdf', headers={'Content-Disposition': f'attachment; filename="{pdf_file}"'}, status_code=200)