#!/usr/bin/env python

from typing import Any
from os import path, listdir
from services import DataScv
from txparser import Parser
from log import debug_on, debug_print
import argparse

# debug_on()

parser = argparse.ArgumentParser(description="Generate CV from tex file")

parser.add_argument("-p", "--profile", help="path to profile data file", default="profile-data.yaml")
parser.add_argument("-i", "--input", help="path to input file or directory", default="input")
parser.add_argument("-o", "--output", help="path to output file or directory", default="output")
args = parser.parse_args()

profile_data_path = args.profile
input_path = args.input
output_path = args.output
io_path_map: dict[str, str] = {}

if(path.isfile(input_path)):
  io_path_map[input_path] = output_path
else:
  for file in listdir(input_path):
    io_path_map[input_path + '/' + file] = output_path + '/' + file


yaml = DataScv(profile_data_path)

yaml.load_yaml()

for input_file_path, output_file_path in io_path_map.items():
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

      debug_print(output_file_path + ": file written!")
      
print("Done!")