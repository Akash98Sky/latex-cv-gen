#!/usr/bin/env python

from typing import Any
import sys
from services import DataScv
from txparser import Parser
from log import debug_on, debug_print
import argparse

# debug_on()

parser = argparse.ArgumentParser(description="Generate CV from tex file")

parser.add_argument("-p", "--profile", help="path to profile data file", default="profile-data.yaml")
parser.add_argument("-i", "--input", help="path to input file", default="input.tex")
parser.add_argument("-o", "--output", help="path to output file", default="output.tex")
args = parser.parse_args()

profile_data_path = args.profile
input_file_path = args.input
output_file_path = args.output

yaml = DataScv(profile_data_path)

yaml.load_yaml()

#load tex file
with open(input_file_path, "r") as tex_file:
  tex = tex_file.read()
  debug_print("tex file loaded")

  #parse tex file
  parser = Parser()
  parser.generate(tex)
  output = parser.exec(yaml.get_data())

  #write to output file
  with open(output_file_path, "w") as output_file:
    output_file.write(str(output))

    debug_print("tex file written")
    print("Done!")