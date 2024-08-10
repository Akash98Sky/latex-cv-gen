from typing import Any
from fastapi import UploadFile
from jinja2.environment import Environment
from jinja2.loaders import DictLoader, FileSystemLoader
from prisma.models import TemplateFile

class ParsedTemplate:
    def __init__(self, env: Environment):
        self.env = env

    def templates(self):
        return self.env.list_templates()

    async def render(self, file: str, data: dict[str, Any]) -> str:
        return await self.env.get_template(file).render_async(data)

class TexParser:
    def __init__(
        self,
        templates: list[TemplateFile] | list[UploadFile] | None = None,
        templates_dir: str | None = None
    ):
        self.templates = templates
        self.templates_dir = templates_dir
        assert self.templates or self.templates_dir, "Either templates or templates_dir must be provided"

    async def __aenter__(self):
        loader = FileSystemLoader(str(self.templates_dir))
        if self.templates:
            template_map = dict[str, str]()
            for template in self.templates:
                if isinstance(template, TemplateFile):
                    template_map[template.filename] = template.file.content.decode_str() if template.file else ''
                else:
                    template_bin = await template.read()
                    # reset the cursor to the beginning
                    await template.seek(0)
                    template_str = template_bin.decode()
                    template_map[str(template.filename)] = template_str
            loader = DictLoader(template_map)

        
        self.env = Environment(
            block_start_string= '${#',
            block_end_string= '#}',
            variable_start_string= '${',
            variable_end_string= '}',
            line_statement_prefix= '$#',
            comment_start_string= '\\iffalse',
            comment_end_string= '\\fi',
            trim_blocks=True,
            loader=loader,
            auto_reload=False,
            enable_async=True
        )
        return ParsedTemplate(self.env)

    async def __aexit__(self, exc_type, exc, tb):
        self.env = None