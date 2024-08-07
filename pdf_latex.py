import subprocess
import os
from tempfile import TemporaryDirectory
from log import getLogger

logger = getLogger(__name__)

class PDFLatexConverter:
    def __init__(self, tex_file: str, tex_dir: str | None = None):
        self.tex_file = tex_file
        self.tex_dir = tex_dir

    def convert_to_pdf(self, output_dir: str | None = None):
        try:            
            # Run the pdflatex command
            with TemporaryDirectory() as td:
                subprocess.run(
                    ['pdflatex', f'-output-directory={td}', self.tex_file],
                    timeout=10,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self.tex_dir if self.tex_dir else None
                )
            
                # Move the generated PDF to the output directory if specified
                if output_dir:
                    pdf_file = self.tex_file.replace('.tex', '.pdf')
                    pdf_file = os.path.join(td, pdf_file)
                    if os.path.exists(pdf_file):
                        os.makedirs(output_dir, exist_ok=True)
                        output_path = os.path.join(output_dir, os.path.basename(pdf_file))
                        os.rename(pdf_file, output_path)
                        logger.debug(f"PDF moved to {output_path}")
                    else:
                        logger.warn("PDF file not found.")
                else:
                    logger.debug("PDF generated in the current directory.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error during conversion: {e.stderr.decode()}")
