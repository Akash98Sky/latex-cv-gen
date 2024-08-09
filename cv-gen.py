#!/usr/bin/env python

import asyncio
from os import path, listdir
import argparse
from typing import Any

from helpers.data import ProfileData
from helpers.pdf_latex import PDFLatexConverter
from helpers.log import getLogger, debug_on
from services.tex_parser import TexParser

# debug_on()
logger = getLogger(__name__)

parser = argparse.ArgumentParser(description="Generate CV from tex file")

parser.add_argument("-p", "--profile", help="path to profile data file", default="profile-data.yaml")
parser.add_argument("-i", "--input", help="path to input file or directory", default="input")
parser.add_argument("-o", "--output", help="path to output file or directory", default="output")
args = parser.parse_args()

profile_data_path = args.profile
input_path: str = args.input
output_path: str = args.output
io_path_map: dict[str, str] = {}

if not path.isfile(profile_data_path):
  logger.error("Profile file not found!")
if not path.exists(input_path):
  logger.error("Input path not found!")
if not path.exists(output_path):
  logger.error("Output path not found!")


async def generate_cv(data: dict[str, Any]):
  async with TexParser(templates_dir=input_path) as parsed:
    for input_file in parsed.templates():
      #load tex file
      tex_output = await parsed.render(input_file, data)
      logger.debug("tex file loaded")

      #write to output file
      output_file_path = output_path + '/' + input_file
      with open(output_file_path, "w") as output_file:
        output_file.write(tex_output)

        logger.debug(output_file_path + ": file written!")
        
  converter = PDFLatexConverter('main.tex', tex_dir=output_path)
  converter.convert_to_pdf(output_path)


if __name__ == "__main__":
  profile = ProfileData(profile_data_path)
  profile.load_data()
  asyncio.run(generate_cv(profile.data))
  logger.info("Done!")