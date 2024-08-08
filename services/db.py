from fastapi import UploadFile
from prisma import Base64, Prisma
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
    
    async def get_file(self, file_id: int):
        return await self.db.fileobj.find_unique(
            where={
                'id': file_id
            }
        )

    async def create_template(self, name: str, entrypoint: str, files: list[UploadFile], sample_data: UploadFile | None):
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
                    file=FileObjCreateNestedWithoutRelationsInput(
                        create=FileObjCreateWithoutRelationsInput(
                            name=str(file.filename),
                            content_type=mime_type,
                            content=Base64.encode(file_buffer),
                        )
                    )
                )
            )

        if sample_data:
            file_buffer = await sample_data.read()
            mime_type = magic.from_buffer(file_buffer, mime=True)
            batch.samplefile.create(
                data=SampleFileCreateInput(
                    template=template_ref,
                    file=FileObjCreateNestedWithoutRelationsInput(
                        create=FileObjCreateWithoutRelationsInput(
                            name=str(sample_data.filename),
                            content_type=mime_type,
                            content=Base64.encode(file_buffer),
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
    
    async def get_template(self, template_id: int, populate_content: bool = False):
        return await self.db.template.find_unique(
            where={
                'id': template_id
            },
            include=TemplateInclude(
                files={ 'include': { 'file': populate_content } },
                sample={ 'include': { 'file': populate_content } },
            )
        )