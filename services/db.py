from typing import Any
from fastapi import UploadFile
from prisma import Base64, Json, Prisma
from prisma.types import (
    TemplateCreateInput,
    TemplateCreateNestedWithoutRelationsInput,
    TemplateFileCreateInput,
    FileObjCreateNestedWithoutRelationsInput,
    FileObjCreateWithoutRelationsInput,
    FileObjCreateInput,
    SampleFileCreateInput,
    TemplateInclude
)
from logging import getLogger
import magic

logger = getLogger(__name__)
prisma = Prisma()

class DbSvc:
    def __init__(self):
        self.db = prisma

    async def create_file(self, file: UploadFile):
        file_buffer = await file.read()
        mime_type = magic.from_buffer(file_buffer, mime=True)
        return await self.db.fileobj.create(
            data=FileObjCreateInput(
                name=str(file.filename),
                content_type=mime_type,
                content=Base64.encode(file_buffer),
            )
        )
    
    async def get_file(self, file_id: str):
        return await self.db.fileobj.find_unique(
            where={
                'id': file_id
            }
        )

    async def create_template(self, name: str, entrypoint: str, files: list[UploadFile], sample_data: dict[str, Any] | None, sample_pdf: bytes | None):
        batch = self.db.batch_()

        batch.template.create(TemplateCreateInput(
            title=name,
            entrypoint=entrypoint,
        ))
        template_ref = TemplateCreateNestedWithoutRelationsInput(
            connect={ 'title': name }
        )

        for file in files:
            file_buffer = await file.read()
            mime_type = magic.from_buffer(file_buffer, mime=True)
            batch.templatefile.create(
                data=TemplateFileCreateInput(
                    template=template_ref,
                    filename=str(file.filename),
                    file=FileObjCreateNestedWithoutRelationsInput(
                        create=FileObjCreateWithoutRelationsInput(
                            name=str(file.filename),
                            content_type=mime_type,
                            content=Base64.encode(file_buffer),
                        )
                    )
                )
            )

        if sample_data and sample_pdf:
            batch.samplefile.create(
                data=SampleFileCreateInput(
                    template=template_ref,
                    data=Json(sample_data),
                    file=FileObjCreateNestedWithoutRelationsInput(
                        create=FileObjCreateWithoutRelationsInput(
                            name='sample.pdf',
                            content_type='application/pdf',
                            content=Base64.encode(sample_pdf),
                        )
                    )
                )
            )

        await batch.commit()

        return await self.db.template.find_unique(
            where={ 'title': name }
        )
    
    async def get_templates(self):
        return await self.db.template.find_many()
    
    async def get_template(self, template_id: str, populate_content: bool = False, populate_sample: bool = False):
        return await self.db.template.find_unique(
            where={
                'id': template_id
            },
            include=TemplateInclude(
                files={ 'include': { 'file': populate_content } },
                sample={ 'include': { 'file': populate_sample } },
            )
        )
    
    async def get_sample(self, template_id: str):
        return await self.db.samplefile.find_unique(
            where={ 'template_id': template_id },
            include={ 'file': True }
        )