#!/usr/bin/env python

from os import path, listdir
import argparse

from helpers.data import ProfileData
from helpers.pdf_latex import PDFLatexConverter
from helpers.log import getLogger, debug_on
from services.parser import Parser

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


if(path.isfile(input_path)):
  io_path_map[input_path] = output_path
else:
  for file in listdir(input_path):
    if file.endswith(".tex") or file.endswith(".cls"):
      io_path_map[input_path + '/' + file] = output_path + '/' + file


profile = ProfileData(profile_data_path)
profile.load_data()

for input_file_path, output_file_path in io_path_map.items():
  #load tex file
  with open(input_file_path, "r") as tex_file:
    tex = tex_file.read()
    logger.debug("tex file loaded")

    #parse tex file
    parser = Parser()
    parser.generate(tex)
    output = parser.exec(profile.get_data())

    #write to output file
    with open(output_file_path, "w") as output_file:
      output_file.write(str(output))

      logger.debug(output_file_path + ": file written!")
      
converter = PDFLatexConverter('main.tex', tex_dir=output_path)
converter.convert_to_pdf(output_path)

logger.info("Done!")